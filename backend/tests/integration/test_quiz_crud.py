"""Integration tests for quiz CRUD operations."""

import pytest
from httpx import AsyncClient


class TestQuizCreationFlow:
    """Integration tests for quiz creation user flow."""

    @pytest.mark.asyncio
    async def test_create_quiz_and_list(self, client: AsyncClient, sample_quiz_data):
        """User can create a quiz and see it in their list."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        assert create_response.status_code == 201

        created_quiz = create_response.json()

        # List quizzes
        list_response = await client.get("/quizzes")
        assert list_response.status_code == 200

        quizzes = list_response.json()["quizzes"]
        assert len(quizzes) >= 1

        # Find created quiz in list
        quiz_ids = [q["id"] for q in quizzes]
        assert created_quiz["id"] in quiz_ids

    @pytest.mark.asyncio
    async def test_create_quiz_with_multiple_questions(self, client: AsyncClient):
        """User can create a quiz with multiple questions."""
        quiz_data = {
            "title": "Multi-Question Quiz",
            "questions": [
                {
                    "text": "Question 1?",
                    "points": 1,
                    "answers": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False},
                    ],
                },
                {
                    "text": "Question 2?",
                    "points": 2,
                    "answers": [
                        {"text": "C", "is_correct": False},
                        {"text": "D", "is_correct": True},
                    ],
                },
                {
                    "text": "Question 3?",
                    "points": 3,
                    "answers": [
                        {"text": "E", "is_correct": True},
                        {"text": "F", "is_correct": False},
                        {"text": "G", "is_correct": False},
                    ],
                },
            ],
        }

        response = await client.post("/quizzes", json=quiz_data)
        assert response.status_code == 201

        quiz = response.json()
        assert len(quiz["questions"]) == 3

        # Verify display order
        for i, q in enumerate(quiz["questions"], start=1):
            assert q["display_order"] == i


class TestQuizEditFlow:
    """Integration tests for quiz edit user flow."""

    @pytest.mark.asyncio
    async def test_edit_quiz_title_and_verify(self, client: AsyncClient, sample_quiz_data):
        """User can edit quiz title and see changes persist."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Edit quiz
        edited_data = {**sample_quiz_data, "title": "Edited Quiz Title"}
        edit_response = await client.put(f"/quizzes/{quiz_id}", json=edited_data)
        assert edit_response.status_code == 200

        edited_quiz = edit_response.json()
        assert edited_quiz["title"] == "Edited Quiz Title"

        # Verify change persisted
        get_response = await client.get(f"/quizzes/{quiz_id}")
        assert get_response.json()["title"] == "Edited Quiz Title"

    @pytest.mark.asyncio
    async def test_edit_quiz_questions(self, client: AsyncClient, sample_quiz_data):
        """User can add/remove questions and see changes persist."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]
        original_count = len(create_response.json()["questions"])

        # Add a question
        new_data = {
            **sample_quiz_data,
            "questions": [
                *sample_quiz_data["questions"],
                {
                    "text": "New question?",
                    "answers": [
                        {"text": "Yes", "is_correct": True},
                        {"text": "No", "is_correct": False},
                    ],
                },
            ],
        }

        edit_response = await client.put(f"/quizzes/{quiz_id}", json=new_data)
        assert edit_response.status_code == 200

        edited_quiz = edit_response.json()
        assert len(edited_quiz["questions"]) == original_count + 1


class TestQuizDeleteFlow:
    """Integration tests for quiz delete user flow."""

    @pytest.mark.asyncio
    async def test_delete_quiz_and_verify_removed(
        self, client: AsyncClient, sample_quiz_data
    ):
        """User can delete quiz and it no longer appears in list."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Delete quiz
        delete_response = await client.delete(f"/quizzes/{quiz_id}")
        assert delete_response.status_code == 204

        # Verify removed from list
        list_response = await client.get("/quizzes")
        quizzes = list_response.json()["quizzes"]
        quiz_ids = [q["id"] for q in quizzes]
        assert quiz_id not in quiz_ids

        # Verify get returns 404
        get_response = await client.get(f"/quizzes/{quiz_id}")
        assert get_response.status_code == 404


class TestQuizValidation:
    """Integration tests for quiz validation."""

    @pytest.mark.asyncio
    async def test_quiz_title_trimmed(self, client: AsyncClient):
        """Quiz title should be trimmed of whitespace."""
        quiz_data = {
            "title": "  Spaced Title  ",
            "questions": [
                {
                    "text": "Q?",
                    "answers": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False},
                    ],
                },
            ],
        }

        response = await client.post("/quizzes", json=quiz_data)
        assert response.status_code == 201
        assert response.json()["title"] == "Spaced Title"

    @pytest.mark.asyncio
    async def test_question_must_have_exactly_one_correct(self, client: AsyncClient):
        """Each question must have exactly one correct answer."""
        # Multiple correct answers
        quiz_data = {
            "title": "Test",
            "questions": [
                {
                    "text": "Q?",
                    "answers": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": True},
                    ],
                },
            ],
        }

        response = await client.post("/quizzes", json=quiz_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_points_default_to_one(self, client: AsyncClient):
        """Questions without points specified should default to 1."""
        quiz_data = {
            "title": "Test",
            "questions": [
                {
                    "text": "Q?",
                    "answers": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False},
                    ],
                },
            ],
        }

        response = await client.post("/quizzes", json=quiz_data)
        assert response.status_code == 201
        assert response.json()["questions"][0]["points"] == 1
