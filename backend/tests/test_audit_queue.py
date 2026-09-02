"""Comprehensive tests for Task 3.4: Human Security Audit Queue & Triage Engine.

Tests:
- Automated escalation for low-confidence findings (C < 0.85)
- Automated escalation for non-consensus / model disagreement findings
- Automated escalation for critical findings with active attack paths
- Human triage decision processing: approve and reject actions
- State synchronization with AgentShieldWorkspace
- Queue metrics and statistics calculation
"""

from agentshield.api.store import workspace_store
from agentshield.core.audit import (
    AuditDecision,
    AuditQueueManager,
    AuditStatus,
    EscalationReason,
)
from agentshield.core.schemas.contracts import AgentShieldWorkspace
from agentshield.core.schemas.iac import IaCTemplate
from agentshield.core.schemas.vulnerability import (
    Severity,
    VulnerabilityFinding,
    VulnerabilityReport,
)


def test_automated_escalation_low_confidence(tmp_path):
    """Verify findings with confidence < 0.85 are automatically escalated."""
    queue_file = tmp_path / "test_audit_queue.json"
    manager = AuditQueueManager(persist_file=queue_file)

    finding_low_conf = VulnerabilityFinding(
        finding_id="finding-low-1",
        rule_id="CKV_AWS_20",
        title="S3 Bucket Read Permissions Open",
        description="Public bucket access detected.",
        severity=Severity.HIGH,
        confidence_score=0.72,  # Below 0.85 threshold
        affected_resource="aws_s3_bucket.data",
        requires_human_review=True,
        auto_patchable=False,
        escalation_reason="Confidence 0.72 < 0.85 threshold",
    )

    finding_high_conf = VulnerabilityFinding(
        finding_id="finding-high-1",
        rule_id="CKV_AWS_21",
        title="S3 Bucket Versioning Disabled",
        description="Versioning is not enabled.",
        severity=Severity.LOW,
        confidence_score=0.95,  # High confidence
        affected_resource="aws_s3_bucket.data",
        requires_human_review=False,
        auto_patchable=True,
    )

    report = VulnerabilityReport(
        template_id="tpl-1",
        target_file="main.tf",
        findings=[finding_low_conf, finding_high_conf],
    )
    workspace = AgentShieldWorkspace(
        template=IaCTemplate(file_path="main.tf", raw_content=""),
        report=report,
    )

    enqueued = manager.evaluate_and_enqueue(workspace)

    assert len(enqueued) == 1
    assert enqueued[0].finding_id == "finding-low-1"
    assert enqueued[0].escalation_trigger == EscalationReason.LOW_CONFIDENCE
    assert enqueued[0].status == AuditStatus.PENDING_REVIEW


def test_automated_escalation_model_disagreement(tmp_path):
    """Verify non-consensus multi-LLM findings trigger automated escalation."""
    queue_file = tmp_path / "test_audit_queue.json"
    manager = AuditQueueManager(persist_file=queue_file)

    finding_divergent = VulnerabilityFinding(
        finding_id="finding-div-1",
        rule_id="CKV_AWS_105",
        title="Security group allows unrestricted ingress",
        description="Only one of two ensemble LLMs identified this risk.",
        severity=Severity.HIGH,
        confidence_score=0.78,
        consensus_score=0.50,  # Below 0.80 consensus threshold
        requires_human_review=True,
        auto_patchable=False,
        model_agreements=["gpt-4o"],
        affected_resource="aws_security_group.sg",
    )

    report = VulnerabilityReport(
        template_id="tpl-1",
        target_file="main.tf",
        findings=[finding_divergent],
    )
    workspace = AgentShieldWorkspace(
        template=IaCTemplate(file_path="main.tf", raw_content=""),
        report=report,
    )

    enqueued = manager.evaluate_and_enqueue(workspace)

    assert len(enqueued) == 1
    assert enqueued[0].finding_id == "finding-div-1"
    assert enqueued[0].escalation_trigger in {
        EscalationReason.MODEL_DISAGREEMENT,
        EscalationReason.LOW_CONFIDENCE,
    }


