"""SMTP Email Delivery Service for AgentShield AI.

Sends transactional emails, verification codes, and security alerts from agentsheildai@gmail.com.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("agentshield.api.mailer")


def get_smtp_config() -> dict[str, str | int]:
    """Retrieve SMTP configuration from environment variables."""
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", "agentsheildai@gmail.com"),
        "password": os.getenv("SMTP_PASSWORD", os.getenv("GMAIL_APP_PASSWORD", "")),
        "from_email": os.getenv("SMTP_FROM", "agentsheildai@gmail.com"),
        "from_name": os.getenv("SMTP_FROM_NAME", "AgenShield AI"),
    }


def send_verification_email(to_email: str, code: str) -> tuple[bool, str]:
    """
    Send a 6-digit verification code from agentsheildai@gmail.com to the recipient.

    Returns:
        tuple[bool, str]: (success, message_or_error)
    """
    cfg = get_smtp_config()
    host = str(cfg["host"]).strip()
    port = int(cfg["port"])
    user = str(cfg["user"]).strip()
    password = str(cfg["password"]).replace(" ", "").strip()
    from_email = str(cfg["from_email"]).strip()
    from_name = str(cfg["from_name"]).strip()

    subject = f"AgenShield AI — Password Reset Verification Code: {code}"

    # Rich HTML Email Template
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #0b0f19;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e2e8f0;
    }}
    .wrapper {{
      width: 100%;
      background-color: #0b0f19;
      padding: 40px 0;
    }}
    .email-card {{
      max-width: 520px;
      margin: 0 auto;
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    }}
    .header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      padding: 28px 24px;
      text-align: center;
      border-bottom: 1px solid #334155;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      color: #38bdf8;
      letter-spacing: 0.5px;
    }}
    .header p {{
      margin: 6px 0 0;
      font-size: 13px;
      color: #94a3b8;
    }}
    .content {{
      padding: 32px 28px;
    }}
    .content p {{
      margin: 0 0 16px;
      font-size: 14px;
      line-height: 1.6;
      color: #cbd5e1;
    }}
    .code-container {{
      margin: 26px 0;
      padding: 20px;
      background: #0f172a;
      border: 1px solid #38bdf8;
      border-radius: 8px;
      text-align: center;
    }}
    .code-container .label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: #94a3b8;
      margin-bottom: 8px;
    }}
    .code-container .code {{
      font-size: 34px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #38bdf8;
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
    }}
    .code-container .expiry {{
      margin-top: 8px;
      font-size: 12px;
      color: #64748b;
    }}
    .notice {{
      font-size: 12px;
      color: #94a3b8;
      background: rgba(56, 189, 248, 0.05);
      border-left: 3px solid #38bdf8;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      margin-top: 20px;
    }}
    .footer {{
      padding: 20px 24px;
      background: #0d131f;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      border-top: 1px solid #1f2937;
    }}
    .footer a {{
      color: #38bdf8;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="email-card">
      <div class="header">
        <h1>AgenShield AI</h1>
        <p>Autonomous Infrastructure Security & Verification</p>
      </div>
      <div class="content">
        <p>Hello,</p>
        <p>We received a request to reset the password for your <strong>AgenShield AI</strong> account registered with <strong>{to_email}</strong>.</p>
        
        <div class="code-container">
          <div class="label">One-Time Verification Code</div>
          <div class="code">{code}</div>
          <div class="expiry">Expires in 10 minutes</div>
        </div>

        <p>Enter this code on the AgenShield verification screen to set your new password.</p>

        <div class="notice">
          If you did not request a password reset, please disregard this email. Your password will remain unchanged and your account is secure.
        </div>
      </div>
      <div class="footer">
        Sent by <strong>AgenShield AI</strong> &bull; <a href="mailto:{from_email}">{from_email}</a><br>
        This is an automated system notification.
      </div>
    </div>
  </div>
</body>
</html>
"""

    text_body = f"""AgenShield AI — Password Reset Verification Code

Hello,

We received a request to reset your password for your AgenShield AI account ({to_email}).

Your 6-digit one-time verification code is:
{code}

This code will expire in 10 minutes.

If you did not request this password reset, please ignore this email. Your account remains secure.

Sent by AgenShield AI ({from_email})
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if not password:
        logger.warning(
            "SMTP_PASSWORD is not set in backend/.env. Cannot authenticate with %s to send email to %s.",
            from_email,
            to_email,
        )
        return (
            False,
            "SMTP_PASSWORD (Gmail App Password) not configured in backend/.env",
        )

    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=15) as server:
                server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user, password)
                server.send_message(msg)

        logger.info("Verification email successfully sent from %s to %s", from_email, to_email)
        return True, f"Verification code sent from {from_email} to {to_email}"
    except smtplib.SMTPAuthenticationError as e:
        err_msg = (
            f"SMTP Authentication Error: Could not login to {user}. "
            "For Gmail, please ensure you use an App Password (not your standard Google account password). "
            f"Detail: {e}"
        )
        logger.error(err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"Failed to send email via SMTP ({host}:{port}): {e}"
        logger.error(err_msg)
        return False, err_msg
