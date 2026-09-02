"""Tests for Task 3.4 CLI Triage Interface and API Endpoints."""

from fastapi.testclient import TestClient

from agentshield.api.main import app
from agentshield.cli.triage import main as cli_main
from agentshield.core.audit import (
    AuditQueueItem,
    AuditStatus,
    EscalationReason,
    audit_queue_manager,
)
from agentshield.core.schemas.vulnerability import Severity, VulnerabilityFinding


def create_sample_audit_item(finding_id: str = "test-finding-1", confidence: float = 0.75) -> AuditQueueItem:
    finding = VulnerabilityFinding(
        finding_id=finding_id,
        rule_id="CKV_AWS_20",
        title="S3 Bucket Read Permissions Open",
        description="Public bucket access detected.",
        severity=Severity.HIGH,
        confidence_score=confidence,
        affected_resource="aws_s3_bucket.my_data",
        requires_human_review=True,
        auto_patchable=False,
        attack_path=["aws_internet_gateway.igw", "aws_s3_bucket.my_data"],
    )
    item = AuditQueueItem(
        finding_id=finding_id,
        workspace_id="test-ws-1",
        file_path="main.tf",
        finding=finding,
        status=AuditStatus.PENDING_REVIEW,
        escalation_reason="Low confidence score 0.75 < 0.85 threshold",
        escalation_trigger=EscalationReason.LOW_CONFIDENCE,
        priority_score=78.5,
        priority="HIGH",
        attack_path=finding.attack_path,
        blast_radius=2,
    )
    return audit_queue_manager.enqueue(item)


def test_cli_triage_list_and_stats(capsys):
    """Test CLI commands: list and stats."""
    audit_queue_manager.clear()
    item = create_sample_audit_item("f-cli-1")

    # Run list command
    code = cli_main(["list"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "AGENTSHIELD AI — HUMAN SECURITY AUDIT QUEUE" in captured
    assert item.item_id in captured

    # Run stats command
    code = cli_main(["stats"])
    assert code == 0
    captured_stats = capsys.readouterr().out
    assert "AGENTSHIELD AI — AUDIT QUEUE METRICS" in captured_stats
    assert "Pending Review:         1" in captured_stats


def test_cli_triage_inspect(capsys):
    """Test CLI command: inspect <item_id>."""
    audit_queue_manager.clear()
    item = create_sample_audit_item("f-cli-inspect")

    code = cli_main(["inspect", item.item_id])
    assert code == 0
    captured = capsys.readouterr().out
    assert f"AUDIT ITEM: {item.item_id}" in captured
    assert "Exploitability Route (Attack Path):" in captured
    assert "aws_internet_gateway.igw → aws_s3_bucket.my_data" in captured


def test_cli_triage_approve_and_reject(capsys):
    """Test CLI commands: approve and reject."""
    audit_queue_manager.clear()
    item1 = create_sample_audit_item("f-cli-app")
    item2 = create_sample_audit_item("f-cli-rej")

    # Approve item 1
    code = cli_main(["approve", item1.item_id, "--reviewer", "alice_sec", "--comment", "Valid finding"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "Successfully APPROVED" in captured

    approved_item = audit_queue_manager.get_item(item1.item_id)
    assert approved_item.status == AuditStatus.APPROVED
    assert approved_item.reviewer == "alice_sec"

    # Reject item 2
    code2 = cli_main(["reject", item2.item_id, "--reviewer", "bob_sec", "--comment", "Known exception"])
    assert code2 == 0
    captured2 = capsys.readouterr().out
    assert "Successfully REJECTED" in captured2

    rejected_item = audit_queue_manager.get_item(item2.item_id)
    assert rejected_item.status == AuditStatus.REJECTED
    assert rejected_item.reviewer == "bob_sec"


def test_audit_queue_api_endpoints():
    """Test HTTP API endpoints for audit queue."""
    audit_queue_manager.clear()
    item = create_sample_audit_item("f-api-1")

    client = TestClient(app)

    # 1. GET /api/audit-queue
    resp = client.get("/api/audit-queue")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(i["item_id"] == item.item_id for i in data)

    # 2. GET /api/audit-queue/stats
    resp_stats = client.get("/api/audit-queue/stats")
    assert resp_stats.status_code == 200
    stats = resp_stats.json()
    assert stats["pending_count"] >= 1

    # 3. GET /api/audit-queue/{item_id}
    resp_item = client.get(f"/api/audit-queue/{item.item_id}")
    assert resp_item.status_code == 200
    assert resp_item.json()["item_id"] == item.item_id

    # 4. POST /api/audit-queue/{item_id}/decision (Approve)
    resp_decide = client.post(
        f"/api/audit-queue/{item.item_id}/decision",
        json={"decision": "approve", "reviewer": "api_sec_engineer", "comment": "Approved via Web UI"},
    )
    assert resp_decide.status_code == 200
    decided_item = resp_decide.json()
    assert decided_item["status"] == "APPROVED"
    assert decided_item["reviewer"] == "api_sec_engineer"
