"""Authentication and user management Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Request schemas

class UserRegister(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=50)


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class ResetPassword(BaseModel):
    """Schema for password reset confirmation."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ProfileUpdate(BaseModel):
    """Schema for profile update request."""

    display_name: str = Field(min_length=1, max_length=50)


# Response schemas

class UserResponse(BaseModel):
    """Schema for user data in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str
    is_admin: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """Schema for authentication responses (login/register)."""

    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    """Schema for simple message responses."""

    message: str


class LockoutError(BaseModel):
    """Schema for account lockout error responses."""

    detail: str
    locked_until: datetime
    retry_after: int  # Seconds until retry allowed
