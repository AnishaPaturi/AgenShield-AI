"""FastAPI router for User Authentication and Password Reset."""

from __future__ import annotations

import logging
import secrets
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException

from agentshield.api.store import workspace_store
from agentshield.api.mailer import send_verification_email

logger = logging.getLogger("agentshield.api.routers.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


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
