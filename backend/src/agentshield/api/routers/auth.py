"""FastAPI router for User Authentication and Password Reset."""

from __future__ import annotations

import logging
import os
import secrets
import urllib.parse
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import httpx

from agentshield.api.store import workspace_store
from agentshield.api.mailer import send_verification_email

logger = logging.getLogger("agentshield.api.routers.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "").strip()
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "").strip()
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/auth/github/callback").strip()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback").strip()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").strip()


class VerifyEmailRequest(BaseModel):
    email: EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = ""
    org_name: str = ""
    providers: str = "email"


class SendCodeRequest(BaseModel):
    email: EmailStr


class SendCodeResponse(BaseModel):
    success: bool
    message: str
    email_sent: bool


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    code: str | None = None


class AuthResponse(BaseModel):
    success: bool
    message: str


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest) -> AuthResponse:
    """Register or synchronize a user account in the SQLite database."""
    clean_email = req.email.strip().lower()
    workspace_store.save_user(
        email=clean_email,
        name=req.name.strip(),
        password=req.password,
        org_name=req.org_name.strip(),
        providers=req.providers.strip(),
    )
    logger.info("User registered/synced in SQLite database: %s", clean_email)
    return AuthResponse(success=True, message=f"User {clean_email} saved in database.")


@router.post("/verify-email", response_model=AuthResponse)
def verify_email(req: VerifyEmailRequest) -> AuthResponse:
    """Check if an email is registered in the database."""
    clean_email = req.email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        return AuthResponse(success=False, message="No account found with this email address.")
    return AuthResponse(success=True, message="Account found.")


@router.post("/send-code", response_model=SendCodeResponse)
def send_code(req: SendCodeRequest) -> SendCodeResponse:
    """
    Generate a 6-digit verification code, store it with an expiry timestamp,
    and dispatch an email from agentsheildai@gmail.com to the user's email address.
    If the user does not exist in the database yet, provision an account for them.
    """
    clean_email = req.email.strip().lower()

    # Ensure user exists in SQLite database; auto-provision if needed
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        name_part = clean_email.split("@")[0].replace(".", " ").replace("-", " ").replace("_", " ").title()
        workspace_store.save_user(
            email=clean_email,
            name=name_part or "AgentShield User",
            password="",
            org_name="AgentShield Security",
            providers="email",
        )
        logger.info("Auto-provisioned user record for %s in SQLite database", clean_email)

    # Generate a cryptographically secure 6-digit code
    code = f"{secrets.randbelow(900000) + 100000}"

    # Store code with 10-minute expiry (600 seconds)
    workspace_store.save_verification_code(clean_email, code, ttl_seconds=600)

    # Attempt to send via SMTP from agentsheildai@gmail.com
    email_sent, mail_msg = send_verification_email(to_email=clean_email, code=code)

    if not email_sent:
        logger.error("Failed to send verification email to %s: %s", clean_email, mail_msg)
        raise HTTPException(
            status_code=502,
            detail=f"Unable to dispatch verification email: {mail_msg}. Please check email configuration.",
        )

    logger.info("Verification code emailed to %s from agentsheildai@gmail.com", clean_email)
    return SendCodeResponse(
        success=True,
        email_sent=True,
        message=f"Verification code sent from agentsheildai@gmail.com to {clean_email}.",
    )



@router.post("/verify-code", response_model=AuthResponse)
def verify_code(req: VerifyCodeRequest) -> AuthResponse:
    """Verify if a code submitted by the user matches and has not expired."""
    clean_email = req.email.strip().lower()
    is_valid = workspace_store.verify_code(clean_email, req.code)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code. Please request a new code.",
        )
    return AuthResponse(success=True, message="Verification code confirmed.")


@router.post("/reset-password", response_model=AuthResponse)
def reset_password(req: ResetPasswordRequest) -> AuthResponse:
    """Update a user's password in the database."""
    if len(req.new_password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters long."
        )

    clean_email = req.email.strip().lower()

    # If code is provided, verify it
    if req.code:
        is_valid = workspace_store.verify_code(clean_email, req.code)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification code.",
            )

    updated = workspace_store.update_user_password(clean_email, req.new_password)
    if not updated:
        # Create or update user with new password
        name_part = clean_email.split("@")[0].replace(".", " ").replace("-", " ").replace("_", " ").title()
        workspace_store.save_user(
            email=clean_email,
            name=name_part or "AgentShield User",
            password=req.new_password,
            org_name="AgentShield Security",
            providers="email",
        )

    # Invalidate the verification code after successful password change
    workspace_store.clear_verification_code(clean_email)

    logger.info("Password successfully updated in SQLite database for %s", clean_email)
    return AuthResponse(success=True, message="Password updated successfully in database.")


# ==========================================
# Real GitHub OAuth 2.0 Endpoints
# ==========================================

@router.get("/github/status")
def get_github_status() -> dict:
    """Return whether real GitHub OAuth is configured in the environment."""
    return {
        "configured": bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET),
        "client_id": f"{GITHUB_CLIENT_ID[:6]}..." if GITHUB_CLIENT_ID else None,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }


