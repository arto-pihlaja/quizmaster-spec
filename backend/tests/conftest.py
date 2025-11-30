"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.db import Base, get_db
from src.main import app


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
def sample_quiz_data():
    """Sample quiz data for testing."""
    return {
        "title": "Test Quiz",
        "questions": [
            {
                "text": "What is 2 + 2?",
                "points": 1,
                "answers": [
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": True},
                    {"text": "5", "is_correct": False},
                ],
            },
            {
                "text": "What is the capital of France?",
                "points": 2,
                "answers": [
                    {"text": "London", "is_correct": False},
                    {"text": "Paris", "is_correct": True},
                ],
            },
        ],
    }


@pytest.fixture
def minimal_quiz_data():
    """Minimal valid quiz data."""
    return {
        "title": "Minimal Quiz",
        "questions": [
            {
                "text": "Question 1?",
                "answers": [
                    {"text": "Yes", "is_correct": True},
                    {"text": "No", "is_correct": False},
                ],
            },
        ],
    }


# Alias for auth tests
@pytest_asyncio.fixture
async def db_session(test_db: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Alias for test_db fixture used in auth tests."""
    yield test_db
