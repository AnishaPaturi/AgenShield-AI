"""Unit & integration tests for Live Cloud Drift Detection Engine (Task 5.2)."""

from fastapi.testclient import TestClient

from agentshield.api.main import app
from agentshield.api.store import workspace_store
from agentshield.core.drift import (
    AWSCloudMonitor,
    DriftDetector,
    DriftSeverity,
    DriftType,
)
from agentshield.core.schemas import (
    AgentShieldWorkspace,
    CloudProvider,
    IaCTemplate,
    IaCType,
)

client = TestClient(app)


def test_drift_detector_security_group_out_of_band_ingress():
    raw_tf = """
resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "Web security group"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}
"""
    template = IaCTemplate(
        file_path="main.tf",
        raw_content=raw_tf,
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )

    # In live cloud, port 22 with 0.0.0.0/0 was added out-of-band!
    monitor = AWSCloudMonitor()
    monitor.set_mock_resource_state(
        "aws_security_group.web_sg",
        {
            "name": "web_sg",
            "ingress": [
                {
                    "from_port": 80,
                    "to_port": 80,
                    "protocol": "tcp",
                    "cidr_blocks": ["10.0.0.0/16"],
                },
                {
                    "from_port": 22,
                    "to_port": 22,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"],
                },
            ],
        },
    )

    detector = DriftDetector(monitors={CloudProvider.AWS: monitor})
    report = detector.detect_drift(template)

    assert report.total_drifts >= 1
    assert report.critical_count >= 1
    assert report.status == "CRITICAL_DRIFT"

    sg_drift = next((d for d in report.drifts if "ingress" in d.attribute_path), None)
    assert sg_drift is not None
    assert sg_drift.drift_type == DriftType.OUT_OF_BAND_ADDITION
    assert sg_drift.severity == DriftSeverity.CRITICAL
    assert "0.0.0.0/0" in sg_drift.actual_live_value


def test_drift_detector_s3_acl_degradation():
    raw_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-data-lake"
  acl    = "private"
}
"""
    template = IaCTemplate(
        file_path="main.tf",
        raw_content=raw_tf,
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )

    monitor = AWSCloudMonitor()
    monitor.set_mock_resource_state(
        "aws_s3_bucket.data_bucket",
        {
            "bucket": "data_bucket",
            "acl": "public-read",
            "block_public_acls": False,
        },
    )

    detector = DriftDetector(monitors={CloudProvider.AWS: monitor})
    report = detector.detect_drift(template)

    assert report.total_drifts == 1
    d = report.drifts[0]
    assert d.drift_type == DriftType.SECURITY_DEGRADATION
    assert d.severity == DriftSeverity.HIGH
    assert d.actual_live_value == "public-read"
    assert d.expected_iac_value == "private"


def test_drift_detector_in_sync():
    raw_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-data-lake"
  acl    = "private"
}
"""
    template = IaCTemplate(
        file_path="main.tf",
        raw_content=raw_tf,
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )

    monitor = AWSCloudMonitor()
    monitor.set_mock_resource_state(
        "aws_s3_bucket.data_bucket",
        {
            "bucket": "data_bucket",
            "acl": "private",
            "block_public_acls": True,
        },
    )

    detector = DriftDetector(monitors={CloudProvider.AWS: monitor})
    report = detector.detect_drift(template)

    assert report.total_drifts == 0
    assert report.status == "IN_SYNC"


def test_api_drift_scan_and_get():
    template = IaCTemplate(
        file_path="main.tf",
        raw_content='resource "aws_s3_bucket" "b" { bucket = "b"; acl = "private" }',
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )
    ws = AgentShieldWorkspace(template=template)
    workspace_store.save(ws)

    # Scan drift
    resp = client.post(f"/api/workspaces/{ws.workspace_id}/drift/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "total_drifts" in data

    # Get drift
    get_resp = client.get(f"/api/workspaces/{ws.workspace_id}/drift")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["report_id"] == data["report_id"]
