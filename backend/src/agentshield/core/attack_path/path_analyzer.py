"""Attack-path analysis for infrastructure resource graphs."""

from __future__ import annotations

from collections import deque

from agentshield.core.attack_path.graph import ResourceGraph


class AttackPathAnalyzer:
    """Find possible attacker routes through an infrastructure graph."""

    def __init__(self, graph: ResourceGraph) -> None:
        self.graph = graph

    def find_entry_points(self) -> list[str]:
        """Return resources that can serve as internet-facing entry points."""

        return sorted(
            resource_id
            for resource_id in self.graph.resources
            if self.graph.is_internet_exposed(resource_id)
        )

    def find_attack_paths(
        self,
        target_resource: str,
        max_paths: int = 20,
        max_depth: int = 20,
    ) -> list[list[str]]:
        """Find paths from internet-facing resources to a target.

        IaC dependencies are stored as:

            dependent -> dependency

        Attack traversal therefore follows the reverse/dependent direction.
        """

        if target_resource not in self.graph:
            return []

        entry_points = self.find_entry_points()

        paths: list[list[str]] = []

        for entry_point in entry_points:
            if len(paths) >= max_paths:
                break

            paths.extend(
                self._find_paths(
                    entry_point,
                    target_resource,
                    max_paths=max_paths - len(paths),
                    max_depth=max_depth,
                )
            )

        return paths[:max_paths]

    def _find_paths(
        self,
        start: str,
        target: str,
        max_paths: int,
        max_depth: int,
    ) -> list[list[str]]:
        """Breadth-first search for simple paths."""

        if start == target:
            return [[start]]

        queue: deque[list[str]] = deque([[start]])
        results: list[list[str]] = []

        while queue and len(results) < max_paths:
            path = queue.popleft()
            current = path[-1]

            if len(path) > max_depth:
                continue

            for neighbor in self.graph.get_dependents(current):
                if neighbor in path:
                    continue

                new_path = path + [neighbor]

                if neighbor == target:
                    results.append(new_path)
                else:
                    queue.append(new_path)

        return results

    def find_shortest_attack_path(
        self,
        target_resource: str,
    ) -> list[str]:
        """Return the shortest internet-to-target attack path."""

        paths = self.find_attack_paths(
            target_resource=target_resource,
            max_paths=100,
        )

        if not paths:
            return []

        return min(paths, key=len)

    @staticmethod
    def calculate_path_length(path: list[str]) -> int:
        """Return the number of edges in an attack path."""

        if len(path) < 2:
            return 0

        return len(path) - 1

    def calculate_topological_exposure(
        self,
        target_resource: str,
    ) -> float:
        """Calculate a normalized 0-1 exposure score from attack topology.

        Higher values indicate:
        - reachability from an internet-facing entry point;
        - fewer hops to the target;
        - more independent attack paths.
        """

        paths = self.find_attack_paths(
            target_resource=target_resource,
            max_paths=20,
        )

        if not paths:
            return 0.0

        shortest_length = min(
            self.calculate_path_length(path)
            for path in paths
        )

        distance_score = 1.0 / max(shortest_length, 1)
        path_score = min(len(paths) / 5.0, 1.0)

        exposure = (
            (0.7 * distance_score)
            + (0.3 * path_score)
        )

        return round(min(exposure, 1.0), 4)