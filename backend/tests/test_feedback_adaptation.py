"""Unit & integration tests for Developer Feedback & Prompt Adaptation Engine (Task 4.5)."""

from pathlib import Path
from fastapi.testclient import TestClient

from agentshield.agents import RemediationAgent, SecurityAnalystAgent
from agentshield.api.main import app
from agentshield.api.store import workspace_store
from agentshield.core.feedback import (
    FeedbackCategory,
    FeedbackDecision,
    FeedbackEntry,
    FeedbackPromptAdaptor,
    FeedbackStore,
)
from agentshield.core.schemas import (
    AgentShieldWorkspace,
    CloudProvider,
    IaCTemplate,
    IaCType,
    PatchDiff,
    RemediationStatus,
    Severity,
    VulnerabilityFinding,
    VulnerabilityReport,
)

client = TestClient(app)


def test_feedback_store_crud(tmp_path: Path):
    store_file = tmp_path / "test_feedback.json"
    store = FeedbackStore(storage_path=store_file)

    # Initially empty
    assert len(store.list_entries()) == 0

    # Record accept
    entry_accept = FeedbackEntry(
        workspace_id="ws-1",
        patch_id="p-1",
        finding_id="f-1",
        rule_id="CKV_AWS_20",
        resource_type="aws_s3_bucket",
        decision=FeedbackDecision.ACCEPT,
        category=FeedbackCategory.TRUE_POSITIVE_APPROVED,
        reason="Good security fix for private S3",
        original_code='acl = "public-read"',
        patched_code='acl = "private"',
        reviewer="alice@corp.com",
    )
    store.record_feedback(entry_accept)

    # Record reject
    entry_reject = FeedbackEntry(
        workspace_id="ws-1",
        patch_id="p-2",
        finding_id="f-2",
        rule_id="CKV_AWS_20",
        resource_type="aws_s3_bucket",
        decision=FeedbackDecision.REJECT,
        category=FeedbackCategory.INTENDED_BEHAVIOR,
        reason="Website bucket must be public for hosting",
        original_code='acl = "public-read"',
        patched_code='acl = "private"',
        reviewer="bob@corp.com",
    )
    store.record_feedback(entry_reject)

    # Query
    all_entries = store.list_entries()
    assert len(all_entries) == 2

    positives = store.get_positive_exemplars(rule_id="CKV_AWS_20")
    assert len(positives) == 1
    assert positives[0].decision == FeedbackDecision.ACCEPT

    negatives = store.get_negative_exemplars(rule_id="CKV_AWS_20")
    assert len(negatives) == 1
    assert negatives[0].decision == FeedbackDecision.REJECT

    # Stats
    stats = store.get_stats()
    assert stats["total_feedback"] == 2
    assert stats["accepted_patches"] == 1
    assert stats["rejected_patches"] == 1
    assert stats["acceptance_rate"] == 0.5


def test_prompt_adaptor_generates_context(tmp_path: Path):
    store = FeedbackStore(storage_path=tmp_path / "test_feedback.json")
    adaptor = FeedbackPromptAdaptor(store=store)

    # Empty store -> empty prompts
    assert adaptor.build_analyst_negative_shot_prompt() == ""
    assert adaptor.build_remediation_few_shot_prompt() == ""

    # Add rejection
    store.record_feedback(
        FeedbackEntry(
            workspace_id="ws-1",
            patch_id="p-1",
            finding_id="f-1",
            rule_id="CKV_AWS_260",
            resource_type="aws_security_group",
            decision=FeedbackDecision.REJECT,
            category=FeedbackCategory.INTENDED_BEHAVIOR,
            reason="Bastion host requires ingress 0.0.0.0/0 on port 22",
            original_code='cidr_blocks = ["0.0.0.0/0"]',
        )
    )

    analyst_prompt = adaptor.build_analyst_negative_shot_prompt(rule_ids=["CKV_AWS_260"])
    assert "FALSE POSITIVE SUPPRESSION RULES" in analyst_prompt
    assert "CKV_AWS_260" in analyst_prompt
    assert "Bastion host requires ingress" in analyst_prompt

    # Add acceptance
    store.record_feedback(
        FeedbackEntry(
            workspace_id="ws-1",
            patch_id="p-2",
            finding_id="f-2",
            rule_id="CKV_AWS_20",
            decision=FeedbackDecision.ACCEPT,
            reason="Follow standard bucket block",
            original_code='acl = "public-read"',
            patched_code='acl = "private"',
        )
    )

    remed_prompt = adaptor.build_remediation_few_shot_prompt(rule_id="CKV_AWS_20")
    assert "APPROVED TEAM REMEDIATION EXAMPLES" in remed_prompt
    assert "CKV_AWS_20" in remed_prompt
    assert "--- Original:" in remed_prompt
    assert "+++ Patched:" in remed_prompt


def test_api_patch_decision_records_feedback(tmp_path: Path):
    template = IaCTemplate(
        file_path="main.tf",
        raw_content='resource "aws_s3_bucket" "b" { acl = "public-read" }',
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )
    finding = VulnerabilityFinding(
        finding_id="find-feedback-1",
        rule_id="CKV_AWS_20",
        title="Public S3 bucket",
        description="Public S3 bucket detected",
        severity=Severity.HIGH,
        affected_resource="aws_s3_bucket.b",
    )
    report = VulnerabilityReport(
        template_id=template.template_id,
        target_file="main.tf",
        findings=[finding],
    )
    patch = PatchDiff(
        patch_id="patch-feedback-1",
        finding_id="find-feedback-1",
        target_file="main.tf",
        target_resource="aws_s3_bucket.b",
        original_code='acl = "public-read"',
        patched_code='acl = "private"',
        remediation_status=RemediationStatus.PENDING,
    )
    ws = AgentShieldWorkspace(
        template=template,
        report=report,
        patches=[patch],
    )
    workspace_store.save(ws)

    # Post developer decision via API
    resp = client.post(
        f"/api/workspaces/{ws.workspace_id}/patches/{patch.patch_id}/decision",
        json={
            "decision": "accept",
            "category": "TRUE_POSITIVE_APPROVED",
            "reason": "Applied company security standard",
            "reviewer": "charlie@security.team",
        },
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["remediation_status"] == "APPLIED"

    # Verify feedback list API
    list_resp = client.get("/api/feedback")
    assert list_resp.status_code == 200
    entries = list_resp.json()
    assert any(e["patch_id"] == "patch-feedback-1" for e in entries)

    # Verify feedback stats API
    stats_resp = client.get("/api/feedback/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["accepted_patches"] >= 1
