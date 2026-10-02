"""Integration tests for Auth, Profile, and Account Security API endpoints."""

import uuid

import pytest
from fastapi.testclient import TestClient

from agentshield.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_register_and_login_flow(client: TestClient) -> None:
    # 1. Register a new user
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Security",
            "email": "jane@shieldsecurity.io",
            "password": "SecurePassword123!",
            "org_name": "Shield Security Corp",
            "providers": "email",
        },
    )
    assert reg_resp.status_code == 200
    assert reg_resp.json()["success"] is True

    # 2. Login with correct credentials
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "jane@shieldsecurity.io",
            "password": "SecurePassword123!",
        },
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    assert login_data["user"]["name"] == "Jane Security"
    assert login_data["user"]["email"] == "jane@shieldsecurity.io"
    assert "token" in login_data

    # 3. Login with incorrect password fails with 401
    bad_login = client.post(
        "/api/auth/login",
        json={
            "email": "jane@shieldsecurity.io",
            "password": "WrongPassword999!",
        },
    )
    assert bad_login.status_code == 401


def test_profile_and_avatar_management(client: TestClient) -> None:
    email = "jane@shieldsecurity.io"

    # 1. Fetch profile
    prof_resp = client.get(f"/api/auth/profile?email={email}")
    assert prof_resp.status_code == 200
    assert prof_resp.json()["email"] == email

    # 2. Update profile (name, phone, org_name)
    update_resp = client.put(
        "/api/auth/profile",
        json={
            "email": email,
            "name": "Jane Senior Lead",
            "phone": "+1 (555) 987-6543",
            "org_name": "Enterprise Cyber Defense",
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "Jane Senior Lead"
    assert updated["phone"] == "+1 (555) 987-6543"
    assert updated["orgName"] == "Enterprise Cyber Defense"

    # 3. Upload avatar
    fake_avatar = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    av_resp = client.post(
        "/api/auth/avatar",
        json={"email": email, "avatar_data": fake_avatar},
    )
    assert av_resp.status_code == 200
    assert av_resp.json()["success"] is True

    # 4. Remove avatar
    del_resp = client.delete(f"/api/auth/avatar?email={email}")
    assert del_resp.status_code == 200
    assert del_resp.json()["avatar"] == ""


def test_change_password_and_email(client: TestClient) -> None:
    email = "test_pw_change@agentshield.ai"
    client.post(
        "/api/auth/register",
        json={
            "name": "Change User",
            "email": email,
            "password": "Password123!",
            "org_name": "Test Org",
        },
    )

    # 1. Change password
    chg_pw = client.post(
        "/api/auth/change-password",
        json={
            "email": email,
            "current_password": "Password123!",
            "new_password": "NewSecretPassword2026!",
        },
    )
    assert chg_pw.status_code == 200
    assert chg_pw.json()["success"] is True

    # 2. Verify login works with new password
    login_new = client.post(
        "/api/auth/login",
        json={"email": email, "password": "NewSecretPassword2026!"},
    )
    assert login_new.status_code == 200

    # 3. Change email
    new_email = f"test_pw_updated_{uuid.uuid4().hex[:8]}@agentshield.ai"
    chg_em = client.put(
        "/api/auth/change-email",
        json={
            "current_email": email,
            "new_email": new_email,
            "password": "NewSecretPassword2026!",
        },
    )
    assert chg_em.status_code == 200
    assert chg_em.json()["success"] is True


def test_oauth_account_linking_and_provider_merging(client: TestClient) -> None:
    oauth_email = f"oauth_user_{uuid.uuid4().hex[:8]}@example.com"

    # 1. Register/Provision via Google OAuth with no password
    reg_google = client.post(
        "/api/auth/register",
        json={
            "name": "OAuth User",
            "email": oauth_email,
            "password": "",
            "org_name": "Google Org",
            "providers": "google",
        },
    )
    assert reg_google.status_code == 200

    prof_1 = client.get(f"/api/auth/profile?email={oauth_email}").json()
    assert prof_1["hasPassword"] is False
    assert "google" in prof_1["providers"]

    # 2. Same user later signs in / links via GitHub OAuth
    reg_github = client.post(
        "/api/auth/register",
        json={
            "name": "OAuth User GitHub",
            "email": oauth_email,
            "password": "",
            "org_name": "GitHub Org",
            "providers": "github",
        },
    )
    assert reg_github.status_code == 200

    prof_2 = client.get(f"/api/auth/profile?email={oauth_email}").json()
    assert "google" in prof_2["providers"]
    assert "github" in prof_2["providers"]
    assert prof_2["hasPassword"] is False

    # 3. User sets an account password
    reset_pw = client.post(
        "/api/auth/reset-password",
        json={
            "email": oauth_email,
            "new_password": "SecureEnterprisePassword2026!",
        },
    )
    assert reset_pw.status_code == 200

    prof_3 = client.get(f"/api/auth/profile?email={oauth_email}").json()
    assert prof_3["hasPassword"] is True

    # 4. User can now log in with the new password
    login_pw = client.post(
        "/api/auth/login",
        json={
            "email": oauth_email,
            "password": "SecureEnterprisePassword2026!",
        },
    )
    assert login_pw.status_code == 200
    assert login_pw.json()["success"] is True

    # 5. User unlinks Google provider
    unlink_resp = client.post(
        "/api/auth/unlink-provider",
        json={"email": oauth_email, "provider": "google"},
    )
    assert unlink_resp.status_code == 200
    assert "google" not in unlink_resp.json()["user"]["providers"]
    assert "github" in unlink_resp.json()["user"]["providers"]

    # 6. Safety check: create user with ONLY github and NO password
    oauth_single = f"single_oauth_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/register",
        json={
            "name": "Single OAuth",
            "email": oauth_single,
            "password": "",
            "providers": "github",
        },
    )
    # Attempting to unlink their ONLY authentication method must fail with 400
    fail_unlink = client.post(
        "/api/auth/unlink-provider",
        json={"email": oauth_single, "provider": "github"},
    )
    assert fail_unlink.status_code == 400
    assert "only sign-in method" in fail_unlink.json()["detail"]


def test_oauth_status_and_login_endpoints(client: TestClient) -> None:
    # 1. GitHub status endpoint returns structure
    gh_status = client.get("/api/auth/github/status")
    assert gh_status.status_code == 200
    assert "configured" in gh_status.json()

    # 2. Google status endpoint returns structure
    g_status = client.get("/api/auth/google/status")
    assert g_status.status_code == 200
    assert "configured" in g_status.json()


def test_github_oauth_callback_flow(client: TestClient) -> None:
    from unittest.mock import patch
    import httpx

    # Test error returned from GitHub
    err_resp = client.get(
        "/api/auth/github/callback?error=access_denied&error_description=The+user+cancelled",
        follow_redirects=False,
    )
    assert err_resp.status_code == 307
    assert "error=" in err_resp.headers["location"]
    assert "provider=github" in err_resp.headers["location"]

    # Test successful code exchange & user provisioning via mock
    async def mock_post(self, url, *args, **kwargs):
        return httpx.Response(200, json={"access_token": "gho_fake_token_123"}, request=httpx.Request("POST", url))

    async def mock_get(self, url, *args, **kwargs):
        if "user/emails" in str(url):
            return httpx.Response(200, json=[{"email": "gh_developer@example.com", "primary": True, "verified": True}], request=httpx.Request("GET", url))
        return httpx.Response(200, json={"login": "octocat", "name": "Mona Lisa", "email": ""}, request=httpx.Request("GET", url))

    with patch("agentshield.api.routers.auth.GITHUB_CLIENT_ID", "fake_id"), \
         patch("agentshield.api.routers.auth.GITHUB_CLIENT_SECRET", "fake_secret"), \
         patch("httpx.AsyncClient.post", mock_post), \
         patch("httpx.AsyncClient.get", mock_get):
        resp = client.get("/api/auth/github/callback?code=mock_code&state=return_to=%2Fdashboard", follow_redirects=False)
        assert resp.status_code == 307
        assert "auth=success" in resp.headers["location"]
        assert "github_auth=success" in resp.headers["location"]
        assert "gh_developer" in resp.headers["location"]


def test_google_oauth_callback_flow(client: TestClient) -> None:
    from unittest.mock import patch
    import httpx

    # Test error returned from Google
    err_resp = client.get(
        "/api/auth/google/callback?error=access_denied",
        follow_redirects=False,
    )
    assert err_resp.status_code == 307
    assert "error=" in err_resp.headers["location"]
    assert "provider=google" in err_resp.headers["location"]

    # Test successful code exchange & user provisioning via mock
    async def mock_post(self, url, *args, **kwargs):
        return httpx.Response(200, json={"access_token": "ya29_fake_token_123"}, request=httpx.Request("POST", url))

    async def mock_get(self, url, *args, **kwargs):
        return httpx.Response(200, json={"email": "google_user@example.com", "name": "Google Lead", "picture": "https://example.com/pic.png"}, request=httpx.Request("GET", url))

    with patch("agentshield.api.routers.auth.GOOGLE_CLIENT_ID", "fake_id"), \
         patch("agentshield.api.routers.auth.GOOGLE_CLIENT_SECRET", "fake_secret"), \
         patch("httpx.AsyncClient.post", mock_post), \
         patch("httpx.AsyncClient.get", mock_get):
        resp = client.get("/api/auth/google/callback?code=mock_code&state=return_to=%2Fdashboard", follow_redirects=False)
        assert resp.status_code == 307
        assert "auth=success" in resp.headers["location"]
        assert "google_auth=success" in resp.headers["location"]
        assert "google_user" in resp.headers["location"]

