"""Blast-radius calculation for compromised infrastructure resources."""

from __future__ import annotations

from collections import deque

from agentshield.core.attack_path.graph import ResourceGraph


class BlastRadiusCalculator:
    """Calculate infrastructure impact if a resource is compromised."""

    def __init__(self, graph: ResourceGraph) -> None:
        self.graph = graph

    def get_reachable_resources(
        self,
        resource_id: str,
        max_depth: int | None = None,
    ) -> set[str]:
        """Return resources affected through dependent relationships.

        If resource A is depended upon by B, C, and D, compromising A can
        potentially affect B, C, and D.
        """

        if resource_id not in self.graph:
            return set()

        reachable: set[str] = set()

        queue: deque[tuple[str, int]] = deque(
            [(resource_id, 0)]
        )

        while queue:
            current, depth = queue.popleft()

            if max_depth is not None and depth >= max_depth:
                continue

            for dependent in self.graph.get_dependents(current):
                if dependent in reachable or dependent == resource_id:
                    continue

                reachable.add(dependent)
                queue.append(
                    (dependent, depth + 1)
                )

        return reachable

    def calculate_blast_radius(
        self,
        resource_id: str,
    ) -> int:
        """Return the number of additional resources potentially affected."""

        return len(
            self.get_reachable_resources(resource_id)
        )

    def calculate_impact_score(
        self,
        resource_id: str,
    ) -> float:
        """Return a normalized 0-1 blast-radius score."""

        total_resources = len(self.graph)

        if total_resources <= 1:
            return 0.0

        affected_resources = self.calculate_blast_radius(
            resource_id
        )

        score = affected_resources / (total_resources - 1)

        return round(
            min(score, 1.0),
            4,
        )