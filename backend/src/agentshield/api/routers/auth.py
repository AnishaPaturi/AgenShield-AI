"""FastAPI router for User Authentication and Password Reset."""

from __future__ import annotations

import logging
import os
import secrets
from typing import Any
import urllib.parse
from pydantic import BaseModel
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
    email: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str = ""
    org_name: str = ""
    providers: str = "email"


class SendCodeRequest(BaseModel):
    email: str


class SendCodeResponse(BaseModel):
    success: bool
    message: str
    email_sent: bool


class VerifyCodeRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str
    code: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    user: dict[str, Any] | None = None
    token: str = ""


class ProfileUpdateRequest(BaseModel):
    email: str
    name: str | None = None
    phone: str | None = None
    org_name: str | None = None
    avatar: str | None = None


class ChangeEmailRequest(BaseModel):
    current_email: str
    new_email: str
    password: str


class ChangePasswordRequest(BaseModel):
    email: str
    current_password: str
    new_password: str


class AvatarUploadRequest(BaseModel):
    email: str
    avatar_data: str


class UnlinkProviderRequest(BaseModel):
    email: str
    provider: str


class OAuthExchangeRequest(BaseModel):
    code: str
    redirect_uri: str | None = None
    state: str | None = None


class AuthResponse(BaseModel):
    success: bool
    message: str


def _sanitize_user(user: dict[str, Any]) -> dict[str, Any]:
    """Helper to return sanitized user dictionary without plain password."""
    providers_list = (user.get("providers") or "email").split(",")
    return {
        "id": user.get("user_id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "phone": user.get("phone") or "",
        "avatar": user.get("avatar") or "",
        "orgName": user.get("org_name") or "",
        "providers": [p.strip() for p in providers_list if p.strip()],
        "hasPassword": bool(user.get("password") and user.get("password").strip()),
        "createdAt": user.get("created_at"),
        "updatedAt": user.get("updated_at"),
    }


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> LoginResponse:
    """Authenticate user with email and password from SQLite database."""
    clean_email = req.email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="No account found with this email address. Please sign up first.",
        )

    if user.get("password") != req.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password. Please verify your credentials.",
        )

    token = f"as-token-{secrets.token_hex(24)}"
    logger.info("User authenticated successfully: %s", clean_email)
    return LoginResponse(
        success=True,
        message="Authentication successful.",
        user=_sanitize_user(user),
        token=token,
    )


@router.get("/profile")
def get_profile(email: str) -> dict[str, Any]:
    """Retrieve user profile from SQLite database."""
    clean_email = email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
    return _sanitize_user(user)