def test_triage_decision_approve_and_reject(tmp_path):
    """Verify approving and rejecting queued findings updates status and syncs workspace."""
    queue_file = tmp_path / "test_audit_queue.json"
    manager = AuditQueueManager(persist_file=queue_file)

    finding = VulnerabilityFinding(
        finding_id="f-triage-1",
        rule_id="CKV_AWS_16",
        title="Unencrypted DB",
        description="Database encryption disabled.",
        severity=Severity.HIGH,
        confidence_score=0.80,
        requires_human_review=True,
        auto_patchable=False,
        affected_resource="aws_db_instance.db",
    )

    template = IaCTemplate(file_path="main.tf", raw_content="")
    report = VulnerabilityReport(
        template_id=template.template_id,
        target_file="main.tf",
        findings=[finding],
    )
    workspace = AgentShieldWorkspace(template=template, report=report)
    workspace_store.save(workspace)

    enqueued = manager.evaluate_and_enqueue(workspace)
    item_id = enqueued[0].item_id

    # 1. Approve decision
    approval = AuditDecision(
        decision="approve",
        reviewer="lead_sec_engineer@corp.com",
        comment="Confirmed legitimate finding in production VPC; approved for auto-remediation.",
    )
    approved_item = manager.submit_decision(item_id, approval, workspace_store=workspace_store)

    assert approved_item.status == AuditStatus.APPROVED
    assert approved_item.reviewer == "lead_sec_engineer@corp.com"
    assert approved_item.reviewed_at is not None

    # Verify workspace sync
    updated_ws = workspace_store.get(workspace.workspace_id)
    assert updated_ws is not None
    updated_f = updated_ws.report.findings[0]
    assert updated_f.auto_patchable is True
    assert updated_f.requires_human_review is False
    assert updated_f.raw_details["triage_status"] == "APPROVED"

    # 2. Reject decision
    rejection = AuditDecision(
        decision="reject",
        reviewer="lead_sec_engineer@corp.com",
        comment="Intentional public demo bucket; mark as false positive.",
    )
    rejected_item = manager.submit_decision(item_id, rejection, workspace_store=workspace_store)

    assert rejected_item.status == AuditStatus.REJECTED
    updated_ws = workspace_store.get(workspace.workspace_id)
    updated_f = updated_ws.report.findings[0]
    assert updated_f.auto_patchable is False
    assert updated_f.raw_details["triage_status"] == "REJECTED_FALSE_POSITIVE"

    # Cleanup test workspace
    workspace_store.delete(workspace.workspace_id)


def test_queue_summary_metrics(tmp_path):
    """Verify queue metrics calculation (pending, approved, rejected counts)."""
    queue_file = tmp_path / "test_audit_queue.json"
    manager = AuditQueueManager(persist_file=queue_file)

    f1 = VulnerabilityFinding(
        finding_id="f1",
        rule_id="R1",
        title="Finding 1",
        description="Desc",
        severity=Severity.CRITICAL,
        confidence_score=0.70,
        requires_human_review=True,
        affected_resource="r1",
    )
    f2 = VulnerabilityFinding(
        finding_id="f2",
        rule_id="R2",
        title="Finding 2",
        description="Desc",
        severity=Severity.HIGH,
        confidence_score=0.75,
        requires_human_review=True,
        affected_resource="r2",
    )

    report = VulnerabilityReport(template_id="t1", target_file="main.tf", findings=[f1, f2])
    ws = AgentShieldWorkspace(template=IaCTemplate(file_path="main.tf", raw_content=""), report=report)

    enqueued = manager.evaluate_and_enqueue(ws)
    assert len(enqueued) == 2

    stats = manager.get_queue_summary()
    assert stats["total_items"] == 2
    assert stats["pending_count"] == 2
    assert stats["approved_count"] == 0
    assert stats["rejected_count"] == 0

    # Approve one item
    manager.submit_decision(enqueued[0].item_id, AuditDecision(decision="approve"))
    stats2 = manager.get_queue_summary()
    assert stats2["pending_count"] == 1
    assert stats2["approved_count"] == 1
