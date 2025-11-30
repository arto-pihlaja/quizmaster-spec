"""Unit tests for password hashing and validation."""

import pytest

from src.security.password import hash_password, verify_password, validate_password_strength


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_hash(self):
        """hash_password returns a bcrypt hash."""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt identifier

    def test_hash_password_different_each_time(self):
        """hash_password returns different hash each time (due to salt)."""
        password = "SecurePass123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """verify_password returns True for correct password."""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password returns False for incorrect password."""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty(self):
        """verify_password returns False for empty password."""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False


class TestPasswordValidation:
    """Tests for password strength validation."""

    def test_valid_password(self):
        """Valid password passes validation."""
        is_valid, error = validate_password_strength("SecurePass123")

        assert is_valid is True
        assert error is None

    def test_password_too_short(self):
        """Password shorter than 8 characters fails."""
        is_valid, error = validate_password_strength("Short1")

        assert is_valid is False
        assert "8 characters" in error

    def test_password_no_uppercase(self):
        """Password without uppercase fails."""
        is_valid, error = validate_password_strength("lowercase123")

        assert is_valid is False
        assert "uppercase" in error

    def test_password_no_lowercase(self):
        """Password without lowercase fails."""
        is_valid, error = validate_password_strength("UPPERCASE123")

        assert is_valid is False
        assert "lowercase" in error

    def test_password_no_digit(self):
        """Password without digit fails."""
        is_valid, error = validate_password_strength("NoDigitsHere")

        assert is_valid is False
        assert "digit" in error

    def test_password_exactly_8_chars(self):
        """Password with exactly 8 characters and all requirements passes."""
        is_valid, error = validate_password_strength("Secure1!")

        assert is_valid is True
        assert error is None
