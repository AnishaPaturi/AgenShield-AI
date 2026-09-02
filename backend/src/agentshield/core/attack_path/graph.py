"""Infrastructure resource graph for attack-path analysis."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from agentshield.core.schemas.iac import ASTNode, IaCTemplate


class ResourceGraph:
    """Directed graph representing relationships between IaC resources.

    The IaC schema defines a dependency as:

        source_id -> target_id

    where source_id is the dependent resource and target_id is the
    resource it depends on.

    For security analysis, both directions are maintained:

        dependencies: source -> target
        dependents:   target -> source

    The reverse direction is useful for attack-path and blast-radius analysis.
    """

    def __init__(self) -> None:
        self.resources: dict[str, dict[str, Any]] = {}
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        self.dependents: dict[str, set[str]] = defaultdict(set)

    def add_resource(
        self,
        resource_id: str,
        resource_type: str | None = None,
        name: str | None = None,
        attributes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add or update a resource in the graph."""

        self.resources[resource_id] = {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "name": name or resource_id,
            "attributes": attributes or {},
            "metadata": metadata or {},
        }

        self.dependencies.setdefault(resource_id, set())
        self.dependents.setdefault(resource_id, set())

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "explicit",
    ) -> None:
        """Add a directed dependency relationship."""

        if source_id not in self.resources:
            self.add_resource(source_id)

        if target_id not in self.resources:
            self.add_resource(target_id)

        self.dependencies[source_id].add(target_id)
        self.dependents[target_id].add(source_id)

    @classmethod
    def from_template(cls, template: IaCTemplate) -> "ResourceGraph":
        """Build a resource graph from an IaCTemplate."""

        graph = cls()

        if template.parsed_ast is not None:
            for node in cls._resource_nodes(template.parsed_ast):
                graph.add_resource(
                    resource_id=node.node_id,
                    resource_type=node.resource_type,
                    name=node.name,
                    attributes=node.attributes,
                    metadata=node.metadata,
                )

                for dependency_id in node.dependencies:
                    graph.add_relationship(
                        source_id=node.node_id,
                        target_id=dependency_id,
                        relationship_type="ast",
                    )

        for dependency in template.dependencies:
            graph.add_relationship(
                source_id=dependency.source_id,
                target_id=dependency.target_id,
                relationship_type=dependency.dependency_type,
            )

        return graph

    @staticmethod
    def _resource_nodes(root: ASTNode) -> list[ASTNode]:
        """Return resource nodes recursively from an AST."""

        resources: list[ASTNode] = []

        if root.resource_type is not None or root.node_type.lower() == "resource":
            resources.append(root)

        for child in root.children:
            resources.extend(ResourceGraph._resource_nodes(child))

        return resources

    def get_resource(self, resource_id: str) -> dict[str, Any] | None:
        """Return resource metadata."""

        return self.resources.get(resource_id)

    def get_neighbors(self, resource_id: str) -> list[str]:
        """Return resources directly depended on by resource_id."""

        return sorted(self.dependencies.get(resource_id, set()))

    def get_dependencies(self, resource_id: str) -> list[str]:
        """Return direct dependency targets."""

        return self.get_neighbors(resource_id)

    def get_dependents(self, resource_id: str) -> list[str]:
        """Return resources that depend on resource_id."""

        return sorted(self.dependents.get(resource_id, set()))

    def is_internet_exposed(self, resource_id: str) -> bool:
        """Determine whether a resource is marked or configured as internet-facing.

        Explicit metadata/attributes are checked first, followed by common
        IaC security indicators such as 0.0.0.0/0.
        """

        resource = self.get_resource(resource_id)

        if resource is None:
            return False

        attributes = resource.get("attributes", {})
        metadata = resource.get("metadata", {})

        for container in (attributes, metadata):
            if self._contains_true_flag(
                container,
                {
                    "internet_exposed",
                    "internet_facing",
                    "public",
                    "publicly_accessible",
                    "exposed_to_internet",
                },
            ):
                return True

            if self._contains_public_cidr(container):
                return True

        resource_type = str(resource.get("resource_type") or "").lower()

        internet_entry_types = {
            "aws_internet_gateway",
            "aws_lb",
            "aws_alb",
            "aws_api_gateway",
            "aws_apigatewayv2_api",
            "aws_cloudfront_distribution",
            "azure_application_gateway",
            "google_compute_global_forwarding_rule",
        }

        return resource_type in internet_entry_types

    @staticmethod
    def _contains_true_flag(
        data: dict[str, Any],
        keys: set[str],
    ) -> bool:
        """Recursively search dictionaries and lists for true security flags."""

        for key, value in data.items():
            normalized_key = str(key).lower().replace("-", "_")

            if normalized_key in keys and value is True:
                return True

            if isinstance(value, dict):
                if ResourceGraph._contains_true_flag(value, keys):
                    return True

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if ResourceGraph._contains_true_flag(item, keys):
                            return True

        return False

    @staticmethod
    def _contains_public_cidr(data: Any) -> bool:
        """Detect common public CIDR indicators."""

        if isinstance(data, str):
            return data.strip() == "0.0.0.0/0"

        if isinstance(data, dict):
            return any(
                ResourceGraph._contains_public_cidr(value)
                for value in data.values()
            )

        if isinstance(data, list):
            return any(
                ResourceGraph._contains_public_cidr(item)
                for item in data
            )

        return False

    def get_graph(self) -> dict[str, Any]:
        """Return a serializable representation of the graph."""

        return {
            "resources": dict(self.resources),
            "dependencies": {
                key: sorted(value)
                for key, value in self.dependencies.items()
            },
            "dependents": {
                key: sorted(value)
                for key, value in self.dependents.items()
            },
        }

    def __contains__(self, resource_id: str) -> bool:
        return resource_id in self.resources

    def __len__(self) -> int:
        return len(self.resources)