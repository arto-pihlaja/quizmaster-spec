"""Quiz taking API endpoints."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..services.attempt import AttemptService
from ..schemas.attempt import (
    SubmitRequest,
    QuizTakingView,
    AttemptResult,
    MyAttemptsResponse,
)

router = APIRouter()

# Templates for HTML pages
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Dependency to get current user ID
# TODO: Replace with actual auth when user-management (002) is implemented
async def get_current_user_id() -> str:
    """Get the current authenticated user's ID."""
    return "00000000-0000-0000-0000-000000000001"


# Type aliases for dependencies
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]


# JSON API Endpoints

@router.post(
    "/quizzes/{quiz_id}/start",
    response_model=QuizTakingView,
    status_code=status.HTTP_201_CREATED,
)
async def start_quiz(
    quiz_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Start a quiz attempt."""
    service = AttemptService(db)
    result = await service.start_quiz(user_id, quiz_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return result


@router.get("/attempts/{attempt_id}", response_model=QuizTakingView)
async def get_attempt(
    attempt_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get an in-progress attempt for resuming."""
    service = AttemptService(db)
    result = await service.get_attempt(attempt_id, user_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Attempt not found or already submitted")

    return result


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResult)
async def submit_attempt(
    attempt_id: str,
    submit_data: SubmitRequest,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Submit quiz answers."""
    service = AttemptService(db)
    result = await service.submit_quiz(attempt_id, user_id, submit_data.answers)

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Attempt not found, not authorized, or already submitted",
        )

    return result


@router.get("/attempts/{attempt_id}/results", response_model=AttemptResult)
async def get_attempt_results(
    attempt_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get results for a submitted attempt."""
    service = AttemptService(db)
    result = await service.get_results(attempt_id, user_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Attempt not found, not authorized, or not yet submitted",
        )

    return result


@router.get("/my-attempts", response_model=MyAttemptsResponse)
async def get_my_attempts(
    db: DbSession,
    user_id: CurrentUserId,
    limit: int = 20,
    offset: int = 0,
):
    """Get all user's quiz attempts."""
    if limit < 1 or limit > 100:
        limit = 20
    if offset < 0:
        offset = 0

    service = AttemptService(db)
    attempts, total = await service.get_my_attempts(user_id, limit, offset)

    return MyAttemptsResponse(
        attempts=attempts,
        total=total,
        limit=limit,
        offset=offset,
    )


# HTML Page Endpoints

@router.get("/browse", response_class=HTMLResponse)
async def get_browse_page(
    request: Request,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get the quiz browser HTML page."""
    service = AttemptService(db)
    quizzes = await service.browse_quizzes(user_id)
    return templates.TemplateResponse(
        "quiz_browser.html",
        {"request": request, "quizzes": quizzes},
    )


@router.get("/take/{quiz_id}", response_class=HTMLResponse)
async def get_take_page(
    request: Request,
    quiz_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get the quiz taking HTML page."""
    service = AttemptService(db)
    # Start a new attempt when visiting the take page
    quiz_view = await service.start_quiz(user_id, quiz_id)

    if quiz_view is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return templates.TemplateResponse(
        "quiz_take.html",
        {"request": request, "quiz": quiz_view},
    )


@router.get("/results/{attempt_id}", response_class=HTMLResponse)
async def get_results_page(
    request: Request,
    attempt_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get the results HTML page."""
    service = AttemptService(db)
    results = await service.get_results(attempt_id, user_id)

    if results is None:
        raise HTTPException(status_code=404, detail="Results not found")

    return templates.TemplateResponse(
        "quiz_results.html",
        {"request": request, "results": results},
    )
