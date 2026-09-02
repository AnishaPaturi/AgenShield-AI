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
    An attacker enters at an internet-facing entry point (e.g. Internet Gateway)
    and traverses through dependents (e.g. Security Group -> EC2 -> Unencrypted DB).
    """

    INTERNET_ENTRY_TYPES: set[str] = {
        # AWS
        "aws_internet_gateway",
        "aws_lb",
        "aws_alb",
        "aws_elb",
        "aws_api_gateway",
        "aws_apigatewayv2_api",
        "aws_cloudfront_distribution",
        "aws_eip",
        "aws_nat_gateway",
        "aws_waf_web_acl",
        "aws_wafv2_web_acl",
        # Azure
        "azure_application_gateway",
        "azurerm_application_gateway",
        "azurerm_public_ip",
        "azurerm_lb",
        "azurerm_frontdoor",
        "azurerm_traffic_manager_profile",
        # GCP
        "google_compute_global_forwarding_rule",
        "google_compute_forwarding_rule",
        "google_compute_target_http_proxy",
        "google_compute_target_https_proxy",
        # Kubernetes
        "ingress",
        # CloudFormation
        "aws::ec2::internetgateway",
        "aws::elasticloadbalancingv2::loadbalancer",
        "aws::cloudfront::distribution",
        "aws::apigateway::restapi",
    }

    SENSITIVE_TYPES: set[str] = {
        # Databases
        "aws_db_instance",
        "aws_rds_cluster",
        "aws_rds_cluster_instance",
        "aws_dynamodb_table",
        "aws_redshift_cluster",
        "aws_docdb_cluster",
        "azurerm_cosmosdb_account",
        "azurerm_mssql_database",
        "azurerm_postgresql_server",
        "google_sql_database_instance",
        "google_bigquery_dataset",
        "aws::rds::dbinstance",
        "aws::rds::dbcluster",
        "aws::dynamodb::table",
        # Storage
        "aws_s3_bucket",
        "azurerm_storage_account",
        "google_storage_bucket",
        "aws::s3::bucket",
        # Secrets / KMS
        "aws_secretsmanager_secret",
        "aws_ssm_parameter",
        "aws_kms_key",
        "azurerm_key_vault",
        "azurerm_key_vault_secret",
        "google_secret_manager_secret",
        "google_kms_crypto_key",
        "aws::secretsmanager::secret",
    }

    COMPUTE_TYPES: set[str] = {
        "aws_instance",
        "aws_lambda_function",
        "aws_ecs_task_definition",
        "aws_eks_cluster",
        "azurerm_linux_virtual_machine",
        "azurerm_windows_virtual_machine",
        "google_compute_instance",
        "aws::ec2::instance",
        "aws::lambda::function",
    }

    def __init__(self) -> None:
        self.resources: dict[str, dict[str, Any]] = {}
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        self.dependents: dict[str, set[str]] = defaultdict(set)
        self.relationships: list[dict[str, Any]] = []
        self.edge_types: dict[tuple[str, str], str] = {}

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
        """Add a directed dependency relationship: source_id depends on target_id."""

        if source_id not in self.resources:
            self.add_resource(source_id)

        if target_id not in self.resources:
            self.add_resource(target_id)

        self.dependencies[source_id].add(target_id)
        self.dependents[target_id].add(source_id)
        self.edge_types[(source_id, target_id)] = relationship_type
        self.relationships.append({
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
        })

    @classmethod
    def from_template(cls, template: IaCTemplate) -> "ResourceGraph":
        """Build a resource graph from an IaCTemplate, resolving AST nodes, explicit dependencies,
        and inferring implicit references and topological cloud network connections."""

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

            # Auto-infer reference relationships from resource attributes
            cls._infer_reference_relationships(graph)

        for dependency in template.dependencies:
            graph.add_relationship(
                source_id=dependency.source_id,
                target_id=dependency.target_id,
                relationship_type=dependency.dependency_type,
            )

        # Auto-infer cloud topological ingress routes (e.g. IGW -> SG)
        cls._infer_cloud_topology(graph)

        return graph

    @classmethod
    def _infer_reference_relationships(cls, graph: "ResourceGraph") -> None:
        """Scan resource attributes for references to other known resources."""
        known_ids = set(graph.resources.keys())
        name_to_ids: dict[str, list[str]] = defaultdict(list)
        for res_id, res in graph.resources.items():
            name = res.get("name")
            if name:
                name_to_ids[name].append(res_id)
            if "." in res_id:
                parts = res_id.split(".", 1)
                name_to_ids[parts[1]].append(res_id)

        for res_id, res in list(graph.resources.items()):
            attrs = res.get("attributes", {})
            refs = cls._extract_references_from_data(attrs, known_ids, name_to_ids, current_id=res_id)
            for target_id, rel_type in refs:
                if target_id != res_id:
                    graph.add_relationship(source_id=res_id, target_id=target_id, relationship_type=rel_type)

    @classmethod
    def _extract_references_from_data(
        cls,
        data: Any,
        known_ids: set[str],
        name_to_ids: dict[str, list[str]],
        current_id: str,
    ) -> list[tuple[str, str]]:
        """Recursively search data structures for references to known resources."""
        refs: list[tuple[str, str]] = []

        if isinstance(data, str):
            val = data.strip().strip('"').strip("'")
            for kid in known_ids:
                if kid == val or kid in val:
                    refs.append((kid, "reference"))
            if val in name_to_ids:
                for target_id in name_to_ids[val]:
                    if target_id != current_id:
                        refs.append((target_id, "named_reference"))

        elif isinstance(data, dict):
            # CloudFormation Ref / Fn::GetAtt
            if "Ref" in data and isinstance(data["Ref"], str):
                ref_target = data["Ref"]
                if ref_target in known_ids:
                    refs.append((ref_target, "cfn_ref"))
                elif ref_target in name_to_ids:
                    for target_id in name_to_ids[ref_target]:
                        refs.append((target_id, "cfn_ref"))

            if "Fn::GetAtt" in data and isinstance(data["Fn::GetAtt"], list) and len(data["Fn::GetAtt"]) > 0:
                target_name = data["Fn::GetAtt"][0]
                if target_name in known_ids:
                    refs.append((target_name, "cfn_getatt"))
                elif target_name in name_to_ids:
                    for target_id in name_to_ids[target_name]:
                        refs.append((target_id, "cfn_getatt"))

            for k, v in data.items():
                k_lower = str(k).lower()
                if k_lower in {
                    "vpc_security_group_ids",
                    "security_groups",
                    "security_group_id",
                    "source_security_group_id",
                    "subnet_id",
                    "subnets",
                    "vpc_id",
                    "depends_on",
                    "target_group_arn",
                    "iam_instance_profile",
                    "role",
                }:
                    if isinstance(v, str):
                        for kid in known_ids:
                            if kid in v or v in kid:
                                refs.append((kid, "network_association"))
                        if v in name_to_ids:
                            for target_id in name_to_ids[v]:
                                refs.append((target_id, "network_association"))
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                for kid in known_ids:
                                    if kid in item or item in kid:
                                        refs.append((kid, "network_association"))
                                if item in name_to_ids:
                                    for target_id in name_to_ids[item]:
                                        refs.append((target_id, "network_association"))
                else:
                    refs.extend(cls._extract_references_from_data(v, known_ids, name_to_ids, current_id))

        elif isinstance(data, list):
            for item in data:
                refs.extend(cls._extract_references_from_data(item, known_ids, name_to_ids, current_id))

        return refs

    @classmethod
    def _infer_cloud_topology(cls, graph: "ResourceGraph") -> None:
        """Infer cloud network routing topology such as Internet Gateway -> Security Group.

        In AWS/Cloud architecture, an Internet Gateway connects public internet traffic to
        the VPC and its internet-facing security groups. Connecting:
            security_group -> internet_gateway
        means that in attack traversal along dependents:
            internet_gateway -> security_group -> ec2 -> database
        exploitability routes can be evaluated.
        """
        igw_nodes = [
            rid for rid, r in graph.resources.items()
            if "internet_gateway" in str(r.get("resource_type") or "").lower()
            or "internetgateway" in str(r.get("resource_type") or "").lower()
            or "igw" in str(r.get("name") or "").lower()
        ]

        if not igw_nodes:
            return

        for igw_id in igw_nodes:
            # Connect IGW to internet-exposed security groups
            for rid, r in graph.resources.items():
                if rid == igw_id:
                    continue
                rtype = str(r.get("resource_type") or "").lower()
                if "security_group" in rtype or "securitygroup" in rtype:
                    if graph.is_internet_exposed(rid):
                        if igw_id not in graph.dependencies[rid]:
                            graph.add_relationship(
                                source_id=rid,
                                target_id=igw_id,
                                relationship_type="internet_route",
                            )

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
        """Determine whether a resource is marked or configured as internet-facing."""

        resource = self.get_resource(resource_id)

        if resource is None:
            return False

        attributes = resource.get("attributes", {})
        metadata = resource.get("metadata", {})

        public_keys = {
            "internet_exposed",
            "internet_facing",
            "public",
            "publicly_accessible",
            "exposed_to_internet",
            "associate_public_ip_address",
            "map_public_ip_on_launch",
            "public_network_access_enabled",
        }

        for container in (attributes, metadata):
            if self._contains_true_flag(container, public_keys):
                return True

            if self._contains_public_cidr(container):
                return True

            if self._contains_public_indicator(container):
                return True

        resource_type = str(resource.get("resource_type") or "").lower()

        return resource_type in self.INTERNET_ENTRY_TYPES

    def is_sensitive_asset(self, resource_id: str) -> bool:
        """Determine if a resource is a sensitive data store, secret, or cryptographic asset."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return False

        rtype = str(resource.get("resource_type") or "").lower()
        rname = str(resource.get("name") or "").lower()
        attrs = resource.get("attributes", {})

        if rtype in self.SENSITIVE_TYPES or any(
            t in rtype for t in ["db_", "database", "secret", "kms", "vault", "rds", "dynamodb", "s3_bucket"]
        ):
            return True

        if "unencrypted" in rname or "database" in rname:
            return True

        if attrs.get("storage_encrypted") is False or attrs.get("encrypted") is False:
            return True

        return False

    def is_compute_asset(self, resource_id: str) -> bool:
        """Determine if a resource is a compute asset (VM, container, serverless function)."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return False
        rtype = str(resource.get("resource_type") or "").lower()
        return rtype in self.COMPUTE_TYPES or any(
            t in rtype for t in ["instance", "lambda", "compute", "vm", "container"]
        )

    def is_iam_asset(self, resource_id: str) -> bool:
        """Determine if a resource is an IAM / privilege asset."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return False
        rtype = str(resource.get("resource_type") or "").lower()
        return "iam" in rtype or "role" in rtype or "policy" in rtype

    def get_asset_role(self, resource_id: str) -> str:
        """Return human-readable security role of the resource in attack paths."""
        resource = self.get_resource(resource_id) or {}
        rtype = str(resource.get("resource_type") or "").lower()

        if self.is_internet_exposed(resource_id):
            if "gateway" in rtype:
                return "Internet Gateway"
            if "security_group" in rtype:
                return "Publicly Accessible Security Group"
            if "lb" in rtype or "balancer" in rtype:
                return "Public Load Balancer"
            return "Internet Ingress / Entry Point"

        if "security_group" in rtype:
            return "Security Group"

        if self.is_sensitive_asset(resource_id):
            attrs = resource.get("attributes", {})
            if attrs.get("storage_encrypted") is False:
                return "Unencrypted Data Store"
            return "Sensitive Data Store"

        if self.is_compute_asset(resource_id):
            return "Compute Host"

        if self.is_iam_asset(resource_id):
            return "Privileged Identity"

        return "Infrastructure Resource"

    @staticmethod
    def _contains_true_flag(
        data: dict[str, Any],
        keys: set[str],
    ) -> bool:
        """Recursively search dictionaries and lists for true security flags."""

        for key, value in data.items():
            normalized_key = str(key).lower().replace("-", "_")

            if normalized_key in keys and (value is True or str(value).lower() in {"true", "enabled", "1"}):
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
        """Detect common public CIDR indicators (0.0.0.0/0, ::/0)."""

        if isinstance(data, str):
            cleaned = data.strip().lower()
            return cleaned in {"0.0.0.0/0", "::/0"} or "0.0.0.0/0" in cleaned or "::/0" in cleaned

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

    @staticmethod
    def _contains_public_indicator(data: Any) -> bool:
        """Detect public ACLs, IAM bindings, or open access flags."""
        public_tokens = {
            "public-read",
            "public-read-write",
            "allusers",
            "allauthenticatedusers",
        }

        if isinstance(data, str):
            val = data.strip().lower()
            return val in public_tokens or any(t in val for t in public_tokens)

        if isinstance(data, dict):
            return any(
                ResourceGraph._contains_public_indicator(v)
                for v in data.values()
            )

        if isinstance(data, list):
            return any(
                ResourceGraph._contains_public_indicator(item)
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
            "relationships": list(self.relationships),
            "entry_points": sorted(
                rid for rid in self.resources if self.is_internet_exposed(rid)
            ),
            "sensitive_assets": sorted(
                rid for rid in self.resources if self.is_sensitive_asset(rid)
            ),
        }

    def to_mermaid(self, highlight_paths: list[list[str]] | None = None) -> str:
        """Generate a Mermaid flowchart diagram representing the topological graph."""
        lines = ["graph LR"]

        highlight_edges: set[tuple[str, str]] = set()
        highlight_nodes: set[str] = set()

        if highlight_paths:
            for path in highlight_paths:
                for i in range(len(path) - 1):
                    highlight_edges.add((path[i], path[i + 1]))
                for node in path:
                    highlight_nodes.add(node)

        def sanitize_id(raw_id: str) -> str:
            return raw_id.replace(".", "_").replace("-", "_").replace(":", "_")

        for rid, r in self.resources.items():
            sid = sanitize_id(rid)
            role = self.get_asset_role(rid)
            label = f'"{r.get("name", rid)}<br/><small>{role}</small>"'
            lines.append(f"    {sid}[{label}]")

        for source_id, targets in sorted(self.dependents.items()):
            for target_id in sorted(targets):
                s_sid = sanitize_id(source_id)
                t_sid = sanitize_id(target_id)
                rel_type = self.edge_types.get((target_id, source_id), "route")
                if (source_id, target_id) in highlight_edges:
                    lines.append(f"    {s_sid} =={rel_type}==> {t_sid}")
                else:
                    lines.append(f"    {s_sid} -->|{rel_type}| {t_sid}")

        for rid in self.resources:
            sid = sanitize_id(rid)
            if self.is_sensitive_asset(rid):
                lines.append(f"    style {sid} fill:#ff4d4f,stroke:#fff,stroke-width:2px,color:#fff")
            elif self.is_internet_exposed(rid):
                lines.append(f"    style {sid} fill:#ffa940,stroke:#fff,stroke-width:2px,color:#fff")
            elif rid in highlight_nodes:
                lines.append(f"    style {sid} fill:#ff7875,stroke:#fff,stroke-width:2px,color:#fff")

        return "\n".join(lines)

    def __contains__(self, resource_id: str) -> bool:
        return resource_id in self.resources

    def __len__(self) -> int:
        return len(self.resources)