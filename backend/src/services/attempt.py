"""Attempt service - business logic for quiz taking operations."""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Quiz, Question, Answer, QuizAttempt, AttemptAnswer
from .scoreboard import ScoreboardService
from ..schemas.attempt import (
    QuizTakingView,
    QuizTakingQuestion,
    QuizTakingAnswer,
    AttemptResult,
    AttemptResultAnswer,
    QuizBrowserItem,
    AttemptHistoryItem,
    AnswerSubmission,
)

logger = logging.getLogger(__name__)


class AttemptService:
    """Service for quiz attempt operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def start_quiz(self, user_id: str, quiz_id: str) -> Optional[QuizTakingView]:
        """Start a new quiz attempt.

        Creates snapshots of the quiz, questions, and answers.
        Returns the quiz view without correct answer indicators.

        Args:
            user_id: ID of the user taking the quiz
            quiz_id: ID of the quiz to start

        Returns:
            QuizTakingView or None if quiz not found
        """
        # Get quiz with questions and answers
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.questions).selectinload(Question.answers)
            )
            .where(Quiz.id == quiz_id)
        )
        result = await self.db.execute(stmt)
        quiz = result.scalar_one_or_none()

        if quiz is None:
            return None

        # Calculate total points
        total_points = sum(q.points for q in quiz.questions)

        # Create attempt
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz.id,
            quiz_title_snapshot=quiz.title,
            total_points_possible=total_points,
            status="in_progress",
        )
        self.db.add(attempt)

        # Create answer snapshots for each question
        questions_data = []
        for question in quiz.questions:
            # Find correct answer
            correct_answer = next((a for a in question.answers if a.is_correct), None)
            correct_text = correct_answer.text if correct_answer else ""

            # Create attempt answer record
            attempt_answer = AttemptAnswer(
                attempt=attempt,
                question_id=question.id,
                question_order=question.display_order,
                question_text_snapshot=question.text,
                question_points=question.points,
                correct_answer_text=correct_text,
            )
            self.db.add(attempt_answer)

            # Build question view (NO correct answer info!)
            answers_data = [
                QuizTakingAnswer(id=UUID(a.id), text=a.text)
                for a in question.answers
            ]
            questions_data.append(
                QuizTakingQuestion(
                    id=UUID(question.id),
                    order=question.display_order,
                    text=question.text,
                    answers=answers_data,
                )
            )

        await self.db.flush()
        logger.info("Started quiz attempt %s for user %s on quiz %s", attempt.id, user_id, quiz_id)

        return QuizTakingView(
            attempt_id=UUID(attempt.id),
            quiz_title=quiz.title,
            questions=questions_data,
            total_questions=len(questions_data),
        )

    async def get_attempt(self, attempt_id: str, user_id: str) -> Optional[QuizTakingView]:
        """Get an in-progress attempt for resuming.

        Args:
            attempt_id: ID of the attempt
            user_id: ID of the user (for authorization)

        Returns:
            QuizTakingView or None if not found/not authorized
        """
        stmt = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.answers))
            .where(QuizAttempt.id == attempt_id)
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.status == "in_progress")
        )
        result = await self.db.execute(stmt)
        attempt = result.scalar_one_or_none()

        if attempt is None:
            return None

        # Get original questions with answers for display
        question_ids = [a.question_id for a in attempt.answers if a.question_id]
        if not question_ids:
            return None

        stmt = (
            select(Question)
            .options(selectinload(Question.answers))
            .where(Question.id.in_(question_ids))
        )
        result = await self.db.execute(stmt)
        questions = {q.id: q for q in result.scalars().all()}

        # Build view
        questions_data = []
        for answer in attempt.answers:
            question = questions.get(answer.question_id)
            if question:
                answers_data = [
                    QuizTakingAnswer(id=UUID(a.id), text=a.text)
                    for a in question.answers
                ]
                questions_data.append(
                    QuizTakingQuestion(
                        id=UUID(question.id),
                        order=answer.question_order,
                        text=answer.question_text_snapshot,
                        answers=answers_data,
                    )
                )

        return QuizTakingView(
            attempt_id=UUID(attempt.id),
            quiz_title=attempt.quiz_title_snapshot,
            questions=questions_data,
            total_questions=len(questions_data),
        )

    async def submit_quiz(
        self, attempt_id: str, user_id: str, answers: List[AnswerSubmission]
    ) -> Optional[AttemptResult]:
        """Submit quiz answers and calculate score.

        Args:
            attempt_id: ID of the attempt to submit
            user_id: ID of the user (for authorization)
            answers: List of question answers

        Returns:
            AttemptResult or None if not found/not authorized/already submitted
        """
        # Get attempt with answers
        stmt = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.answers))
            .where(QuizAttempt.id == attempt_id)
            .where(QuizAttempt.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        attempt = result.scalar_one_or_none()

        if attempt is None:
            logger.warning("Submit failed: attempt %s not found for user %s", attempt_id, user_id)
            return None

        if attempt.status == "submitted":
            logger.warning("Submit failed: attempt %s already submitted", attempt_id)
            return None

        # Build lookup of submitted answers
        answers_by_question = {str(a.question_id): a for a in answers}

        # Get answer texts for selected answers
        answer_ids = [str(a.selected_answer_id) for a in answers]
        stmt = select(Answer).where(Answer.id.in_(answer_ids))
        result = await self.db.execute(stmt)
        answer_texts = {a.id: a.text for a in result.scalars().all()}

        # Update attempt answers and calculate score
        total_score = 0
        result_answers = []

        for attempt_answer in attempt.answers:
            submission = answers_by_question.get(attempt_answer.question_id)

            if submission:
                selected_id = str(submission.selected_answer_id)
                selected_text = answer_texts.get(selected_id, "")
                is_correct = selected_text == attempt_answer.correct_answer_text
                points = attempt_answer.question_points if is_correct else 0

                attempt_answer.selected_answer_id = selected_id
                attempt_answer.selected_answer_text = selected_text
                attempt_answer.is_correct = is_correct
                attempt_answer.points_earned = points
                total_score += points
            else:
                # Unanswered question
                attempt_answer.selected_answer_id = None
                attempt_answer.selected_answer_text = None
                attempt_answer.is_correct = False
                attempt_answer.points_earned = 0

            result_answers.append(
                AttemptResultAnswer(
                    question_order=attempt_answer.question_order,
                    question_text=attempt_answer.question_text_snapshot,
                    question_points=attempt_answer.question_points,
                    selected_answer=attempt_answer.selected_answer_text,
                    correct_answer=attempt_answer.correct_answer_text,
                    is_correct=attempt_answer.is_correct or False,
                    points_earned=attempt_answer.points_earned or 0,
                )
            )

        # Update attempt
        attempt.total_score = total_score
        attempt.submitted_at = datetime.utcnow()
        attempt.status = "submitted"

        # Flush attempt changes before updating scoreboard
        # (scoreboard query uses raw SQL and needs to see the submitted status)
        await self.db.flush()

        # Check if this is a new best score
        is_new_best = await self._update_scoreboard(user_id, attempt.quiz_id, total_score)

        # Update the scoreboard with aggregated user score
        scoreboard_service = ScoreboardService(self.db)
        await scoreboard_service.update_user_score(user_id)
        logger.info(
            "Submitted attempt %s: score %d/%d (%.1f%%)",
            attempt_id,
            total_score,
            attempt.total_points_possible,
            (total_score / attempt.total_points_possible * 100) if attempt.total_points_possible else 0,
        )

        percentage = (total_score / attempt.total_points_possible * 100) if attempt.total_points_possible else 0

        return AttemptResult(
            attempt_id=UUID(attempt.id),
            quiz_title=attempt.quiz_title_snapshot,
            total_score=total_score,
            total_points_possible=attempt.total_points_possible,
            percentage=round(percentage, 1),
            submitted_at=attempt.submitted_at,
            is_new_best=is_new_best,
            answers=result_answers,
        )

    async def _update_scoreboard(self, user_id: str, quiz_id: Optional[str], new_score: int) -> bool:
        """Update scoreboard if this is a new best score.

        Args:
            user_id: ID of the user
            quiz_id: ID of the quiz (may be None if quiz deleted)
            new_score: The new score achieved

        Returns:
            True if this was a new best score
        """
        if quiz_id is None:
            return False

        # Get previous best score for this quiz
        stmt = (
            select(func.max(QuizAttempt.total_score))
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.quiz_id == quiz_id)
            .where(QuizAttempt.status == "submitted")
            .where(QuizAttempt.total_score != None)  # Exclude the just-submitted one
        )
        result = await self.db.execute(stmt)
        previous_best = result.scalar()

        if previous_best is None or new_score > previous_best:
            logger.info("New best score for user %s on quiz %s: %d", user_id, quiz_id, new_score)
            return True

        return False

    async def get_results(self, attempt_id: str, user_id: str) -> Optional[AttemptResult]:
        """Get results for a submitted attempt.

        Args:
            attempt_id: ID of the attempt
            user_id: ID of the user (for authorization)

        Returns:
            AttemptResult or None if not found/not authorized/not submitted
        """
        stmt = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.answers))
            .where(QuizAttempt.id == attempt_id)
            .where(QuizAttempt.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        attempt = result.scalar_one_or_none()

        if attempt is None or attempt.status != "submitted":
            return None

        result_answers = [
            AttemptResultAnswer(
                question_order=a.question_order,
                question_text=a.question_text_snapshot,
                question_points=a.question_points,
                selected_answer=a.selected_answer_text,
                correct_answer=a.correct_answer_text,
                is_correct=a.is_correct or False,
                points_earned=a.points_earned or 0,
            )
            for a in attempt.answers
        ]

        percentage = (
            (attempt.total_score / attempt.total_points_possible * 100)
            if attempt.total_points_possible else 0
        )

        return AttemptResult(
            attempt_id=UUID(attempt.id),
            quiz_title=attempt.quiz_title_snapshot,
            total_score=attempt.total_score or 0,
            total_points_possible=attempt.total_points_possible,
            percentage=round(percentage, 1),
            submitted_at=attempt.submitted_at,
            answers=result_answers,
        )

    async def browse_quizzes(self, user_id: str) -> List[QuizBrowserItem]:
        """Get all available quizzes with user's attempt info.

        Args:
            user_id: ID of the current user

        Returns:
            List of quizzes with question counts and user's attempt stats
        """
        # Get quizzes with question counts
        stmt = (
            select(
                Quiz.id,
                Quiz.title,
                func.count(Question.id).label("question_count"),
            )
            .outerjoin(Question)
            .group_by(Quiz.id)
            .order_by(Quiz.created_at.desc())
        )
        result = await self.db.execute(stmt)
        quizzes = result.all()

        # Get user's attempt stats per quiz
        browser_items = []
        for quiz in quizzes:
            # Get user's completed attempts for this quiz
            stmt = (
                select(
                    func.count(QuizAttempt.id).label("attempts"),
                    func.max(QuizAttempt.total_score).label("best_score"),
                )
                .where(QuizAttempt.quiz_id == quiz.id)
                .where(QuizAttempt.user_id == user_id)
                .where(QuizAttempt.status == "submitted")
            )
            result = await self.db.execute(stmt)
            stats = result.one()

            # Calculate best percentage
            best_percentage = None
            if stats.best_score is not None:
                # Need total points to calculate percentage
                total_points_stmt = (
                    select(func.sum(Question.points))
                    .where(Question.quiz_id == quiz.id)
                )
                total_result = await self.db.execute(total_points_stmt)
                total_points = total_result.scalar() or 0
                if total_points > 0:
                    best_percentage = round(stats.best_score / total_points * 100, 1)

            browser_items.append(
                QuizBrowserItem(
                    id=UUID(quiz.id),
                    title=quiz.title,
                    question_count=quiz.question_count,
                    user_attempts=stats.attempts or 0,
                    user_best_score=stats.best_score,
                    user_best_percentage=best_percentage,
                )
            )

        return browser_items

    async def get_quiz_history(self, user_id: str, quiz_id: str) -> Optional[List[AttemptHistoryItem]]:
        """Get user's attempt history for a specific quiz.

        Args:
            user_id: ID of the user
            quiz_id: ID of the quiz

        Returns:
            List of attempts or None if quiz not found
        """
        # Verify quiz exists
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none() is None:
            return None

        # Get all submitted attempts for this quiz
        stmt = (
            select(QuizAttempt)
            .where(QuizAttempt.quiz_id == quiz_id)
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.status == "submitted")
            .order_by(QuizAttempt.submitted_at.desc())
        )
        result = await self.db.execute(stmt)
        attempts = result.scalars().all()

        if not attempts:
            return []

        # Find best score
        best_score = max(a.total_score or 0 for a in attempts)

        history = []
        for attempt in attempts:
            percentage = (
                (attempt.total_score / attempt.total_points_possible * 100)
                if attempt.total_points_possible else 0
            )
            history.append(
                AttemptHistoryItem(
                    attempt_id=UUID(attempt.id),
                    quiz_title=attempt.quiz_title_snapshot,
                    total_score=attempt.total_score or 0,
                    total_points_possible=attempt.total_points_possible,
                    percentage=round(percentage, 1),
                    submitted_at=attempt.submitted_at,
                    is_best=(attempt.total_score == best_score),
                )
            )

        return history

    async def get_my_attempts(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[List[AttemptHistoryItem], int]:
        """Get all user's attempts across all quizzes.

        Args:
            user_id: ID of the user
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            Tuple of (attempts list, total count)
        """
        # Count total
        count_stmt = (
            select(func.count(QuizAttempt.id))
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.status == "submitted")
        )
        result = await self.db.execute(count_stmt)
        total = result.scalar() or 0

        # Get attempts
        stmt = (
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.status == "submitted")
            .order_by(QuizAttempt.submitted_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        attempts = result.scalars().all()

        # Get best scores per quiz for is_best calculation
        quiz_ids = list(set(a.quiz_id for a in attempts if a.quiz_id))
        best_scores = {}
        if quiz_ids:
            stmt = (
                select(
                    QuizAttempt.quiz_id,
                    func.max(QuizAttempt.total_score).label("best"),
                )
                .where(QuizAttempt.user_id == user_id)
                .where(QuizAttempt.quiz_id.in_(quiz_ids))
                .where(QuizAttempt.status == "submitted")
                .group_by(QuizAttempt.quiz_id)
            )
            result = await self.db.execute(stmt)
            best_scores = {row.quiz_id: row.best for row in result.all()}

        history = []
        for attempt in attempts:
            percentage = (
                (attempt.total_score / attempt.total_points_possible * 100)
                if attempt.total_points_possible else 0
            )
            is_best = best_scores.get(attempt.quiz_id) == attempt.total_score
            history.append(
                AttemptHistoryItem(
                    attempt_id=UUID(attempt.id),
                    quiz_title=attempt.quiz_title_snapshot,
                    total_score=attempt.total_score or 0,
                    total_points_possible=attempt.total_points_possible,
                    percentage=round(percentage, 1),
                    submitted_at=attempt.submitted_at,
                    is_best=is_best,
                )
            )

        return history, total
