"""Contract tests for Quiz API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateQuizContract:
    """Contract tests for POST /quizzes."""

    @pytest.mark.asyncio
    async def test_create_quiz_returns_201(self, client: AsyncClient, sample_quiz_data):
        """POST /quizzes should return 201 Created on success."""
        response = await client.post("/quizzes", json=sample_quiz_data)

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_quiz_response_structure(self, client: AsyncClient, sample_quiz_data):
        """POST /quizzes should return proper response structure."""
        response = await client.post("/quizzes", json=sample_quiz_data)
        data = response.json()

        # Check required fields
        assert "id" in data
        assert "title" in data
        assert "owner_id" in data
        assert "questions" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Check values
        assert data["title"] == sample_quiz_data["title"]
        assert len(data["questions"]) == len(sample_quiz_data["questions"])

    @pytest.mark.asyncio
    async def test_create_quiz_question_structure(self, client: AsyncClient, sample_quiz_data):
        """POST /quizzes questions should have proper structure."""
        response = await client.post("/quizzes", json=sample_quiz_data)
        data = response.json()

        question = data["questions"][0]
        assert "id" in question
        assert "text" in question
        assert "answers" in question
        assert "display_order" in question
        assert "points" in question

    @pytest.mark.asyncio
    async def test_create_quiz_answer_structure(self, client: AsyncClient, sample_quiz_data):
        """POST /quizzes answers should have proper structure."""
        response = await client.post("/quizzes", json=sample_quiz_data)
        data = response.json()

        answer = data["questions"][0]["answers"][0]
        assert "id" in answer
        assert "text" in answer
        assert "is_correct" in answer

    @pytest.mark.asyncio
    async def test_create_quiz_validation_no_title(self, client: AsyncClient):
        """POST /quizzes should return 422 when title is missing."""
        response = await client.post("/quizzes", json={
            "questions": [{"text": "Q?", "answers": [
                {"text": "A", "is_correct": True},
                {"text": "B", "is_correct": False}
            ]}]
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_quiz_validation_empty_questions(self, client: AsyncClient):
        """POST /quizzes should return 422 when questions is empty."""
        response = await client.post("/quizzes", json={
            "title": "Test",
            "questions": []
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_quiz_validation_too_few_answers(self, client: AsyncClient):
        """POST /quizzes should return 422 when question has < 2 answers."""
        response = await client.post("/quizzes", json={
            "title": "Test",
            "questions": [{
                "text": "Q?",
                "answers": [{"text": "A", "is_correct": True}]
            }]
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_quiz_validation_no_correct_answer(self, client: AsyncClient):
        """POST /quizzes should return 422 when no answer is marked correct."""
        response = await client.post("/quizzes", json={
            "title": "Test",
            "questions": [{
                "text": "Q?",
                "answers": [
                    {"text": "A", "is_correct": False},
                    {"text": "B", "is_correct": False}
                ]
            }]
        })

        assert response.status_code == 422


class TestListQuizzesContract:
    """Contract tests for GET /quizzes."""

    @pytest.mark.asyncio
    async def test_list_quizzes_returns_200(self, client: AsyncClient):
        """GET /quizzes should return 200."""
        response = await client.get("/quizzes")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_quizzes_response_structure(self, client: AsyncClient):
        """GET /quizzes should return proper structure."""
        response = await client.get("/quizzes")
        data = response.json()

        assert "quizzes" in data
        assert isinstance(data["quizzes"], list)

    @pytest.mark.asyncio
    async def test_list_quizzes_item_structure(self, client: AsyncClient, sample_quiz_data):
        """GET /quizzes items should have proper structure."""
        # Create a quiz first
        await client.post("/quizzes", json=sample_quiz_data)

        response = await client.get("/quizzes")
        data = response.json()

        assert len(data["quizzes"]) > 0
        quiz = data["quizzes"][0]

        assert "id" in quiz
        assert "title" in quiz
        assert "question_count" in quiz
        assert "created_at" in quiz
        assert "updated_at" in quiz


class TestGetQuizContract:
    """Contract tests for GET /quizzes/{id}."""

    @pytest.mark.asyncio
    async def test_get_quiz_returns_200(self, client: AsyncClient, sample_quiz_data):
        """GET /quizzes/{id} should return 200 for existing quiz."""
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        response = await client.get(f"/quizzes/{quiz_id}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_quiz_returns_404_not_found(self, client: AsyncClient):
        """GET /quizzes/{id} should return 404 for non-existent quiz."""
        response = await client.get("/quizzes/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404


class TestUpdateQuizContract:
    """Contract tests for PUT /quizzes/{id}."""

    @pytest.mark.asyncio
    async def test_update_quiz_returns_200(self, client: AsyncClient, sample_quiz_data, minimal_quiz_data):
        """PUT /quizzes/{id} should return 200 on success."""
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        response = await client.put(f"/quizzes/{quiz_id}", json=minimal_quiz_data)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_quiz_returns_404(self, client: AsyncClient, minimal_quiz_data):
        """PUT /quizzes/{id} should return 404 for non-existent quiz."""
        response = await client.put(
            "/quizzes/00000000-0000-0000-0000-000000000000",
            json=minimal_quiz_data
        )

        assert response.status_code == 404


class TestDeleteQuizContract:
    """Contract tests for DELETE /quizzes/{id}."""

    @pytest.mark.asyncio
    async def test_delete_quiz_returns_204(self, client: AsyncClient, sample_quiz_data):
        """DELETE /quizzes/{id} should return 204 on success."""
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        response = await client.delete(f"/quizzes/{quiz_id}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_quiz_returns_404(self, client: AsyncClient):
        """DELETE /quizzes/{id} should return 404 for non-existent quiz."""
        response = await client.delete("/quizzes/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404
