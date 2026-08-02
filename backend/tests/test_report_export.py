"""Unit tests for agentshield.api.report_export renderers."""

import json

from agentshield.api.report_export import (
    render_html,
    render_json,
    render_markdown,
    render_pdf,
    render_sarif,
)
from agentshield.core.schemas import AgentShieldWorkspace


def test_render_json_roundtrip(sample_workspace: AgentShieldWorkspace) -> None:
    out = render_json(sample_workspace)
    parsed = json.loads(out)
    assert parsed["workspace_id"] == sample_workspace.workspace_id


def test_render_markdown_contains_finding(sample_workspace: AgentShieldWorkspace) -> None:
    out = render_markdown(sample_workspace)
    assert "S3 Bucket Read Permissions Open To Public" in out
    assert "```diff" in out


def test_render_html_contains_badge(sample_workspace: AgentShieldWorkspace) -> None:
    out = render_html(sample_workspace)
    assert "<html" in out
    assert 'class="badge HIGH"' in out


def test_render_sarif_is_valid_json_with_rules(sample_workspace: AgentShieldWorkspace) -> None:
    out = render_sarif(sample_workspace)
    parsed = json.loads(out)
    assert parsed["version"] == "2.1.0"
    rules = parsed["runs"][0]["tool"]["driver"]["rules"]
    assert any(r["id"] == "CKV_AWS_20" for r in rules)


def test_render_pdf_returns_nonempty_bytes(sample_workspace: AgentShieldWorkspace) -> None:
    out = render_pdf(sample_workspace)
    assert isinstance(out, bytes)
    assert out[:4] == b"%PDF"
