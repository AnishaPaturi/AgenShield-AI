"""Attack-path analysis for infrastructure resource graphs."""

from __future__ import annotations

from collections import Counter, deque
from typing import Any

from agentshield.core.attack_path.graph import ResourceGraph


class AttackPathAnalyzer:
    """Find and evaluate exploitability routes through an infrastructure graph."""

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
        (e.g., Internet Gateway -> Security Group -> EC2 -> Unencrypted DB).
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

    def find_all_exploitability_routes(
        self,
        max_paths_per_target: int = 5,
    ) -> dict[str, list[list[str]]]:
        """Discover exploitability routes to all sensitive assets and targets."""
        routes: dict[str, list[list[str]]] = {}
        for rid in self.graph.resources:
            if self.graph.is_sensitive_asset(rid) or not self.graph.is_internet_exposed(rid):
                paths = self.find_attack_paths(rid, max_paths=max_paths_per_target)
                if paths:
                    routes[rid] = paths
        return routes

    def evaluate_route_exploitability(
        self,
        path: list[str],
    ) -> list[dict[str, Any]]:
        """Return a structured step-by-step evaluation of an exploitability route."""
        if not path:
            return []

        hops: list[dict[str, Any]] = []

        for i in range(len(path)):
            current_id = path[i]
            res = self.graph.get_resource(current_id) or {}
            role = self.graph.get_asset_role(current_id)
            rtype = res.get("resource_type") or "unknown"

            if i == 0:
                action = f"Initial unauthenticated ingress at perimeter ({role})"
            elif i == len(path) - 1:
                action = f"Target impact on {role} ({current_id})"
            else:
                action = f"Lateral pivot through {role} ({current_id})"

            hop_info: dict[str, Any] = {
                "step": i + 1,
                "resource_id": current_id,
                "resource_type": rtype,
                "role": role,
                "action": action,
            }

            if i < len(path) - 1:
                next_id = path[i + 1]
                edge_type = self.graph.edge_types.get(
                    (next_id, current_id),
                    self.graph.edge_types.get((current_id, next_id), "allows_traffic"),
                )
                hop_info["next_hop"] = next_id
                hop_info["transition_type"] = edge_type

            hops.append(hop_info)

        return hops

    @staticmethod
    def format_path_string(path: list[str]) -> str:
        """Format an attack path as a human-readable arrow sequence."""
        if not path:
            return "No attack path detected (isolated)"
        return " → ".join(path)

    def generate_mermaid_path(
        self,
        path: list[str],
        title: str = "Exploitability Route",
    ) -> str:
        """Generate a focused Mermaid diagram for a specific attack path."""
        if not path:
            return "graph LR\n    none[No Attack Path Detected]"

        lines = [f"graph LR", f"    %% {title}"]

        def sanitize_id(raw_id: str) -> str:
            return raw_id.replace(".", "_").replace("-", "_").replace(":", "_")

        for i, node_id in enumerate(path):
            sid = sanitize_id(node_id)
            role = self.graph.get_asset_role(node_id)
            res = self.graph.get_resource(node_id) or {}
            name = res.get("name", node_id)
            label = f'"{name}<br/><small>{role}</small>"'
            lines.append(f"    {sid}[{label}]")

        for i in range(len(path) - 1):
            s_sid = sanitize_id(path[i])
            t_sid = sanitize_id(path[i + 1])
            edge_type = self.graph.edge_types.get((path[i + 1], path[i]), "routes_to")
            lines.append(f"    {s_sid} =={edge_type}==> {t_sid}")

        # Highlight start (entry) and end (target)
        start_sid = sanitize_id(path[0])
        end_sid = sanitize_id(path[-1])
        lines.append(f"    style {start_sid} fill:#ffa940,stroke:#333,stroke-width:2px,color:#fff")
        lines.append(f"    style {end_sid} fill:#ff4d4f,stroke:#333,stroke-width:2px,color:#fff")

        return "\n".join(lines)

    def find_choke_points(
        self,
        target_resource: str | None = None,
    ) -> list[dict[str, Any]]:
        """Identify critical topological choke points.

        A choke point is an intermediate node that appears in multiple attack paths.
        Remediating or securing a choke point breaks the greatest number of exploit routes.
        """
        all_paths: list[list[str]] = []

        if target_resource:
            all_paths = self.find_attack_paths(target_resource, max_paths=50)
        else:
            routes = self.find_all_exploitability_routes(max_paths_per_target=10)
            for path_list in routes.values():
                all_paths.extend(path_list)

        if not all_paths:
            return []

        # Count intermediate nodes (exclude start and final destination)
        node_counts: Counter[str] = Counter()
        for path in all_paths:
            if len(path) > 2:
                for intermediate in path[1:-1]:
                    node_counts[intermediate] += 1

        total_paths = len(all_paths)
        choke_points: list[dict[str, Any]] = []

        for node_id, count in node_counts.most_common():
            res = self.graph.get_resource(node_id) or {}
            choke_points.append({
                "resource_id": node_id,
                "resource_type": res.get("resource_type"),
                "name": res.get("name", node_id),
                "paths_severed_if_remediated": count,
                "mitigation_coverage_pct": round((count / total_paths) * 100, 1),
                "role": self.graph.get_asset_role(node_id),
            })

        return choke_points