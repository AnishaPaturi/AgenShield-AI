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


class SendCodeRequest(BaseModel):
    email: EmailStr


class SendCodeResponse(BaseModel):
    success: bool
    message: str
    email_sent: bool
    dev_code: str | None = None


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


@router.post("/verify-email", response_model=AuthResponse)
def verify_email(req: VerifyEmailRequest) -> AuthResponse:
    """Check if an email is registered in the database."""
    user = workspace_store.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email address.")
    return AuthResponse(success=True, message="Account found.")


@router.post("/send-code", response_model=SendCodeResponse)
def send_code(req: SendCodeRequest) -> SendCodeResponse:
    """
    Generate a 6-digit verification code, store it with an expiry timestamp,
    and dispatch an email from agentsheildai@gmail.com to the user's email address.
    """
    user = workspace_store.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email address.")

    # Generate a cryptographically secure 6-digit code
    code = f"{secrets.randbelow(900000) + 100000}"

    # Store code with 10-minute expiry (600 seconds)
    workspace_store.save_verification_code(req.email, code, ttl_seconds=600)

    # Attempt to send via SMTP from agentsheildai@gmail.com
    email_sent, mail_msg = send_verification_email(to_email=req.email, code=code)

    if email_sent:
        logger.info("Verification code emailed to %s from agentsheildai@gmail.com", req.email)
        return SendCodeResponse(
            success=True,
            email_sent=True,
            message=f"Verification code sent from agentsheildai@gmail.com to {req.email}.",
            dev_code=None,
        )
    else:
        logger.warning(
            "Verification email could not be sent to %s: %s", req.email, mail_msg
        )
        return SendCodeResponse(
            success=True,
            email_sent=False,
            message=(
                f"Verification code generated. (Live delivery requires SMTP_PASSWORD in backend/.env: {mail_msg})"
            ),
            dev_code=code,
        )


@router.post("/verify-code", response_model=AuthResponse)
def verify_code(req: VerifyCodeRequest) -> AuthResponse:
    """Verify if a code submitted by the user matches and has not expired."""
    is_valid = workspace_store.verify_code(req.email, req.code)
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

    # If code is provided, verify it
    if req.code:
        is_valid = workspace_store.verify_code(req.email, req.code)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification code.",
            )

    updated = workspace_store.update_user_password(req.email, req.new_password)
    if not updated:
        raise HTTPException(status_code=404, detail="No account found with this email address.")

    # Invalidate the verification code after successful password change
    workspace_store.clear_verification_code(req.email)

    logger.info("Password successfully updated in SQLite database for %s", req.email)
    return AuthResponse(success=True, message="Password updated successfully in database.")
