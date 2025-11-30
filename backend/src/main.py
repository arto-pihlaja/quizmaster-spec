"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .api.quiz import router as quiz_router
from .api.attempt import router as attempt_router


# Paths relative to project root
BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown (nothing to clean up currently)


app = FastAPI(
    title="QuizMaster",
    description="Quiz creation and management API",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files (only if directory exists)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(quiz_router, tags=["Quizzes"])
app.include_router(attempt_router, tags=["Quiz Taking"])


@app.get("/")
async def root():
    """Root endpoint - redirect to quiz list."""
    return {"message": "Welcome to QuizMaster", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
