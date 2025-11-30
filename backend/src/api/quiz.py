"""Quiz API endpoints."""

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..services.quiz import QuizService
from ..services.attempt import AttemptService
from ..schemas.quiz import (
    QuizCreate,
    QuizResponse,
    QuizListResponse,
    QuestionResponse,
    AnswerResponse,
)
from ..schemas.attempt import QuizBrowserResponse, AttemptHistoryResponse

router = APIRouter()

# Templates for HTML pages
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Dependency to get current user ID
# TODO: Replace with actual auth when user-management is implemented
async def get_current_user_id() -> str:
    """Get the current authenticated user's ID.

    This is a placeholder until user-management (002) is implemented.
    For now, returns a fixed user ID for development.
    """
    return "00000000-0000-0000-0000-000000000001"


# Type aliases for dependencies
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]


def quiz_to_response(quiz) -> QuizResponse:
    """Convert Quiz model to QuizResponse schema."""
    return QuizResponse(
        id=UUID(quiz.id),
        title=quiz.title,
        owner_id=UUID(quiz.owner_id),
        questions=[
            QuestionResponse(
                id=UUID(q.id),
                text=q.text,
                display_order=q.display_order,
                points=q.points,
                answers=[
                    AnswerResponse(
                        id=UUID(a.id),
                        text=a.text,
                        is_correct=a.is_correct,
                    )
                    for a in q.answers
                ],
            )
            for q in quiz.questions
        ],
        created_at=quiz.created_at,
        updated_at=quiz.updated_at,
    )


# JSON API Endpoints

@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Create a new quiz."""
    service = QuizService(db)
    quiz = await service.create_quiz(user_id, quiz_data)
    return quiz_to_response(quiz)


@router.get("/quizzes", response_model=QuizListResponse)
async def list_quizzes(
    db: DbSession,
    user_id: CurrentUserId,
):
    """List current user's quizzes."""
    service = QuizService(db)
    quizzes = await service.list_quizzes(user_id)
    return QuizListResponse(quizzes=quizzes)


@router.get("/quizzes/browse", response_model=QuizBrowserResponse)
async def browse_quizzes(
    db: DbSession,
    user_id: CurrentUserId,
):
    """Browse all available quizzes."""
    service = AttemptService(db)
    quizzes = await service.browse_quizzes(user_id)
    return QuizBrowserResponse(quizzes=quizzes)


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get a quiz by ID."""
    service = QuizService(db)
    quiz = await service.get_quiz(quiz_id)

    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this quiz")

    return quiz_to_response(quiz)


@router.get("/quizzes/{quiz_id}/history", response_model=AttemptHistoryResponse)
async def get_quiz_history(
    quiz_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get user's attempt history for a specific quiz."""
    service = AttemptService(db)
    history = await service.get_quiz_history(user_id, quiz_id)

    if history is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get quiz title from first attempt or from quiz
    quiz_title = history[0].quiz_title if history else ""

    return AttemptHistoryResponse(
        quiz_id=quiz_id,
        quiz_title=quiz_title,
        attempts=history,
    )


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizCreate,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Update a quiz."""
    service = QuizService(db)

    # First check if quiz exists
    existing = await service.get_quiz(quiz_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if existing.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this quiz")

    quiz = await service.update_quiz(quiz_id, user_id, quiz_data)
    return quiz_to_response(quiz)


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Delete a quiz."""
    service = QuizService(db)

    # First check if quiz exists
    existing = await service.get_quiz(quiz_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if existing.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this quiz")

    await service.delete_quiz(quiz_id, user_id)


# HTML Page Endpoints

@router.get("/my-quizzes", response_class=HTMLResponse)
async def get_my_quizzes_page(
    request: Request,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get the quiz list HTML page."""
    service = QuizService(db)
    quizzes = await service.list_quizzes(user_id)
    return templates.TemplateResponse(
        "quiz_list.html",
        {"request": request, "quizzes": quizzes},
    )


@router.get("/quizzes/new", response_class=HTMLResponse)
async def get_quiz_create_page(
    request: Request,
    user_id: CurrentUserId,
):
    """Get the quiz creation HTML page."""
    return templates.TemplateResponse(
        "quiz_create.html",
        {"request": request},
    )


@router.get("/quizzes/{quiz_id}/edit", response_class=HTMLResponse)
async def get_quiz_edit_page(
    request: Request,
    quiz_id: str,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Get the quiz edit HTML page."""
    service = QuizService(db)
    quiz = await service.get_quiz(quiz_id)

    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this quiz")

    return templates.TemplateResponse(
        "quiz_edit.html",
        {"request": request, "quiz": quiz_to_response(quiz)},
    )
