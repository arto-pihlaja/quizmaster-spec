"""Authentication API endpoints."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..services.auth import AuthService
from ..services.user import UserService
from ..schemas.auth import (
    UserRegister,
    UserLogin,
    ForgotPassword,
    ResetPassword,
    ProfileUpdate,
    UserResponse,
    AuthResponse,
    MessageResponse,
    LockoutError,
)

router = APIRouter()

# Templates for HTML pages
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Session cookie name
SESSION_COOKIE_NAME = "session_id"


# Type aliases for dependencies
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    """Get the current authenticated user from session cookie.

    Args:
        db: Database session.
        session_id: Session cookie value.

    Returns:
        The authenticated user.

    Raises:
        HTTPException: If not authenticated.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    service = AuthService(db)
    user = await service.get_user_by_session_token(session_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return user


async def get_optional_user(
    db: DbSession,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    """Get the current user if authenticated, None otherwise.

    Args:
        db: Database session.
        session_id: Session cookie value.

    Returns:
        The authenticated user or None.
    """
    if not session_id:
        return None

    service = AuthService(db)
    return await service.get_user_by_session_token(session_id)


CurrentUser = Annotated[object, Depends(get_current_user)]
OptionalUser = Annotated[object | None, Depends(get_optional_user)]


def set_session_cookie(response: Response, token: str) -> None:
    """Set the session cookie on a response.

    Args:
        response: The FastAPI response object.
        token: The session token.
    """
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        # secure=True,  # Uncomment in production with HTTPS
    )


def clear_session_cookie(response: Response) -> None:
    """Clear the session cookie on a response.

    Args:
        response: The FastAPI response object.
    """
    response.delete_cookie(key=SESSION_COOKIE_NAME)


# ==================== JSON API Endpoints ====================

@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    response: Response,
    data: UserRegister,
    db: DbSession,
):
    """Register a new user account.

    The first user to register becomes an admin.
    """
    service = AuthService(db)
    user, error = await service.register_user(
        email=data.email,
        password=data.password,
        display_name=data.display_name,
    )

    if error:
        if "already registered" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    # Create session for the new user
    session = await service.create_session(
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    set_session_cookie(response, session.token)

    return AuthResponse(
        message="Registration successful",
        user=UserResponse.model_validate(user),
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(
    request: Request,
    response: Response,
    data: UserLogin,
    db: DbSession,
):
    """Log in to an existing account."""
    service = AuthService(db)

    # Check for account lockout
    is_locked, locked_until = await service.check_lockout(data.email)
    if is_locked and locked_until:
        retry_after = int((locked_until - __import__("datetime").datetime.utcnow()).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account locked due to too many failed attempts",
            headers={"Retry-After": str(max(retry_after, 0))},
        )

    # Authenticate user
    user = await service.authenticate_user(data.email, data.password)

    if user is None:
        # Record failed attempt
        _, locked_until = await service.record_failed_attempt(data.email)

        # Use generic error message to prevent email enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Clear any lockout on successful login
    await service.clear_lockout(data.email)

    # Create session
    session = await service.create_session(
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    set_session_cookie(response, session.token)

    return AuthResponse(
        message="Login successful",
        user=UserResponse.model_validate(user),
    )


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    db: DbSession,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    """Log out current session."""
    if session_id:
        service = AuthService(db)
        await service.invalidate_session(session_id)

    clear_session_cookie(response)

    return MessageResponse(message="Logged out successfully")


@router.post("/auth/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPassword,
    db: DbSession,
):
    """Request a password reset email.

    Always returns success to prevent email enumeration.
    """
    service = AuthService(db)
    token = await service.request_password_reset(data.email)

    if token:
        # In production, send email with reset link
        # For development, log to console
        reset_link = f"/reset-password?token={token}"
        print(f"Password reset for {data.email}: {reset_link}")

    # Always return success message
    return MessageResponse(
        message="If an account exists with that email, a reset link has been sent."
    )


@router.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPassword,
    db: DbSession,
):
    """Reset password using a reset token."""
    service = AuthService(db)
    success, error = await service.reset_password(data.token, data.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Invalid or expired token",
        )

    return MessageResponse(message="Password reset successful. You can now log in with your new password.")


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    user: CurrentUser,
):
    """Get current authenticated user's information."""
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: ProfileUpdate,
    user: CurrentUser,
    db: DbSession,
):
    """Update current user's profile."""
    service = UserService(db)
    updated_user = await service.update_profile(user.id, display_name=data.display_name)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid display name",
        )

    return UserResponse.model_validate(updated_user)


# ==================== HTML Page Endpoints ====================

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(
    request: Request,
    user: OptionalUser,
):
    """Get the login page. Redirects to home if already logged in."""
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(
    request: Request,
    user: OptionalUser,
):
    """Get the registration page. Redirects to home if already logged in."""
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@router.get("/forgot-password", response_class=HTMLResponse)
async def get_forgot_password_page(
    request: Request,
):
    """Get the forgot password page."""
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request},
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def get_reset_password_page(
    request: Request,
    token: str,
    db: DbSession,
):
    """Get the reset password page. Validates token first."""
    from ..security.tokens import hash_token
    from ..models.password_reset import PasswordReset
    from sqlalchemy import select

    # Validate token exists and is not expired/used
    token_hash = hash_token(token)
    result = await db.execute(
        select(PasswordReset).where(PasswordReset.token_hash == token_hash)
    )
    reset = result.scalar_one_or_none()

    if reset is None or not reset.is_valid:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": "Invalid or expired reset link"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": token, "error": None},
    )


@router.get("/profile", response_class=HTMLResponse)
async def get_profile_page(
    request: Request,
    user: CurrentUser,
):
    """Get the profile page. Requires authentication."""
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user},
    )
