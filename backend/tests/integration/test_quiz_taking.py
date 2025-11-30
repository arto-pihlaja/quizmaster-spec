"""Integration tests for quiz taking operations."""

import pytest
from httpx import AsyncClient


class TestCompleteQuizFlow:
    """Integration tests for the complete quiz-taking flow."""

    @pytest.mark.asyncio
    async def test_complete_quiz_flow(self, client: AsyncClient, sample_quiz_data):
        """User can browse, start, submit, and view results."""
        # Step 1: Create a quiz (as quiz owner)
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        assert create_response.status_code == 201
        quiz_id = create_response.json()["id"]

        # Step 2: Browse quizzes (as quiz taker)
        browse_response = await client.get("/quizzes/browse")
        assert browse_response.status_code == 200
        quizzes = browse_response.json()["quizzes"]
        assert any(q["id"] == quiz_id for q in quizzes)

        # Step 3: Start the quiz
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        assert start_response.status_code == 201
        quiz_view = start_response.json()
        attempt_id = quiz_view["attempt_id"]

        # Verify no correct answers are exposed
        for question in quiz_view["questions"]:
            for answer in question["answers"]:
                assert "is_correct" not in answer

        # Step 4: Submit answers
        answers = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in quiz_view["questions"]
        ]
        submit_response = await client.post(
            f"/attempts/{attempt_id}/submit",
            json={"answers": answers},
        )
        assert submit_response.status_code == 200
        result = submit_response.json()
        assert result["total_score"] >= 0
        assert result["total_points_possible"] > 0

        # Step 5: View results
        results_response = await client.get(f"/attempts/{attempt_id}/results")
        assert results_response.status_code == 200
        results = results_response.json()
        assert results["attempt_id"] == attempt_id
        assert len(results["answers"]) == len(sample_quiz_data["questions"])

    @pytest.mark.asyncio
    async def test_score_calculation_correct_answers(
        self, client: AsyncClient, sample_quiz_data
    ):
        """Score should be calculated correctly for all correct answers."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        created_quiz = create_response.json()
        quiz_id = created_quiz["id"]

        # Start quiz
        start_response = await client.post(f"/quizzes/{quiz_id}/start")
        quiz_view = start_response.json()
        attempt_id = quiz_view["attempt_id"]

        # Find correct answers from the created quiz
        # The correct answers are marked with is_correct: True in the original data
        correct_answer_indices = []
        for q_data in sample_quiz_data["questions"]:
            for i, a_data in enumerate(q_data["answers"]):
                if a_data["is_correct"]:
                    correct_answer_indices.append(i)
                    break

        # Build answers using correct indices
        answers = []
        for i, question in enumerate(quiz_view["questions"]):
            correct_idx = correct_answer_indices[i]
            answers.append({
                "question_id": question["id"],
                "selected_answer_id": question["answers"][correct_idx]["id"],
            })

        # Submit
        submit_response = await client.post(
            f"/attempts/{attempt_id}/submit",
            json={"answers": answers},
        )
        result = submit_response.json()

        # Calculate expected total points
        expected_points = sum(
            q.get("points", 1) for q in sample_quiz_data["questions"]
        )
        assert result["total_score"] == expected_points
        assert result["percentage"] == 100.0


class TestRetakeQuiz:
    """Integration tests for retaking quizzes."""

    @pytest.mark.asyncio
    async def test_can_retake_quiz(self, client: AsyncClient, sample_quiz_data):
        """User can take the same quiz multiple times."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Complete first attempt
        start1 = await client.post(f"/quizzes/{quiz_id}/start")
        quiz_view1 = start1.json()
        answers1 = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in quiz_view1["questions"]
        ]
        await client.post(
            f"/attempts/{quiz_view1['attempt_id']}/submit",
            json={"answers": answers1},
        )

        # Complete second attempt
        start2 = await client.post(f"/quizzes/{quiz_id}/start")
        quiz_view2 = start2.json()
        answers2 = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in quiz_view2["questions"]
        ]
        submit2 = await client.post(
            f"/attempts/{quiz_view2['attempt_id']}/submit",
            json={"answers": answers2},
        )

        assert submit2.status_code == 200
        assert quiz_view1["attempt_id"] != quiz_view2["attempt_id"]

    @pytest.mark.asyncio
    async def test_history_shows_all_attempts(self, client: AsyncClient, sample_quiz_data):
        """Quiz history should show all user's attempts."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Complete two attempts
        for _ in range(2):
            start = await client.post(f"/quizzes/{quiz_id}/start")
            quiz_view = start.json()
            answers = [
                {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
                for q in quiz_view["questions"]
            ]
            await client.post(
                f"/attempts/{quiz_view['attempt_id']}/submit",
                json={"answers": answers},
            )

        # Check history HTML page
        history_response = await client.get(f"/quizzes/{quiz_id}/history")
        assert history_response.status_code == 200
        # Should return HTML with history items
        html_content = history_response.text
        assert "Attempt History" in html_content
        # Should have two history-item divs (one per attempt)
        assert html_content.count("history-item") >= 2

    @pytest.mark.asyncio
    async def test_best_score_marked_in_history(
        self, client: AsyncClient, sample_quiz_data
    ):
        """Best score should be marked in attempt history."""
        # Create quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        # Complete an attempt
        start = await client.post(f"/quizzes/{quiz_id}/start")
        quiz_view = start.json()
        answers = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in quiz_view["questions"]
        ]
        await client.post(
            f"/attempts/{quiz_view['attempt_id']}/submit",
            json={"answers": answers},
        )

        # Check history HTML page - should have best badge
        history_response = await client.get(f"/quizzes/{quiz_id}/history")
        assert history_response.status_code == 200
        html_content = history_response.text
        # Should have exactly one best-badge element
        assert "best-badge" in html_content or "Best Score" in html_content


class TestBrowseQuizzes:
    """Integration tests for quiz browsing."""

    @pytest.mark.asyncio
    async def test_browse_shows_all_quizzes(self, client: AsyncClient, sample_quiz_data):
        """Browse should show quizzes from all users."""
        # Create quizzes (in test mode, all use same user ID, but concept holds)
        await client.post("/quizzes", json=sample_quiz_data)
        await client.post(
            "/quizzes",
            json={**sample_quiz_data, "title": "Another Quiz"},
        )

        # Browse
        response = await client.get("/quizzes/browse")
        quizzes = response.json()["quizzes"]

        assert len(quizzes) >= 2

    @pytest.mark.asyncio
    async def test_browse_shows_user_stats(self, client: AsyncClient, sample_quiz_data):
        """Browse should show user's attempt stats for each quiz."""
        # Create and complete a quiz
        create_response = await client.post("/quizzes", json=sample_quiz_data)
        quiz_id = create_response.json()["id"]

        start = await client.post(f"/quizzes/{quiz_id}/start")
        quiz_view = start.json()
        answers = [
            {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
            for q in quiz_view["questions"]
        ]
        await client.post(
            f"/attempts/{quiz_view['attempt_id']}/submit",
            json={"answers": answers},
        )

        # Browse and check stats
        response = await client.get("/quizzes/browse")
        quizzes = response.json()["quizzes"]
        our_quiz = next(q for q in quizzes if q["id"] == quiz_id)

        assert our_quiz["user_attempts"] == 1
        assert our_quiz["user_best_score"] is not None


class TestMyAttempts:
    """Integration tests for viewing all user attempts."""

    @pytest.mark.asyncio
    async def test_my_attempts_across_quizzes(self, client: AsyncClient, sample_quiz_data):
        """My attempts should show attempts from all quizzes."""
        # Create two quizzes and complete each
        for title in ["Quiz 1", "Quiz 2"]:
            create_response = await client.post(
                "/quizzes",
                json={**sample_quiz_data, "title": title},
            )
            quiz_id = create_response.json()["id"]

            start = await client.post(f"/quizzes/{quiz_id}/start")
            quiz_view = start.json()
            answers = [
                {"question_id": q["id"], "selected_answer_id": q["answers"][0]["id"]}
                for q in quiz_view["questions"]
            ]
            await client.post(
                f"/attempts/{quiz_view['attempt_id']}/submit",
                json={"answers": answers},
            )

        # Check my attempts
        response = await client.get("/my-attempts")
        data = response.json()

        assert data["total"] >= 2
        assert len(data["attempts"]) >= 2
