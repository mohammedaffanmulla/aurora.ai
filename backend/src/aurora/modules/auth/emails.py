"""
Low-level email dispatch for the auth module.

Uses aiosmtplib for a non-blocking SMTP send so we don't stall the event
loop. Swap the body of `_send_email` for your provider's SDK (SES,
Postmark, SendGrid, etc.) if you don't want to talk to SMTP directly.
"""

import logging
from email.message import EmailMessage

import aiosmtplib

from aurora.modules.auth.config import settings

logger = logging.getLogger("auth.emails")


async def _send_email(
    *,
    to: str,
    subject: str,
    html_body: str,
    text_body: str,
) -> None:
    message = EmailMessage()
    message["From"] = settings.auth_smtp_from_address
    message["To"] = to
    message["Subject"] = subject

    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.auth_smtp_host,
            port=settings.auth_smtp_port,
            username=settings.auth_smtp_user or None,
            password=settings.auth_smtp_password or None,
            start_tls=settings.auth_smtp_use_tls,
        )
    except Exception:
        logger.exception(
            "Failed to send email to %s (subject=%r)",
            to,
            subject,
        )


async def send_verification_email(*, to: str, token: str) -> None:
    link = (
        f"{settings.auth_frontend_base_url}"
        f"/verify-email?token={token}"
    )

    await _send_email(
        to=to,
        subject="Verify your email address",
        html_body=f"""
        <p>Welcome!</p>
        <p>Please confirm your email address by clicking the button below.</p>

        <p>
            <a href="{link}">
                Verify my email
            </a>
        </p>

        <p>
            This link expires in
            {settings.auth_email_verification_token_expire_hours}
            hours.
        </p>
        """,
        text_body=(
            f"Welcome!\n\n"
            f"Please confirm your email address by visiting:\n"
            f"{link}\n\n"
            f"This link expires in "
            f"{settings.auth_email_verification_token_expire_hours} hours."
        ),
    )


async def send_password_reset_email(*, to: str, token: str) -> None:
    link = (
        f"{settings.auth_frontend_base_url}"
        f"/reset-password?token={token}"
    )

    await _send_email(
        to=to,
        subject="Reset your password",
        html_body=f"""
        <p>We received a request to reset your password.</p>

        <p>
            <a href="{link}">
                Reset my password
            </a>
        </p>

        <p>
            This link expires in
            {settings.auth_password_reset_token_expire_minutes}
            minutes.
        </p>

        <p>
            If you didn't request this, you can safely ignore this email.
        </p>
        """,
        text_body=(
            f"We received a request to reset your password.\n\n"
            f"Visit:\n{link}\n\n"
            f"This link expires in "
            f"{settings.auth_password_reset_token_expire_minutes} minutes.\n\n"
            f"If you didn't request this, you can safely ignore this email."
        ),
    )