@router.put("/profile")
def update_profile(req: ProfileUpdateRequest) -> dict[str, Any]:
    """Update profile fields (name, phone, org_name, avatar) in database."""
    clean_email = req.email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    updated = workspace_store.update_user_profile(
        email=clean_email,
        name=req.name,
        phone=req.phone,
        org_name=req.org_name,
        avatar=req.avatar,
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update profile.")
    return _sanitize_user(updated)


@router.put("/change-email", response_model=AuthResponse)
def change_email(req: ChangeEmailRequest) -> AuthResponse:
    """Change user email address after password validation."""
    clean_current = req.current_email.strip().lower()
    clean_new = req.new_email.strip().lower()

    if clean_current == clean_new:
        raise HTTPException(status_code=400, detail="New email cannot be identical to current email.")

    user = workspace_store.get_user_by_email(clean_current)
    if not user:
        raise HTTPException(status_code=404, detail="Current account not found.")

    if user.get("password") and user.get("password") != req.password:
        raise HTTPException(status_code=401, detail="Incorrect password. Verification required.")

    # Check if new email is already taken
    existing = workspace_store.get_user_by_email(clean_new)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this new email already exists.")

    ok = workspace_store.update_user_email(clean_current, clean_new)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update email address.")

    logger.info("User changed email from %s to %s", clean_current, clean_new)
    return AuthResponse(success=True, message=f"Email successfully updated to {clean_new}.")


@router.post("/change-password", response_model=AuthResponse)
def change_password(req: ChangePasswordRequest) -> AuthResponse:
    """Change user password after verifying current password."""
    clean_email = req.email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    if user.get("password") and user.get("password") != req.current_password:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long.")

    ok = workspace_store.update_user_password(clean_email, req.new_password)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update password.")

    logger.info("Password changed successfully for %s", clean_email)
    return AuthResponse(success=True, message="Password updated successfully.")


@router.post("/avatar")
def upload_avatar(req: AvatarUploadRequest) -> dict[str, Any]:
    """Upload or update profile avatar image for user."""
    clean_email = req.email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    # Basic size check: reject base64 payloads larger than ~2MB
    if len(req.avatar_data) > 3 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Avatar image exceeds 2MB limit.")

    updated = workspace_store.update_user_profile(email=clean_email, avatar=req.avatar_data)
    return {"success": True, "avatar": updated.get("avatar") if updated else ""}


@router.delete("/avatar")
def remove_avatar(email: str) -> dict[str, Any]:
    """Remove avatar image for user."""
    clean_email = email.strip().lower()
    user = workspace_store.get_user_by_email(clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    updated = workspace_store.update_user_profile(email=clean_email, avatar="")
    return {"success": True, "avatar": ""}


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


@router.post("/unlink-provider")
def unlink_provider(req: UnlinkProviderRequest) -> dict[str, Any]:
    """Unlink an authentication provider from a user account."""
    clean_email = req.email.strip().lower()
    clean_provider = req.provider.strip().lower()
    try:
        updated = workspace_store.unlink_user_provider(clean_email, clean_provider)
        return {
            "success": True,
            "user": _sanitize_user(updated),
            "message": f"{req.provider.title()} unlinked successfully.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
def github_login(
    state: str | None = None,
    return_to: str | None = None,
    link_email: str | None = None,
):
    """
    Redirect the user to GitHub's real OAuth 2.0 authorization page.
    Requires GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET configured in .env.
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in backend/.env",
        )

    state_parts = []
    if state:
        state_parts.append(f"state={urllib.parse.quote(state)}")
    if return_to:
        state_parts.append(f"return_to={urllib.parse.quote(return_to)}")
    if link_email:
        state_parts.append(f"link_email={urllib.parse.quote(link_email)}")
    oauth_state = "&".join(state_parts) if state_parts else secrets.token_urlsafe(16)

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
    4. Redirect the browser to the AgentShield frontend.
    """
    return_to = "/dashboard"
    link_email = None
    if state:
        try:
            parsed_state = urllib.parse.parse_qs(state)
            if "return_to" in parsed_state:
                return_to = parsed_state["return_to"][0]
            if "link_email" in parsed_state:
                link_email = parsed_state["link_email"][0]
        except Exception:
            pass

    if error:
        err_msg = error_description or error or "GitHub authentication failed"
        logger.error("GitHub OAuth error from provider: %s", err_msg)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote(err_msg)}&provider=github"
        )

    if not code:
        logger.error("No authorization code provided in GitHub OAuth callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Missing authorization code from GitHub.')}&provider=github"
        )

    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        logger.error("GitHub OAuth credentials not configured on callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('GitHub OAuth credentials are not configured on the server.')}&provider=github"
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
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Failed to exchange code with GitHub.')}&provider=github"
                )

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                err_desc = token_data.get("error_description", "No access token received from GitHub.")
                logger.error("GitHub token error: %s", err_desc)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote(err_desc)}&provider=github"
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
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Failed to fetch user profile from GitHub.')}&provider=github"
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
            target_email = link_email.strip().lower() if link_email and link_email.strip() else clean_email

            # Provision or update user in SQLite database with merged providers
            user = workspace_store.save_user(
                email=target_email,
                name=name,
                password="",
                org_name=f"{login} (GitHub)",
                providers="github",
            )
            logger.info("GitHub user successfully authenticated & saved: %s (%s)", target_email, login)

            # Redirect user to the frontend callback handler with auth params
            redirect_params = urllib.parse.urlencode({
                "auth": "success",
                "github_auth": "success",
                "email": target_email,
                "name": user.get("name") or name,
                "login": login,
                "provider": "github",
                "return_to": return_to,
            })
            return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?{redirect_params}")

    except Exception as exc:
        logger.exception("Unexpected error during GitHub OAuth callback: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote(str(exc))}&provider=github"
        )


