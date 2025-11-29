# Quickstart: Quiz Taking Feature

**Feature**: 005-quiz-taking
**Date**: 2025-11-29

## Prerequisites

- Python 3.11+ installed
- QuizMaster backend running
- SQLite database initialized
- User authentication working (from 002-user-management)
- Quiz creation working (from 001-quiz-creation)
- At least one quiz with questions exists
- At least one test user account

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages (should already be installed):
- fastapi
- uvicorn
- sqlalchemy
- jinja2
- pytest
- pytest-asyncio
- httpx

### 2. Database Migration

Run the migration to add quiz-taking tables:

```bash
# If using Alembic
alembic upgrade head

# Or run the migration script directly
python -m src.db.migrations.add_attempt_tables
```

This creates:
- `quiz_attempts` table
- `attempt_answers` table

### 3. Verify Tables

```bash
sqlite3 quizmaster.db ".schema quiz_attempts"
sqlite3 quizmaster.db ".schema attempt_answers"
```

## Running the Feature

### Start the Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Quiz-Taking Features

- **Browse Quizzes**: http://localhost:8000/browse
- **Take Quiz**: http://localhost:8000/take/{quiz_id}
- **View Results**: http://localhost:8000/results/{attempt_id}
- **My Attempts**: http://localhost:8000/my-attempts

## Verification Steps

### User Story 1: Start and Complete a Quiz (P1)

1. Log in to your account
2. Navigate to http://localhost:8000/browse
3. Verify: List of available quizzes is displayed
4. Click "Start Quiz" on any quiz
5. Verify: Quiz page shows all questions with answer options
6. Verify: Correct answers are NOT indicated
7. Select an answer for each question
8. Click "Submit Quiz"
9. Verify: Results page shows your score
10. Check the scoreboard - your score should be added

```bash
# API test - Browse quizzes
curl http://localhost:8000/quizzes/browse \
  -b "session_id=YOUR_SESSION"

# API test - Start quiz
curl -X POST http://localhost:8000/quizzes/{QUIZ_ID}/start \
  -b "session_id=YOUR_SESSION"

# API test - Submit quiz
curl -X POST http://localhost:8000/attempts/{ATTEMPT_ID}/submit \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{
    "answers": [
      {"question_id": "q1-uuid", "selected_answer_id": "a1-uuid"},
      {"question_id": "q2-uuid", "selected_answer_id": "a2-uuid"}
    ]
  }'
```

Expected: 200 response with score and per-question results.

### User Story 2: Change Answers Before Submission (P1)

1. Start a quiz
2. Select answer "A" for question 1
3. Verify: Answer "A" is highlighted/selected
4. Click answer "B" for question 1
5. Verify: Answer "B" is now selected, "A" is deselected
6. Navigate to different questions and back
7. Verify: Your selections are preserved
8. Submit the quiz
9. Verify: Final selections are what was recorded

```bash
# This is primarily a frontend test
# API submission should reflect final answers only
```

### User Story 3: View Quiz Results After Submission (P2)

1. Complete and submit a quiz
2. Verify: Results page loads immediately
3. Verify: Total score shown (e.g., "7/10 points")
4. Verify: Percentage shown (e.g., "70%")
5. Verify: Each question shows:
   - Your answer
   - Whether it was correct (checkmark/X)
   - The correct answer
   - Points earned

```bash
# API test - Get results
curl http://localhost:8000/attempts/{ATTEMPT_ID}/results \
  -b "session_id=YOUR_SESSION"
```

Expected: 200 response with full results breakdown.

### User Story 4: Browse Available Quizzes (P2)

1. Navigate to http://localhost:8000/browse
2. Verify: All quizzes in the system are visible
3. Verify: Each quiz shows title and question count
4. Verify: Quizzes from different creators are all visible
5. Verify: Your attempt count for each quiz is shown

```bash
# API test - Browse with attempt counts
curl http://localhost:8000/quizzes/browse \
  -b "session_id=YOUR_SESSION"
```

