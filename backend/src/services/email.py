"""Email service for sending emails (password reset, etc.)."""

import os
from typing import Protocol


class EmailService(Protocol):
    """Protocol for email service implementations."""

    async def send_reset_email(self, to: str, reset_link: str) -> bool:
        """Send a password reset email.

        Args:
            to: Recipient email address.
            reset_link: The password reset link.

        Returns:
            True if email was sent successfully, False otherwise.
        """
        ...


class ConsoleEmailService:
    """Console-based email service for development.

    Prints email content to console instead of actually sending.
    """

    async def send_reset_email(self, to: str, reset_link: str) -> bool:
        """Print password reset email to console.

        Args:
            to: Recipient email address.
            reset_link: The password reset link.

        Returns:
            Always True for development.
        """
        print("=" * 60)
        print("PASSWORD RESET EMAIL")
        print("=" * 60)
        print(f"To: {to}")
        print(f"Subject: Reset your QuizMaster password")
        print("-" * 60)
        print(f"Hello,")
        print()
        print(f"You requested a password reset for your QuizMaster account.")
        print(f"Click the link below to reset your password:")
        print()
        print(f"  {reset_link}")
        print()
        print(f"This link will expire in 24 hours.")
        print()
        print(f"If you didn't request this, you can ignore this email.")
        print("=" * 60)

        return True


def get_email_service() -> EmailService:
    """Get the appropriate email service based on configuration.

    Returns:
        An email service instance.
    """
    backend = os.getenv("EMAIL_BACKEND", "console")

    if backend == "console":
        return ConsoleEmailService()
    # Add other backends here (SMTP, SendGrid, etc.)

    return ConsoleEmailService()
