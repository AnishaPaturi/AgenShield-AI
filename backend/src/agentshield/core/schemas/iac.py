"""IaC Schema Contracts for AgentShield AI.

Defines core data structures for Infrastructure-as-Code templates,
Abstract Syntax Trees (AST), node representations, and cloud provider metadata.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IaCType(StrEnum):
    """Supported Infrastructure-as-Code platforms."""

    TERRAFORM = "terraform"
    CLOUDFORMATION = "cloudformation"
    KUBERNETES = "kubernetes"
    HELM = "helm"
    UNKNOWN = "unknown"


class CloudProvider(StrEnum):
    """Target Cloud Service Providers."""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI_CLOUD = "multi_cloud"
    UNKNOWN = "unknown"


class LineRange(BaseModel):
    """Represents a span of lines in a source IaC file."""

    model_config = ConfigDict(frozen=True)

    start_line: int = Field(..., ge=1, description="1-indexed starting line number")
    end_line: int = Field(..., ge=1, description="1-indexed ending line number")

    @field_validator("end_line")
    @classmethod
    def validate_line_range(cls, end_line: int, info: Any) -> int:
        start = info.data.get("start_line")
        if start is not None and end_line < start:
            raise ValueError(f"end_line ({end_line}) cannot be less than start_line ({start})")
        return end_line


class ASTNode(BaseModel):
    """Represents a node in the Abstract Syntax Tree (AST) of an IaC template."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_id: str = Field(..., description="Unique identifier for the node (e.g. resource path)")
    node_type: str = Field(
        ..., description="Kind of AST node (e.g., resource, variable, module, provider, output)"
    )
    name: str = Field(..., description="Logical or declared name of the AST node")
    resource_type: str | None = Field(
        default=None, description="IaC resource type (e.g. aws_s3_bucket, AWS::S3::Bucket)"
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict, description="Parsed attributes and key-value configurations"
    )
    children: list["ASTNode"] = Field(
        default_factory=list, description="Child AST nodes contained within this node"
    )
    line_range: LineRange | None = Field(
        default=None, description="Source file line span for this node"
    )
    parent_id: str | None = Field(
        default=None, description="node_id of parent node if applicable"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="node_ids of resources this node depends on"
    )
    resolved_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Pre-evaluated dynamic variables and parameter values"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context or parser specific metadata"
    )

    def find_nodes_by_type(self, target_node_type: str) -> list["ASTNode"]:
        """Recursively search for nodes matching a given node_type."""
        results: list[ASTNode] = []
        if self.node_type == target_node_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find_nodes_by_type(target_node_type))
        return results

    def find_resources_by_resource_type(self, target_resource_type: str) -> list["ASTNode"]:
        """Recursively search for nodes matching a specific IaC resource_type."""
        results: list[ASTNode] = []
        if self.resource_type == target_resource_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find_resources_by_resource_type(target_resource_type))
        return results


class ResourceDependency(BaseModel):
    """Represents a directed dependency edge between two IaC resources."""

    source_id: str = Field(..., description="node_id of dependent resource")
    target_id: str = Field(..., description="node_id of dependency target resource")
    dependency_type: str = Field(
        default="explicit", description="Type of dependency (explicit, implicit, reference)"
    )


class IaCTemplate(BaseModel):
    """Represents an ingested Infrastructure-as-Code template file and its parsed representation."""

    template_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique template identifier"
    )
    file_path: str = Field(..., description="Absolute or workspace-relative path to the IaC file")
    iac_type: IaCType = Field(
        default=IaCType.UNKNOWN, description="Detected or specified IaC engine type"
    )
    cloud_provider: CloudProvider = Field(
        default=CloudProvider.UNKNOWN, description="Primary target cloud platform"
    )
    raw_content: str = Field(..., description="Unparsed raw text content of the IaC template")
    parsed_ast: ASTNode | None = Field(
        default=None, description="Root AST node generated by Hybrid AST Parser Agent"
    )
    dependencies: list[ResourceDependency] = Field(
        default_factory=list, description="Dependency graph relationships extracted from AST"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="File tags, size, hash, and environment variables"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when template was ingested",
    )

    def auto_detect_type(self) -> IaCType:
        """Infer IaCType from file extension or content patterns if unknown."""
        if self.iac_type != IaCType.UNKNOWN:
            return self.iac_type

        lower_path = self.file_path.lower()
        if lower_path.endswith(".tf") or lower_path.endswith(".tf.json"):
            self.iac_type = IaCType.TERRAFORM
        elif lower_path.endswith(".template") or "AWSTemplateFormatVersion" in self.raw_content:
            self.iac_type = IaCType.CLOUDFORMATION
        elif lower_path.endswith("chart.yaml") or lower_path.endswith("values.yaml"):
            self.iac_type = IaCType.HELM
        elif lower_path.endswith(".yaml") or lower_path.endswith(".yml"):
            if "apiVersion:" in self.raw_content and "kind:" in self.raw_content:
                self.iac_type = IaCType.KUBERNETES
            elif "Resources:" in self.raw_content:
                self.iac_type = IaCType.CLOUDFORMATION
        elif lower_path.endswith(".json") and (
            "AWSTemplateFormatVersion" in self.raw_content or "Resources" in self.raw_content
        ):
            self.iac_type = IaCType.CLOUDFORMATION

        return self.iac_type


# Resolve forward ref for self-referential children in ASTNode for Pydantic v2
ASTNode.model_rebuild()
