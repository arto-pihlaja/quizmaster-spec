"""Scoreboard API endpoints."""

from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..services.scoreboard import ScoreboardService
from ..schemas.scoreboard import ScoreboardResponse, MyRankResponse, ScoreboardStats

router = APIRouter()

# Templates
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_current_user_id(request: Request) -> Optional[str]:
    """Extract current user ID from session (optional auth).

    Returns None if not authenticated.
    """
    # For now, check for a user_id in cookies or headers
    # This will be replaced with proper session auth when 002-user-management is integrated
    return request.cookies.get("user_id") or request.headers.get("X-User-ID")


# JSON API Endpoints

@router.get("/api/scoreboard", response_model=ScoreboardResponse)
async def get_scoreboard_data(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=10, le=100, description="Entries per page"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get scoreboard data as JSON for client-side refresh."""
    service = ScoreboardService(db)
    current_user_id = get_current_user_id(request) if request else None

    return await service.get_scoreboard(
        page=page,
        page_size=page_size,
        current_user_id=current_user_id,
    )


@router.get("/api/scoreboard/my-rank", response_model=MyRankResponse)
async def get_my_rank(
    page_size: int = Query(50, ge=10, le=100, description="Page size for calculating page number"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get current user's rank and the page they appear on.

    Requires authentication. Returns 401 if not logged in.
    """
    user_id = get_current_user_id(request) if request else None

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ScoreboardService(db)
    result = await service.get_user_rank(user_id, page_size)

    if not result:
        raise HTTPException(status_code=404, detail="User has no score record")

    return result


@router.get("/api/scoreboard/stats", response_model=ScoreboardStats)
async def get_scoreboard_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregate statistics about the scoreboard.

    Public endpoint, no authentication required.
    """
    service = ScoreboardService(db)
    return await service.get_stats()


# HTML Page Endpoints

@router.get("/scoreboard", response_class=HTMLResponse)
async def get_scoreboard_page(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    db: AsyncSession = Depends(get_db),
):
    """Get the server-rendered scoreboard page.

    If user is logged in, their entry will be highlighted.
    """
    service = ScoreboardService(db)
    current_user_id = get_current_user_id(request)

    scoreboard = await service.get_scoreboard(
        page=page,
        page_size=50,
        current_user_id=current_user_id,
    )

    stats = await service.get_stats()

    # Get user's rank if logged in
    user_rank = None
    if current_user_id:
        user_rank = await service.get_user_rank(current_user_id)

    return templates.TemplateResponse(
        request,
        "scoreboard.html",
        {
            "scoreboard": scoreboard,
            "stats": stats,
            "user_rank": user_rank,
            "current_user_id": current_user_id,
        },
    )
