"""Unit tests for SQLite WorkspaceStore implementation."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from agentshield.api.store import WorkspaceStore
from agentshield.core.schemas.contracts import AgentShieldWorkspace
from agentshield.core.schemas.iac import IaCTemplate, IaCType
from agentshield.core.schemas.vulnerability import (
    Severity,
    VulnerabilityFinding,
    VulnerabilityReport,
    VulnerabilitySummary,
)


def _create_mock_workspace(workspace_id: str = "ws-test-1", risk_score: float = 75.0) -> AgentShieldWorkspace:
    template = IaCTemplate(
        template_id="tpl-1",
        file_path="main.tf",
        raw_content='resource "aws_s3_bucket" "b" {}',
        iac_type=IaCType.TERRAFORM,
    )
    summary = VulnerabilitySummary(
        total_vulnerabilities=1,
        critical_count=0,
        high_count=1,
        medium_count=0,
        low_count=0,
        info_count=0,
        risk_score=risk_score,
    )
    finding = VulnerabilityFinding(
        finding_id="f-1",
        rule_id="CKV_AWS_20",
        title="S3 Bucket Open",
        description="Public access",
        severity=Severity.HIGH,
        confidence_score=0.9,
        affected_resource="aws_s3_bucket.b",
    )
    report = VulnerabilityReport(
        template_id="tpl-1",
        target_file="main.tf",
        summary=summary,
        findings=[finding],
    )
    return AgentShieldWorkspace(
        workspace_id=workspace_id,
        template=template,
        report=report,
        status="REMEDIATED",
    )


def test_sqlite_store_crud(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    store = WorkspaceStore(db_path=db_file)

    assert db_file.exists()
    assert store.list_all() == []

    # Save
    ws = _create_mock_workspace("ws-1", risk_score=82.5)
    saved = store.save(ws)
    assert saved.workspace_id == "ws-1"

    # Get
    retrieved = store.get("ws-1")
    assert retrieved is not None
    assert retrieved.workspace_id == "ws-1"
    assert retrieved.report.summary.risk_score == 82.5
    assert retrieved.template.file_path == "main.tf"

    # Get non-existent
    assert store.get("non-existent") is None

    # List all
    ws2 = _create_mock_workspace("ws-2", risk_score=40.0)
    store.save(ws2)
    all_ws = store.list_all()
    assert len(all_ws) == 2
    ids = {w.workspace_id for w in all_ws}
    assert ids == {"ws-1", "ws-2"}

    # Update
    ws.status = "DEPLOYED"
    store.save(ws)
    updated = store.get("ws-1")
    assert updated.status == "DEPLOYED"
    assert len(store.list_all()) == 2

    # Delete
    assert store.delete("ws-1") is True
    assert store.get("ws-1") is None
    assert store.delete("ws-1") is False
    assert len(store.list_all()) == 1

    # Clear
    store.clear()
    assert store.list_all() == []


def test_sqlite_persistence_across_instances(tmp_path: Path) -> None:
    db_file = tmp_path / "persisted.db"
    store1 = WorkspaceStore(db_path=db_file)
    ws = _create_mock_workspace("ws-persisted")
    store1.save(ws)

    # Re-open with a new instance pointing to the same file
    store2 = WorkspaceStore(db_path=db_file)
    retrieved = store2.get("ws-persisted")
    assert retrieved is not None
    assert retrieved.workspace_id == "ws-persisted"


def test_legacy_json_migration(tmp_path: Path) -> None:
    legacy_dir = tmp_path / "legacy_data"
    legacy_dir.mkdir()

    # Write a legacy JSON workspace file
    ws = _create_mock_workspace("ws-legacy")
    json_file = legacy_dir / "ws-legacy.json"
    json_file.write_text(ws.model_dump_json(indent=2), encoding="utf-8")

    # Initialize store pointing to legacy_dir
    store = WorkspaceStore(persist_dir=legacy_dir)

    # Verify legacy file was imported into SQLite
    imported = store.get("ws-legacy")
    assert imported is not None
    assert imported.workspace_id == "ws-legacy"
    assert (legacy_dir / "agentshield.db").exists()