Expected response includes `user_attempts` and `user_best_score` per quiz.

### User Story 5: Retake a Quiz (P3)

1. Complete a quiz (score 6/10)
2. Navigate back to the quiz browser
3. Click "Start Quiz" on the same quiz
4. Verify: Quiz starts fresh (no previous answers)
5. Complete and submit again (score 8/10)
6. Verify: New attempt is recorded
7. Check scoreboard: Should show 8 (best score), not 14 (sum)
8. View attempt history
9. Verify: Both attempts visible with scores

```bash
# API test - View quiz history
curl http://localhost:8000/quizzes/{QUIZ_ID}/history \
  -b "session_id=YOUR_SESSION"

# Should return both attempts, with is_best flag on the 8/10 one
```

### Validation Tests

```bash
# Test: Cannot submit with missing answers
curl -X POST http://localhost:8000/attempts/{ATTEMPT_ID}/submit \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{
    "answers": [
      {"question_id": "q1-uuid", "selected_answer_id": "a1-uuid"}
    ]
  }'
# Expected: 400 error if quiz has more than 1 question

# Test: Cannot submit already-submitted attempt
curl -X POST http://localhost:8000/attempts/{SUBMITTED_ATTEMPT_ID}/submit \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{"answers": [...]}'
# Expected: 400 error - "Attempt already submitted"

# Test: Cannot access another user's attempt
curl http://localhost:8000/attempts/{OTHER_USER_ATTEMPT_ID}/results \
  -b "session_id=YOUR_SESSION"
# Expected: 403 error - "Not authorized"

# Test: Cannot get results before submission
curl http://localhost:8000/attempts/{IN_PROGRESS_ATTEMPT}/results \
  -b "session_id=YOUR_SESSION"
# Expected: 400 error - "Attempt not yet submitted"
```

## API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/quizzes/browse` | GET | Yes | List available quizzes |
| `/quizzes/{id}/start` | POST | Yes | Start new attempt |
| `/attempts/{id}` | GET | Yes | Get in-progress attempt |
| `/attempts/{id}/submit` | POST | Yes | Submit answers |
| `/attempts/{id}/results` | GET | Yes | Get results (after submit) |
| `/quizzes/{id}/history` | GET | Yes | User's attempts for quiz |
| `/my-attempts` | GET | Yes | All user's attempts |
| `/browse` | GET | Yes | HTML browser page |
| `/take/{id}` | GET | Yes | HTML quiz-taking page |
| `/results/{id}` | GET | Yes | HTML results page |

## Common Issues

### "Quiz not found"

- Verify the quiz_id is valid
- Quiz may have been deleted

### "Attempt not found"

- Verify the attempt_id is valid
- Attempt belongs to another user

### "All questions must be answered"

- Submit endpoint requires an answer for every question
- Check the total question count matches your answers array

### "Attempt already submitted"

- Each attempt can only be submitted once
- Start a new attempt to retake the quiz

### "Not authorized"

- You can only access your own attempts
- Log in as the correct user

## Test Commands

```bash
# Run all quiz-taking tests
pytest backend/tests -k attempt -v

# Run contract tests only
pytest backend/tests/contract/test_attempt_api.py -v

# Run integration tests
pytest backend/tests/integration/test_quiz_taking.py -v

# Run with coverage
pytest backend/tests -k attempt --cov=src.services.attempt --cov=src.api.attempt
```

## Scoreboard Integration

After submission, the scoreboard is automatically updated:

1. If first attempt at quiz: full score added to total
2. If better than previous best: difference added to total
3. If worse than previous best: no change to total

```bash
# Check scoreboard after submission
curl http://localhost:8000/scoreboard \
  -b "session_id=YOUR_SESSION"
```

## Next Steps

After verifying quiz-taking works:

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement tests first (TDD per constitution)
3. Build P1 stories (start/complete, change answers) first
4. Then P2 (results, browse), then P3 (retake)
5. Verify scoreboard integration works correctly
