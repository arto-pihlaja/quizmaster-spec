"""Token generation and hashing utilities."""

import hashlib
import secrets


def generate_session_token() -> str:
    """Generate a cryptographically secure session token.

    Returns:
        A 64-character URL-safe token.
    """
    return secrets.token_urlsafe(48)  # 48 bytes = 64 chars when base64 encoded


def generate_reset_token() -> str:
    """Generate a cryptographically secure password reset token.

    Returns:
        A 43-character URL-safe token (32 bytes base64 encoded).
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token using SHA-256 for secure storage.

    Reset tokens should be hashed before storage to prevent
    exposure if the database is compromised.

    Args:
        token: The plain token to hash.

    Returns:
        The SHA-256 hex digest of the token.
    """
    return hashlib.sha256(token.encode()).hexdigest()
