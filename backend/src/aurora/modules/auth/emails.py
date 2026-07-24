from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def send_verification_email(
    email: str,
    token: str,
) -> None:
    """
    Send an email verification link.

    TODO:
    Replace this with Resend, SendGrid, SES, SMTP, etc.
    """
    logger.info(
        "Verification email -> %s | token=%s",
        email,
        token,
    )


async def send_password_reset_email(
    email: str,
    token: str,
) -> None:
    """
    Send a password reset email.

    TODO:
    Replace this with Resend, SendGrid, SES, SMTP, etc.
    """
    logger.info(
        "Password reset email -> %s | token=%s",
        email,
        token,
    )