@router.post("/github/exchange")
async def exchange_github_code(req: OAuthExchangeRequest) -> dict[str, Any]:
    """Client-side code exchange endpoint for GitHub OAuth."""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="GitHub OAuth credentials not configured on the server.",
        )

    redirect_uri = req.redirect_uri or GITHUB_REDIRECT_URI
    token_url = "https://github.com/login/oauth/access_token"
    token_payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": req.code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(token_url, json=token_payload, headers=headers)
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code with GitHub.")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            err_desc = token_data.get("error_description", "No access token received from GitHub.")
            raise HTTPException(status_code=400, detail=err_desc)

        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "User-Agent": "AgentShield-AI",
            },
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user profile from GitHub.")

        user_data = user_resp.json()
        login = user_data.get("login") or "github_user"
        name = user_data.get("name") or login
        email = user_data.get("email")

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
                for item in emails_resp.json():
                    if item.get("primary") and item.get("verified"):
                        email = item.get("email")
                        break
        if not email:
            email = f"{login}@users.noreply.github.com"

        user = workspace_store.save_user(
            email=email.strip().lower(),
            name=name,
            password="",
            org_name=f"{login} (GitHub)",
            providers="github",
        )
        return {"success": True, "user": _sanitize_user(user)}


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
def google_login(
    state: str | None = None,
    return_to: str | None = None,
    link_email: str | None = None,
):
    """
    Redirect the user to Google's real OAuth 2.0 authorization page.
    Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET configured in .env.
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env",
        )

    state_parts = []
    if state:
        state_parts.append(f"state={urllib.parse.quote(state)}")
    if return_to:
        state_parts.append(f"return_to={urllib.parse.quote(return_to)}")
    if link_email:
        state_parts.append(f"link_email={urllib.parse.quote(link_email)}")
    oauth_state = "&".join(state_parts) if state_parts else secrets.token_urlsafe(16)

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
    4. Redirect the browser to the AgentShield frontend.
    """
    return_to = "/dashboard"
    link_email = None
    if state:
        try:
            parsed_state = urllib.parse.parse_qs(state)
            if "return_to" in parsed_state:
                return_to = parsed_state["return_to"][0]
            if "link_email" in parsed_state:
                link_email = parsed_state["link_email"][0]
        except Exception:
            pass

    if error:
        err_msg = error_description or error or "Google authentication failed"
        logger.error("Google OAuth error from provider: %s", err_msg)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote(err_msg)}&provider=google"
        )

    if not code:
        logger.error("No authorization code provided in Google OAuth callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Missing authorization code from Google.')}&provider=google"
        )

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        logger.error("Google OAuth credentials not configured on callback")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Google OAuth credentials are not configured on the server.')}&provider=google"
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
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Failed to exchange code with Google.')}&provider=google"
                )

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                err_desc = token_data.get("error_description", "No access token received from Google.")
                logger.error("Google token error: %s", err_desc)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote(err_desc)}&provider=google"
                )

            # Fetch user profile from Google UserInfo endpoint
            user_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_resp.status_code != 200:
                logger.error("Failed to fetch user profile from Google: %s", user_resp.text)
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('Failed to fetch user profile from Google.')}&provider=google"
                )

            user_data = user_resp.json()
            email = user_data.get("email")
            name = user_data.get("name") or user_data.get("given_name") or "Google User"
            picture = user_data.get("picture", "")

            if not email:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote('No email associated with this Google account.')}&provider=google"
                )

            clean_email = email.strip().lower()
            target_email = link_email.strip().lower() if link_email and link_email.strip() else clean_email

            # Provision or update user in SQLite database with merged providers
            user = workspace_store.save_user(
                email=target_email,
                name=name,
                password="",
                org_name="Google Account",
                avatar=picture,
                providers="google",
            )
            logger.info("Google user successfully authenticated & saved: %s (%s)", target_email, name)

            # Redirect user to the frontend callback handler with auth params
            redirect_params = urllib.parse.urlencode({
                "auth": "success",
                "google_auth": "success",
                "email": target_email,
                "name": user.get("name") or name,
                "provider": "google",
                "picture": picture or (user.get("avatar") or ""),
                "return_to": return_to,
            })
            return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?{redirect_params}")

    except Exception as exc:
        logger.exception("Unexpected error during Google OAuth callback: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error={urllib.parse.quote(str(exc))}&provider=google"
        )


@router.post("/google/exchange")
async def exchange_google_code(req: OAuthExchangeRequest) -> dict[str, Any]:
    """Client-side code exchange endpoint for Google OAuth."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth credentials not configured on the server.",
        )

    redirect_uri = req.redirect_uri or GOOGLE_REDIRECT_URI
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": req.code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(token_url, data=token_payload, headers=headers)
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code with Google.")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            err_desc = token_data.get("error_description", "No access token received from Google.")
            raise HTTPException(status_code=400, detail=err_desc)

        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user profile from Google.")

        user_data = user_resp.json()
        email = user_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="No email associated with Google account.")
        name = user_data.get("name") or user_data.get("given_name") or "Google User"
        picture = user_data.get("picture", "")

        user = workspace_store.save_user(
            email=email.strip().lower(),
            name=name,
            password="",
            org_name="Google Account",
            avatar=picture,
            providers="google",
        )
        return {"success": True, "user": _sanitize_user(user)}


