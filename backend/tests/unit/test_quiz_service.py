"""Unit tests for QuizService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.quiz import QuizService
from src.schemas.quiz import QuizCreate, QuestionCreate, AnswerCreate


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
        ],
    )


class TestCreateQuiz:
    """Unit tests for QuizService.create_quiz()."""

    @pytest.mark.asyncio
    async def test_create_quiz_returns_quiz(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """create_quiz should return a Quiz entity."""
        owner_id = "test-owner-id"

        quiz = await quiz_service.create_quiz(owner_id, quiz_create_data)

        assert quiz is not None
        assert quiz.title == quiz_create_data.title
        assert quiz.owner_id == owner_id

    @pytest.mark.asyncio
    async def test_create_quiz_generates_id(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """create_quiz should generate a UUID for the quiz."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        assert quiz.id is not None
        assert len(quiz.id) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_create_quiz_creates_questions(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """create_quiz should create questions with correct data."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        assert len(quiz.questions) == 1
        question = quiz.questions[0]
        assert question.text == quiz_create_data.questions[0].text
        assert question.points == quiz_create_data.questions[0].points
        assert question.display_order == 1

    @pytest.mark.asyncio
    async def test_create_quiz_creates_answers(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """create_quiz should create answers for questions."""
        quiz = await quiz_service.create_quiz("owner-1", quiz_create_data)

        answers = quiz.questions[0].answers
        assert len(answers) == 2

        correct_answers = [a for a in answers if a.is_correct]
        assert len(correct_answers) == 1


class TestListQuizzes:
    """Unit tests for QuizService.list_quizzes()."""

    @pytest.mark.asyncio
    async def test_list_quizzes_empty(self, quiz_service: QuizService):
        """list_quizzes should return empty list when no quizzes exist."""
        quizzes = await quiz_service.list_quizzes("owner-1")

        assert quizzes == []

    @pytest.mark.asyncio
    async def test_list_quizzes_returns_owner_quizzes(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """list_quizzes should return only quizzes owned by the user."""
        await quiz_service.create_quiz("owner-1", quiz_create_data)
        await quiz_service.create_quiz("owner-2", quiz_create_data)

        quizzes = await quiz_service.list_quizzes("owner-1")

        assert len(quizzes) == 1

    @pytest.mark.asyncio
    async def test_list_quizzes_includes_question_count(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """list_quizzes should include question count."""
        await quiz_service.create_quiz("owner-1", quiz_create_data)

        quizzes = await quiz_service.list_quizzes("owner-1")

        assert quizzes[0].question_count == 1


class TestGetQuiz:
    """Unit tests for QuizService.get_quiz()."""

    @pytest.mark.asyncio
    async def test_get_quiz_returns_quiz(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """get_quiz should return the quiz with given ID."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        quiz = await quiz_service.get_quiz(created.id)

        assert quiz is not None
        assert quiz.id == created.id

    @pytest.mark.asyncio
    async def test_get_quiz_returns_none_not_found(self, quiz_service: QuizService):
        """get_quiz should return None for non-existent quiz."""
        quiz = await quiz_service.get_quiz("non-existent-id")

        assert quiz is None

    @pytest.mark.asyncio
    async def test_get_quiz_with_owner_check(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """get_quiz with owner_id should only return quiz if owner matches."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        # Correct owner
        quiz = await quiz_service.get_quiz(created.id, "owner-1")
        assert quiz is not None

        # Wrong owner
        quiz = await quiz_service.get_quiz(created.id, "owner-2")
        assert quiz is None


class TestUpdateQuiz:
    """Unit tests for QuizService.update_quiz()."""

    @pytest.mark.asyncio
    async def test_update_quiz_changes_title(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """update_quiz should update the quiz title."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        updated_data = QuizCreate(
            title="Updated Title",
            questions=quiz_create_data.questions,
        )

        updated = await quiz_service.update_quiz(created.id, "owner-1", updated_data)

        assert updated.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_quiz_replaces_questions(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """update_quiz should replace questions atomically."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        new_questions = [
            QuestionCreate(
                text="New question?",
                answers=[
                    AnswerCreate(text="Yes", is_correct=True),
                    AnswerCreate(text="No", is_correct=False),
                ],
            ),
            QuestionCreate(
                text="Another question?",
                answers=[
                    AnswerCreate(text="A", is_correct=False),
                    AnswerCreate(text="B", is_correct=True),
                ],
            ),
        ]

        updated_data = QuizCreate(title=created.title, questions=new_questions)
        updated = await quiz_service.update_quiz(created.id, "owner-1", updated_data)

        assert len(updated.questions) == 2
        assert updated.questions[0].text == "New question?"

    @pytest.mark.asyncio
    async def test_update_quiz_returns_none_wrong_owner(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """update_quiz should return None if owner doesn't match."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        result = await quiz_service.update_quiz(created.id, "owner-2", quiz_create_data)

        assert result is None


class TestDeleteQuiz:
    """Unit tests for QuizService.delete_quiz()."""

    @pytest.mark.asyncio
    async def test_delete_quiz_returns_true(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """delete_quiz should return True on success."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        result = await quiz_service.delete_quiz(created.id, "owner-1")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_quiz_removes_quiz(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """delete_quiz should remove the quiz from database."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        await quiz_service.delete_quiz(created.id, "owner-1")

        quiz = await quiz_service.get_quiz(created.id)
        assert quiz is None

    @pytest.mark.asyncio
    async def test_delete_quiz_returns_false_not_found(self, quiz_service: QuizService):
        """delete_quiz should return False for non-existent quiz."""
        result = await quiz_service.delete_quiz("non-existent", "owner-1")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_quiz_returns_false_wrong_owner(
        self, quiz_service: QuizService, quiz_create_data: QuizCreate
    ):
        """delete_quiz should return False if owner doesn't match."""
        created = await quiz_service.create_quiz("owner-1", quiz_create_data)

        result = await quiz_service.delete_quiz(created.id, "owner-2")

        assert result is False
