"""Tests for AgentShieldWorkspace aggregate contract and unified re-exports."""

from agentshield.core.schemas import (
    AgentShieldWorkspace,
    ASTNode,
    IaCTemplate,
    PatchDiff,
    VulnerabilityReport,
)


def test_agentshield_workspace(sample_workspace: AgentShieldWorkspace):
    assert sample_workspace.status == "REMEDIATED"
    assert isinstance(sample_workspace.template, IaCTemplate)
    assert isinstance(sample_workspace.report, VulnerabilityReport)
    assert len(sample_workspace.patches) == 1
    assert isinstance(sample_workspace.patches[0], PatchDiff)


def test_schema_exports():
    from agentshield.core.schemas import (
        ASTNode as ExportedASTNode,
    )
    from agentshield.core.schemas import (
        IaCTemplate as ExportedIaCTemplate,
    )
    from agentshield.core.schemas import (
        PatchDiff as ExportedPatchDiff,
    )
    from agentshield.core.schemas import (
        VulnerabilityReport as ExportedVulnerabilityReport,
    )

    assert ExportedASTNode is ASTNode
    assert ExportedIaCTemplate is IaCTemplate
    assert ExportedPatchDiff is PatchDiff
    assert ExportedVulnerabilityReport is VulnerabilityReport
