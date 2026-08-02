"""Integration tests for the Member 4 API layer (scan -> workspace -> export)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agentshield.api.main import app
from agentshield.api.store import workspace_store

FIXTURE = Path(__file__).parent / "fixtures" / "terraform" / "sample.tf"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clean_store():
    """Isolate each test's workspaces from leftovers written to disk by other tests."""
    yield
    for ws in list(workspace_store.list_all()):
        workspace_store.delete(ws.workspace_id)


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_scan_terraform_file_returns_workspace(client: TestClient) -> None:
    with FIXTURE.open("rb") as f:
        resp = client.post("/api/scan", files={"file": ("sample.tf", f, "text/plain")})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "REMEDIATED"
    assert body["template"]["iac_type"] == "terraform"
    assert body["report"] is not None
    # The fixture contains 0.0.0.0/0 ingress, so at least one finding is expected
    # via the heuristic fallback path when no real LLM key is configured.
    assert body["report"]["summary"]["total_vulnerabilities"] >= 1


def test_scan_rejects_empty_file(client: TestClient) -> None:
    resp = client.post("/api/scan", files={"file": ("empty.tf", b"", "text/plain")})
    assert resp.status_code == 400


def test_get_workspace_after_scan(client: TestClient) -> None:
    with FIXTURE.open("rb") as f:
        scan_resp = client.post("/api/scan", files={"file": ("sample.tf", f, "text/plain")})
    workspace_id = scan_resp.json()["workspace_id"]

    get_resp = client.get(f"/api/workspaces/{workspace_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["workspace_id"] == workspace_id


def test_get_unknown_workspace_404(client: TestClient) -> None:
    resp = client.get("/api/workspaces/does-not-exist")
    assert resp.status_code == 404


def test_list_workspaces(client: TestClient) -> None:
    with FIXTURE.open("rb") as f:
        client.post("/api/scan", files={"file": ("sample.tf", f, "text/plain")})

    resp = client.get("/api/workspaces")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.parametrize("fmt", ["json", "markdown", "html", "sarif", "pdf"])
def test_export_formats(client: TestClient, fmt: str) -> None:
    with FIXTURE.open("rb") as f:
        scan_resp = client.post("/api/scan", files={"file": ("sample.tf", f, "text/plain")})
    workspace_id = scan_resp.json()["workspace_id"]

    resp = client.get(f"/api/workspaces/{workspace_id}/export/{fmt}")
    assert resp.status_code == 200
    assert len(resp.content) > 0


def test_export_unsupported_format_400(client: TestClient) -> None:
    with FIXTURE.open("rb") as f:
        scan_resp = client.post("/api/scan", files={"file": ("sample.tf", f, "text/plain")})
    workspace_id = scan_resp.json()["workspace_id"]

    resp = client.get(f"/api/workspaces/{workspace_id}/export/xml")
    assert resp.status_code == 400


def test_patch_decision_accept(client: TestClient) -> None:
    with FIXTURE.open("rb") as f:
        scan_resp = client.post("/api/scan", files={"file": ("sample.tf", f, "text/plain")})
    body = scan_resp.json()
    workspace_id = body["workspace_id"]
    if not body["patches"]:
        pytest.skip("No patches generated for this fixture in the current heuristic path.")
    patch_id = body["patches"][0]["patch_id"]

    resp = client.post(
        f"/api/workspaces/{workspace_id}/patches/{patch_id}/decision",
        json={"decision": "accept"},
    )
    assert resp.status_code == 200
    assert resp.json()["remediation_status"] == "APPLIED"
