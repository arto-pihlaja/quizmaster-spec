"""Quiz service - business logic for quiz CRUD operations."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Quiz, Question, Answer
from ..schemas.quiz import QuizCreate, QuizResponse, QuizListItem

logger = logging.getLogger(__name__)


class QuizService:
    """Service for quiz CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def create_quiz(self, owner_id: str, quiz_data: QuizCreate) -> Quiz:
        """Create a new quiz with questions and answers.

        Args:
            owner_id: ID of the user creating the quiz
            quiz_data: Quiz creation data including questions and answers

        Returns:
            The created Quiz entity
        """
        # Create quiz
        quiz = Quiz(
            title=quiz_data.title,
            owner_id=owner_id,
        )
        self.db.add(quiz)

        # Create questions and answers
        for q_idx, q_data in enumerate(quiz_data.questions, start=1):
            question = Question(
                quiz=quiz,
                text=q_data.text,
                display_order=q_idx,
                points=q_data.points,
            )
            self.db.add(question)

            for a_idx, a_data in enumerate(q_data.answers, start=1):
                answer = Answer(
                    question=question,
                    text=a_data.text,
                    is_correct=a_data.is_correct,
                    display_order=a_idx,
                )
                self.db.add(answer)

        await self.db.flush()

        # Re-fetch with eager loading to get all relationships
        created_quiz = await self.get_quiz(quiz.id)
        logger.info("Created quiz %s for owner %s with %d questions", quiz.id, owner_id, len(quiz_data.questions))
        return created_quiz

    async def list_quizzes(self, owner_id: str) -> List[QuizListItem]:
        """List all quizzes owned by a user.

        Args:
            owner_id: ID of the quiz owner

        Returns:
            List of quiz list items with question counts
        """
        stmt = (
            select(
                Quiz.id,
                Quiz.title,
                Quiz.created_at,
                Quiz.updated_at,
                func.count(Question.id).label("question_count"),
            )
            .outerjoin(Question)
            .where(Quiz.owner_id == owner_id)
            .group_by(Quiz.id)
            .order_by(Quiz.updated_at.desc())
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            QuizListItem(
                id=row.id,
                title=row.title,
                question_count=row.question_count,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    async def get_quiz(self, quiz_id: str, owner_id: Optional[str] = None) -> Optional[Quiz]:
        """Get a quiz by ID with all questions and answers.

        Args:
            quiz_id: ID of the quiz to retrieve
            owner_id: If provided, verify the quiz belongs to this owner

        Returns:
            The Quiz entity or None if not found
        """
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.questions).selectinload(Question.answers)
            )
            .where(Quiz.id == quiz_id)
        )

        if owner_id is not None:
            stmt = stmt.where(Quiz.owner_id == owner_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_quiz(self, quiz_id: str, owner_id: str, quiz_data: QuizCreate) -> Optional[Quiz]:
        """Update a quiz with atomic replacement of questions and answers.

        Args:
            quiz_id: ID of the quiz to update
            owner_id: ID of the owner (for authorization)
            quiz_data: New quiz data

        Returns:
            The updated Quiz entity or None if not found/not authorized
        """
        # Get existing quiz
        quiz = await self.get_quiz(quiz_id, owner_id)
        if quiz is None:
            return None

        # Update quiz title
        quiz.title = quiz_data.title

        # Delete existing questions (cascade deletes answers)
        for question in list(quiz.questions):  # Copy list to avoid modification during iteration
            await self.db.delete(question)

        # Flush deletions and clear the cached relationship
        await self.db.flush()

        # Expire the quiz to clear cached relationship data
        await self.db.refresh(quiz)

        # Create new questions and answers
        for q_idx, q_data in enumerate(quiz_data.questions, start=1):
            question = Question(
                quiz_id=quiz.id,  # Use ID instead of object to avoid caching issues
                text=q_data.text,
                display_order=q_idx,
                points=q_data.points,
            )
            self.db.add(question)

            for a_idx, a_data in enumerate(q_data.answers, start=1):
                answer = Answer(
                    question=question,
                    text=a_data.text,
                    is_correct=a_data.is_correct,
                    display_order=a_idx,
                )
                self.db.add(answer)

        await self.db.flush()

        # Re-fetch with eager loading to get all relationships
        updated_quiz = await self.get_quiz(quiz.id)
        logger.info("Updated quiz %s with %d questions", quiz_id, len(quiz_data.questions))
        return updated_quiz

    async def delete_quiz(self, quiz_id: str, owner_id: str) -> bool:
        """Delete a quiz by ID.

        Args:
            quiz_id: ID of the quiz to delete
            owner_id: ID of the owner (for authorization)

        Returns:
            True if deleted, False if not found or not authorized
        """
        quiz = await self.get_quiz(quiz_id, owner_id)
        if quiz is None:
            logger.warning("Delete failed: quiz %s not found or not owned by %s", quiz_id, owner_id)
            return False

        await self.db.delete(quiz)
        logger.info("Deleted quiz %s for owner %s", quiz_id, owner_id)
        return True
