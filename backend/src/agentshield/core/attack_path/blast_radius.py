"""Blast-radius calculation for compromised infrastructure resources."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

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

    def get_blast_radius_breakdown(
        self,
        resource_id: str,
        max_depth: int | None = None,
    ) -> dict[str, Any]:
        """Provide detailed structural breakdown of blast-radius exposure.

        Categorizes affected resources by asset type, identifies sensitive assets
        (databases, secrets) compromised in downstream blast radius, and maps
        hop distance layers.
        """
        if resource_id not in self.graph:
            return {
                "total_affected": 0,
                "reachable_resources": [],
                "sensitive_count": 0,
                "sensitive_assets": [],
                "by_category": {},
                "depth_layers": {},
                "has_sensitive_exposure": False,
            }

        depth_layers: dict[int, list[str]] = defaultdict(list)
        reachable: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(resource_id, 0)])

        while queue:
            current, depth = queue.popleft()

            if max_depth is not None and depth >= max_depth:
                continue

            for dependent in self.graph.get_dependents(current):
                if dependent in reachable or dependent == resource_id:
                    continue

                reachable.add(dependent)
                depth_layers[depth + 1].append(dependent)
                queue.append((dependent, depth + 1))

        # Categorize affected resources
        by_category: dict[str, list[str]] = {
            "databases": [],
            "compute": [],
            "storage": [],
            "iam": [],
            "networking": [],
            "other": [],
        }
        sensitive_assets: list[str] = []

        for rid in sorted(reachable):
            res = self.graph.get_resource(rid) or {}
            rtype = str(res.get("resource_type") or "").lower()

            if self.graph.is_sensitive_asset(rid):
                sensitive_assets.append(rid)

            if "db" in rtype or "database" in rtype or "rds" in rtype:
                by_category["databases"].append(rid)
            elif self.graph.is_compute_asset(rid):
                by_category["compute"].append(rid)
            elif "s3" in rtype or "storage" in rtype or "bucket" in rtype:
                by_category["storage"].append(rid)
            elif self.graph.is_iam_asset(rid):
                by_category["iam"].append(rid)
            elif "vpc" in rtype or "subnet" in rtype or "gateway" in rtype or "route" in rtype:
                by_category["networking"].append(rid)
            else:
                by_category["other"].append(rid)

        # Filter out empty categories
        active_categories = {k: v for k, v in by_category.items() if v}

        return {
            "total_affected": len(reachable),
            "reachable_resources": sorted(reachable),
            "sensitive_count": len(sensitive_assets),
            "sensitive_assets": sorted(sensitive_assets),
            "by_category": active_categories,
            "depth_layers": {d: sorted(nodes) for d, nodes in sorted(depth_layers.items())},
            "has_sensitive_exposure": len(sensitive_assets) > 0,
        }

    def calculate_weighted_impact_score(
        self,
        resource_id: str,
    ) -> float:
        """Calculate impact score adjusted for compromised asset sensitivity."""
        breakdown = self.get_blast_radius_breakdown(resource_id)
        base_score = self.calculate_impact_score(resource_id)

        if breakdown["total_affected"] == 0:
            return 0.0

        # Sensitivity multiplier: up to +30% boost if sensitive data stores are in blast radius
        sensitive_ratio = breakdown["sensitive_count"] / max(breakdown["total_affected"], 1)
        weighted_score = base_score * (1.0 + (0.3 * sensitive_ratio))

        return round(min(weighted_score, 1.0), 4)