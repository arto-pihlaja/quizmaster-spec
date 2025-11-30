"""Contract tests for Quiz Taking API endpoints."""

import pytest
from httpx import AsyncClient


class TestStartQuizContract:
    """Contract tests for POST /quizzes/{quiz_id}/start."""

    @pytest.mark.asyncio
    async def test_start_quiz_returns_201(self, client: AsyncClient, sample_quiz_data):
        """POST /quizzes/{quiz_id}/start should return 201 Created on success."""
        # First create a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Start the quiz
        response = await client.post(f"/quizzes/{quiz_id}/start")

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_start_quiz_response_structure(self, client: AsyncClient, sample_quiz_data):
        """POST /quizzes/{quiz_id}/start should return proper response structure."""
        # Create a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Start the quiz
        response = await client.post(f"/quizzes/{quiz_id}/start")
        data = response.json()

        # Check required fields
        assert "attempt_id" in data
        assert "quiz_title" in data
        assert "questions" in data
        assert "total_questions" in data

        # Check values
        assert data["quiz_title"] == sample_quiz_data["title"]
        assert len(data["questions"]) == len(sample_quiz_data["questions"])

    @pytest.mark.asyncio
    async def test_start_quiz_questions_no_correct_answer(
        self, client: AsyncClient, sample_quiz_data
    ):
        """POST /quizzes/{quiz_id}/start should NOT include is_correct in answers."""
        # Create a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Start the quiz
        response = await client.post(f"/quizzes/{quiz_id}/start")
        data = response.json()

        # Verify no is_correct field in any answer
        for question in data["questions"]:
            for answer in question["answers"]:
                assert "is_correct" not in answer

    @pytest.mark.asyncio
    async def test_start_quiz_not_found(self, client: AsyncClient):
        """POST /quizzes/{quiz_id}/start should return 404 for non-existent quiz."""
        response = await client.post("/quizzes/00000000-0000-0000-0000-000000000000/start")

        assert response.status_code == 404


class TestSubmitAttemptContract:
    """Contract tests for POST /attempts/{attempt_id}/submit."""

    @pytest.mark.asyncio
    async def test_submit_returns_200(self, client: AsyncClient, sample_quiz_data):
        """POST /attempts/{attempt_id}/submit should return 200 on success."""
        # Create and start a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        attempt = start_response.json()

        # Build answers
        answers = []
        for question in attempt["questions"]:
            answers.append({
                "question_id": question["id"],
                "selected_answer_id": question["answers"][0]["id"],
            })

        # Submit
        response = await client.post(
            f"/attempts/{attempt['attempt_id']}/submit",
            json={"answers": answers},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_submit_response_structure(self, client: AsyncClient, sample_quiz_data):
        """POST /attempts/{attempt_id}/submit should return proper result structure."""
        # Create and start a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        attempt = start_response.json()

        # Build answers
        answers = []
        for question in attempt["questions"]:
            answers.append({
                "question_id": question["id"],
                "selected_answer_id": question["answers"][0]["id"],
            })

        # Submit
        response = await client.post(
            f"/attempts/{attempt['attempt_id']}/submit",
            json={"answers": answers},
        )
        data = response.json()

        # Check required fields
        assert "attempt_id" in data
        assert "quiz_title" in data
        assert "total_score" in data
        assert "total_points_possible" in data
        assert "percentage" in data
        assert "submitted_at" in data
        assert "answers" in data

    @pytest.mark.asyncio
    async def test_submit_already_submitted(self, client: AsyncClient, sample_quiz_data):
        """POST /attempts/{attempt_id}/submit should reject already submitted attempt."""
        # Create and start a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        attempt = start_response.json()

        # Build answers
        answers = []
        for question in attempt["questions"]:
            answers.append({
                "question_id": question["id"],
                "selected_answer_id": question["answers"][0]["id"],
            })

        # Submit once
        await client.post(
            f"/attempts/{attempt['attempt_id']}/submit",
            json={"answers": answers},
        )

        # Try to submit again
        response = await client.post(
            f"/attempts/{attempt['attempt_id']}/submit",
            json={"answers": answers},
        )

        assert response.status_code == 400


class TestGetResultsContract:
    """Contract tests for GET /attempts/{attempt_id}/results."""

    @pytest.mark.asyncio
    async def test_get_results_returns_200(self, client: AsyncClient, sample_quiz_data):
        """GET /attempts/{attempt_id}/results should return 200 for submitted attempt."""
        # Create, start, and submit a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        attempt = start_response.json()

        # Submit with answers
        answers = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in attempt["questions"]
        ]
        await client.post(
            f"/attempts/{attempt['attempt_id']}/submit",
            json={"answers": answers},
        )

        # Get results
        response = await client.get(f"/attempts/{attempt['attempt_id']}/results")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_results_includes_feedback(self, client: AsyncClient, sample_quiz_data):
        """GET /attempts/{attempt_id}/results should include per-question feedback."""
        # Create, start, and submit
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        attempt = start_response.json()

        answers = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in attempt["questions"]
        ]
        await client.post(
            f"/attempts/{attempt['attempt_id']}/submit",
            json={"answers": answers},
        )

        # Get results
        response = await client.get(f"/attempts/{attempt['attempt_id']}/results")
        data = response.json()

        # Check answer details
        assert len(data["answers"]) > 0
        answer = data["answers"][0]
        assert "question_text" in answer
        assert "selected_answer" in answer
        assert "correct_answer" in answer
        assert "is_correct" in answer
        assert "points_earned" in answer


class TestBrowseQuizzesContract:
    """Contract tests for GET /quizzes/browse."""

    @pytest.mark.asyncio
    async def test_browse_returns_200(self, client: AsyncClient):
        """GET /quizzes/browse should return 200."""
        response = await client.get("/quizzes/browse")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_browse_response_structure(self, client: AsyncClient, sample_quiz_data):
        """GET /quizzes/browse should return proper structure."""
        # Create a quiz first
        await client.post("/quizzes", json=sample_quiz_data)

        response = await client.get("/quizzes/browse")
        data = response.json()

        assert "quizzes" in data
        assert isinstance(data["quizzes"], list)

        if len(data["quizzes"]) > 0:
            quiz = data["quizzes"][0]
            assert "id" in quiz
            assert "title" in quiz
            assert "question_count" in quiz
            assert "user_attempts" in quiz


class TestQuizHistoryContract:
    """Contract tests for GET /quizzes/{quiz_id}/history."""

    @pytest.mark.asyncio
    async def test_history_returns_200(self, client: AsyncClient, sample_quiz_data):
        """GET /quizzes/{quiz_id}/history should return 200."""
        # Create a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        response = await client.get(f"/quizzes/{quiz_id}/history")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_history_not_found(self, client: AsyncClient):
        """GET /quizzes/{quiz_id}/history should return 404 for non-existent quiz."""
        response = await client.get("/quizzes/00000000-0000-0000-0000-000000000000/history")

        assert response.status_code == 404


class TestMyAttemptsContract:
    """Contract tests for GET /my-attempts."""

    @pytest.mark.asyncio
    async def test_my_attempts_returns_200(self, client: AsyncClient):
        """GET /my-attempts should return 200."""
        response = await client.get("/my-attempts")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_my_attempts_response_structure(self, client: AsyncClient):
        """GET /my-attempts should return proper structure."""
        response = await client.get("/my-attempts")
        data = response.json()

        assert "attempts" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