@router.get("/github/login")
def github_login(state: str | None = None):
    """
    Redirect the user to GitHub's real OAuth 2.0 authorization page.
    Requires GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET configured in .env.
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in backend/.env",
        )

    oauth_state = state or secrets.token_urlsafe(16)
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
        "state": oauth_state,
        "allow_signup": "true",
    }
    github_auth_url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    logger.info("Redirecting user to GitHub OAuth: %s", github_auth_url)
    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback")
async def github_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    """
    Handle GitHub OAuth 2.0 callback:
    1. Exchange authorization code for access token.
    2. Fetch user profile and verified email from GitHub API.
    3. Register or update the user in the SQLite database.
    4. Redirect the browser to the AgentShield frontend console.
    """
    if error:
        err_msg = error_description or error or "GitHub authentication failed"
        logger.error("GitHub OAuth error from provider: %s", err_msg)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote(err_msg)}"
        )

    if not code:
        logger.error("No authorization code provided in GitHub OAuth callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote('Missing authorization code from GitHub.')}"
        )

    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        logger.error("GitHub OAuth credentials not configured on callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote('GitHub OAuth credentials are not configured on the server.')}"
        )

    token_url = "https://github.com/login/oauth/access_token"
    token_payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }
    headers = {"Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(token_url, json=token_payload, headers=headers)
            if token_resp.status_code != 200:
                logger.error("Failed to exchange code with GitHub: %s", token_resp.text)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote('Failed to exchange code with GitHub.')}"
                )

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                err_desc = token_data.get("error_description", "No access token received from GitHub.")
                logger.error("GitHub token error: %s", err_desc)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote(err_desc)}"
                )

            # Fetch user profile
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                    "User-Agent": "AgentShield-AI",
                },
            )
            if user_resp.status_code != 200:
                logger.error("Failed to fetch user profile from GitHub: %s", user_resp.text)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote('Failed to fetch user profile from GitHub.')}"
                )

            user_data = user_resp.json()
            login = user_data.get("login") or "github_user"
            name = user_data.get("name") or login
            email = user_data.get("email")

            # If user email is private, fetch primary verified email from /user/emails
            if not email:
                emails_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                        "User-Agent": "AgentShield-AI",
                    },
                )
                if emails_resp.status_code == 200:
                    emails_data = emails_resp.json()
                    for item in emails_data:
                        if item.get("primary") and item.get("verified"):
                            email = item.get("email")
                            break
                    if not email and emails_data:
                        email = emails_data[0].get("email")

            if not email:
                email = f"{login}@users.noreply.github.com"

            clean_email = email.strip().lower()

            # Provision or update user in SQLite database
            workspace_store.save_user(
                email=clean_email,
                name=name,
                password="",
                org_name=f"{login} (GitHub)",
                providers="github",
            )
            logger.info("GitHub user successfully authenticated & saved: %s (%s)", clean_email, login)

            # Redirect user to the frontend console with auth params
            redirect_params = urllib.parse.urlencode({
                "github_auth": "success",
                "email": clean_email,
                "name": name,
                "login": login,
                "provider": "github",
            })
            return RedirectResponse(url=f"{FRONTEND_URL}/console?{redirect_params}")

    except Exception as exc:
        logger.exception("Unexpected error during GitHub OAuth callback: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?github_error={urllib.parse.quote(str(exc))}"
        )


# ==========================================
# Real Google OAuth 2.0 Endpoints
# ==========================================

@router.get("/google/status")
def get_google_status() -> dict:
    """Return whether real Google OAuth is configured in the environment."""
    return {
        "configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        "client_id": f"{GOOGLE_CLIENT_ID[:6]}..." if GOOGLE_CLIENT_ID else None,
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }


@router.get("/google/login")
def google_login(state: str | None = None):
    """
    Redirect the user to Google's real OAuth 2.0 authorization page.
    Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET configured in .env.
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env",
        )

    oauth_state = state or secrets.token_urlsafe(16)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": oauth_state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    logger.info("Redirecting user to Google OAuth: %s", google_auth_url)
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    """
    Handle Google OAuth 2.0 callback:
    1. Exchange authorization code for access token via https://oauth2.googleapis.com/token.
    2. Fetch user profile and email from https://www.googleapis.com/oauth2/v3/userinfo.
    3. Register or update the user in the SQLite database.
    4. Redirect the browser to the AgentShield frontend console.
    """
    if error:
        err_msg = error_description or error or "Google authentication failed"
        logger.error("Google OAuth error from provider: %s", err_msg)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote(err_msg)}"
        )

    if not code:
        logger.error("No authorization code provided in Google OAuth callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote('Missing authorization code from Google.')}"
        )

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        logger.error("Google OAuth credentials not configured on callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote('Google OAuth credentials are not configured on the server.')}"
        )

    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }
    headers = {"Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(token_url, data=token_payload, headers=headers)
            if token_resp.status_code != 200:
                logger.error("Failed to exchange code with Google: %s", token_resp.text)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote('Failed to exchange code with Google.')}"
                )

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                err_desc = token_data.get("error_description", "No access token received from Google.")
                logger.error("Google token error: %s", err_desc)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote(err_desc)}"
                )

            # Fetch user profile from Google UserInfo endpoint
            user_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_resp.status_code != 200:
                logger.error("Failed to fetch user profile from Google: %s", user_resp.text)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote('Failed to fetch user profile from Google.')}"
                )

            user_data = user_resp.json()
            email = user_data.get("email")
            name = user_data.get("name") or user_data.get("given_name") or "Google User"
            picture = user_data.get("picture", "")

            if not email:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote('No email associated with this Google account.')}"
                )

            clean_email = email.strip().lower()

            # Provision or update user in SQLite database
            workspace_store.save_user(
                email=clean_email,
                name=name,
                password="",
                org_name="Google Account",
                providers="google",
            )
            logger.info("Google user successfully authenticated & saved: %s (%s)", clean_email, name)

            # Redirect user to the frontend console with auth params
            redirect_params = urllib.parse.urlencode({
                "google_auth": "success",
                "email": clean_email,
                "name": name,
                "provider": "google",
                "picture": picture,
            })
            return RedirectResponse(url=f"{FRONTEND_URL}/console?{redirect_params}")

    except Exception as exc:
        logger.exception("Unexpected error during Google OAuth callback: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?google_error={urllib.parse.quote(str(exc))}"
        )


