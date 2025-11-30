"""Unit tests for AttemptService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.attempt import AttemptService
from src.services.quiz import QuizService
from src.schemas.quiz import QuizCreate, QuestionCreate, AnswerCreate
from src.schemas.attempt import AnswerSubmission


@pytest.fixture
def attempt_service(test_db: AsyncSession) -> AttemptService:
    """Create AttemptService instance with test database."""
    return AttemptService(test_db)


@pytest.fixture
def quiz_service(test_db: AsyncSession) -> QuizService:
    """Create QuizService instance with test database."""
    return QuizService(test_db)


@pytest.fixture
def quiz_create_data() -> QuizCreate:
    """Sample QuizCreate data."""
    return QuizCreate(
        title="Test Quiz",
        questions=[
            QuestionCreate(
                text="What is 2 + 2?",
                points=1,
                answers=[
                    AnswerCreate(text="3", is_correct=False),
                    AnswerCreate(text="4", is_correct=True),
                ],
            ),
            QuestionCreate(
                text="What is 3 + 3?",
                points=2,
                answers=[
                    AnswerCreate(text="5", is_correct=False),
                    AnswerCreate(text="6", is_correct=True),
                ],
            ),
        ],
    )


class TestStartQuiz:
    """Unit tests for AttemptService.start_quiz()."""

    @pytest.mark.asyncio
    async def test_start_quiz_returns_view(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """start_quiz should return a QuizTakingView."""
        # Create a quiz
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        # Start the quiz
        result = await attempt_service.start_quiz("user-1", quiz.id)

        assert result is not None
        assert result.quiz_title == quiz_create_data.title
        assert result.total_questions == len(quiz_create_data.questions)

    @pytest.mark.asyncio
    async def test_start_quiz_creates_attempt(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """start_quiz should create an attempt record."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        result = await attempt_service.start_quiz("user-1", quiz.id)

        assert result.attempt_id is not None

    @pytest.mark.asyncio
    async def test_start_quiz_no_correct_answers(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """start_quiz should not expose correct answers."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        result = await attempt_service.start_quiz("user-1", quiz.id)

        for question in result.questions:
            for answer in question.answers:
                # QuizTakingAnswer should not have is_correct attribute
                assert not hasattr(answer, "is_correct")

    @pytest.mark.asyncio
    async def test_start_quiz_not_found(self, attempt_service: AttemptService):
        """start_quiz should return None for non-existent quiz."""
        result = await attempt_service.start_quiz("user-1", "non-existent-id")

        assert result is None


class TestSubmitQuiz:
    """Unit tests for AttemptService.submit_quiz()."""

    @pytest.mark.asyncio
    async def test_submit_calculates_score(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """submit_quiz should calculate the score correctly."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)

        # Get the correct answers from the original quiz
        correct_answers = []
        for i, question in enumerate(quiz.questions):
            correct = next(a for a in question.answers if a.is_correct)
            correct_answers.append(
                AnswerSubmission(
                    question_id=question.id,
                    selected_answer_id=correct.id,
                )
            )

        result = await attempt_service.submit_quiz(
            str(quiz_view.attempt_id), "user-1", correct_answers
        )

        assert result is not None
        assert result.total_score == 3  # 1 + 2 points
        assert result.total_points_possible == 3

    @pytest.mark.asyncio
    async def test_submit_wrong_answers(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """submit_quiz should give 0 points for wrong answers."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)

        # Get wrong answers
        wrong_answers = []
        for question in quiz.questions:
            wrong = next(a for a in question.answers if not a.is_correct)
            wrong_answers.append(
                AnswerSubmission(
                    question_id=question.id,
                    selected_answer_id=wrong.id,
                )
            )

        result = await attempt_service.submit_quiz(
            str(quiz_view.attempt_id), "user-1", wrong_answers
        )

        assert result is not None
        assert result.total_score == 0

    @pytest.mark.asyncio
    async def test_submit_returns_feedback(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """submit_quiz should return per-question feedback."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)

        answers = [
            AnswerSubmission(
                question_id=q.id, selected_answer_id=q.answers[0].id
            )
            for q in quiz.questions
        ]

        result = await attempt_service.submit_quiz(
            str(quiz_view.attempt_id), "user-1", answers
        )

        assert len(result.answers) == len(quiz_create_data.questions)
        for answer in result.answers:
            assert answer.correct_answer is not None
            assert answer.is_correct is not None

    @pytest.mark.asyncio
    async def test_submit_already_submitted(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """submit_quiz should return None if already submitted."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)

        answers = [
            AnswerSubmission(
                question_id=q.id, selected_answer_id=q.answers[0].id
            )
            for q in quiz.questions
        ]

        # Submit once
        await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        # Try to submit again
        result = await attempt_service.submit_quiz(
            str(quiz_view.attempt_id), "user-1", answers
        )

        assert result is None


class TestGetResults:
    """Unit tests for AttemptService.get_results()."""

    @pytest.mark.asyncio
    async def test_get_results_after_submit(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """get_results should return results after submission."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)

        answers = [
            AnswerSubmission(
                question_id=q.id, selected_answer_id=q.answers[0].id
            )
            for q in quiz.questions
        ]
        await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        result = await attempt_service.get_results(str(quiz_view.attempt_id), "user-1")

        assert result is not None
        assert result.total_score is not None

    @pytest.mark.asyncio
    async def test_get_results_not_submitted(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """get_results should return None if not yet submitted."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)

        result = await attempt_service.get_results(str(quiz_view.attempt_id), "user-1")

        assert result is None


class TestBrowseQuizzes:
    """Unit tests for AttemptService.browse_quizzes()."""

    @pytest.mark.asyncio
    async def test_browse_returns_quizzes(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """browse_quizzes should return all quizzes."""
        await quiz_service.create_quiz("owner-1", quiz_create_data)
        await quiz_service.create_quiz("owner-2", quiz_create_data)

        result = await attempt_service.browse_quizzes("user-1")

        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_browse_includes_question_count(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """browse_quizzes should include question counts."""
        await quiz_service.create_quiz("owner-1", quiz_create_data)

        result = await attempt_service.browse_quizzes("user-1")

        assert result[0].question_count == len(quiz_create_data.questions)

    @pytest.mark.asyncio
    async def test_browse_tracks_user_attempts(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """browse_quizzes should track user's attempt count."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        # Complete one attempt
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)
        answers = [
            AnswerSubmission(
                question_id=q.id, selected_answer_id=q.answers[0].id
            )
            for q in quiz.questions
        ]
        await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        result = await attempt_service.browse_quizzes("user-1")

        # Find our quiz
        quiz_item = next(q for q in result if str(q.id) == quiz.id)
        assert quiz_item.user_attempts == 1


class TestGetQuizHistory:
    """Unit tests for AttemptService.get_quiz_history()."""

    @pytest.mark.asyncio
    async def test_history_returns_attempts(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """get_quiz_history should return user's attempts."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        # Complete two attempts
        for _ in range(2):
            quiz_view = await attempt_service.start_quiz("user-1", quiz.id)
            answers = [
                AnswerSubmission(
                    question_id=q.id, selected_answer_id=q.answers[0].id
                )
                for q in quiz.questions
            ]
            await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        result = await attempt_service.get_quiz_history("user-1", quiz.id)

        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_history_marks_best(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """get_quiz_history should mark the best attempt."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        # Complete an attempt
        quiz_view = await attempt_service.start_quiz("user-1", quiz.id)
        answers = [
            AnswerSubmission(
                question_id=q.id, selected_answer_id=q.answers[0].id
            )
            for q in quiz.questions
        ]
        await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        result = await attempt_service.get_quiz_history("user-1", quiz.id)

        assert any(a.is_best for a in result)


class TestGetMyAttempts:
    """Unit tests for AttemptService.get_my_attempts()."""

    @pytest.mark.asyncio
    async def test_my_attempts_returns_all(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """get_my_attempts should return all user's attempts."""
        quiz1 = await quiz_service.create_quiz("owner-1", quiz_create_data)
        quiz2 = await quiz_service.create_quiz("owner-2", quiz_create_data)

        # Complete attempts on different quizzes
        for quiz in [quiz1, quiz2]:
            quiz_view = await attempt_service.start_quiz("user-1", quiz.id)
            answers = [
                AnswerSubmission(
                    question_id=q.id, selected_answer_id=q.answers[0].id
                )
                for q in quiz.questions
            ]
            await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        result, total = await attempt_service.get_my_attempts("user-1")

        assert total == 2
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_my_attempts_pagination(
        self,
        attempt_service: AttemptService,
        quiz_service: QuizService,
        quiz_create_data: QuizCreate,
    ):
        """get_my_attempts should support pagination."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        # Complete 3 attempts
        for _ in range(3):
            quiz_view = await attempt_service.start_quiz("user-1", quiz.id)
            answers = [
                AnswerSubmission(
                    question_id=q.id, selected_answer_id=q.answers[0].id
                )
                for q in quiz.questions
            ]
            await attempt_service.submit_quiz(str(quiz_view.attempt_id), "user-1", answers)

        result, total = await attempt_service.get_my_attempts("user-1", limit=2, offset=0)

        assert total == 3
        assert len(result) == 2
