# Quickstart: Quiz Creation Feature

**Feature**: 001-quiz-creation
**Date**: 2025-11-29

## Prerequisites

- Python 3.11+ installed
- QuizMaster backend running
- SQLite database initialized
- User authentication working (from 002-user-management)
- At least one test user account

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages (should already be installed from base project):
- fastapi
- uvicorn
- sqlalchemy
- jinja2
- pytest
- pytest-asyncio
- httpx

### 2. Database Migration

Run the migration to add quiz tables:

```bash
# If using Alembic
alembic upgrade head

# Or run the migration script directly
python -m src.db.migrations.add_quiz_tables
```

This creates:
- `quizzes` table
- `questions` table
- `answers` table

### 3. Verify Tables

```bash
sqlite3 quizmaster.db ".schema quizzes"
sqlite3 quizmaster.db ".schema questions"
sqlite3 quizmaster.db ".schema answers"
```

## Running the Feature

### Start the Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Quiz Features

- **My Quizzes**: http://localhost:8000/my-quizzes
- **Create Quiz**: http://localhost:8000/quizzes/new
- **Edit Quiz**: http://localhost:8000/quizzes/{id}/edit
- **API**: http://localhost:8000/quizzes

## Verification Steps

### User Story 1: Create a Basic Quiz (P1)

1. Log in to your account
2. Navigate to http://localhost:8000/quizzes/new
3. Enter title: "Python Basics"
4. Add Question 1:
   - Text: "What is the output of print(1 + 1)?"
   - Answers: "1", "2" (correct), "11", "Error"
5. Click "Add Question"
6. Add Question 2:
   - Text: "Which keyword defines a function?"
   - Answers: "func", "def" (correct), "function", "define"
7. Click "Save Quiz"
8. Verify: Redirected to My Quizzes page
9. Verify: "Python Basics" appears in the list

```bash
# API test - Create quiz
curl -X POST http://localhost:8000/quizzes \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{
    "title": "Test Quiz",
    "questions": [{
      "text": "Sample question?",
      "answers": [
        {"text": "Wrong", "is_correct": false},
        {"text": "Correct", "is_correct": true}
      ]
    }]
  }'
```

Expected: 201 response with quiz ID and full data.

### User Story 2: Edit an Existing Quiz (P2)

1. Go to http://localhost:8000/my-quizzes
2. Click "Edit" on a quiz
3. Verify: Form is pre-filled with existing data
4. Change title from "Python Basics" to "Python Fundamentals"
5. Add a new question
6. Remove an existing question
7. Click "Save"
8. Verify: Changes are saved
9. Verify: Quiz list shows updated title

```bash
# API test - Update quiz
curl -X PUT http://localhost:8000/quizzes/{QUIZ_ID} \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{
    "title": "Updated Title",
    "questions": [{
      "text": "New question?",
      "answers": [
        {"text": "A", "is_correct": true},
        {"text": "B", "is_correct": false}
      ]
    }]
  }'
```

### User Story 3: Delete a Quiz (P3)

1. Go to http://localhost:8000/my-quizzes
2. Click "Delete" on a quiz
3. Verify: Confirmation dialog appears
4. Click "Cancel" - quiz remains
5. Click "Delete" again
6. Click "Confirm"
7. Verify: Quiz is removed from list

```bash
# API test - Delete quiz
curl -X DELETE http://localhost:8000/quizzes/{QUIZ_ID} \
  -b "session_id=YOUR_SESSION"
```

Expected: 204 No Content.

### Validation Tests

```bash
# Test: Cannot save without title
curl -X POST http://localhost:8000/quizzes \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{"title": "", "questions": [...]}'
# Expected: 400 error

# Test: Cannot save with zero questions
curl -X POST http://localhost:8000/quizzes \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{"title": "Empty Quiz", "questions": []}'
# Expected: 400 error

# Test: Question must have exactly one correct answer
curl -X POST http://localhost:8000/quizzes \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION" \
  -d '{
    "title": "Bad Quiz",
    "questions": [{
      "text": "Question?",
      "answers": [
        {"text": "A", "is_correct": false},
        {"text": "B", "is_correct": false}
      ]
    }]
  }'
# Expected: 400 error - "exactly one correct answer"
```

## API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/quizzes` | GET | Yes | List user's quizzes |
| `/quizzes` | POST | Yes | Create new quiz |
| `/quizzes/{id}` | GET | Yes | Get quiz details |
| `/quizzes/{id}` | PUT | Yes | Update quiz |
| `/quizzes/{id}` | DELETE | Yes | Delete quiz |
| `/my-quizzes` | GET | Yes | HTML quiz list page |
| `/quizzes/new` | GET | Yes | HTML create form |
| `/quizzes/{id}/edit` | GET | Yes | HTML edit form |

## Common Issues

### "Not authorized"

- You can only edit/delete quizzes you own
- Verify you're logged in as the quiz creator

### "Validation error"

- Title: 1-200 characters
- Questions: 1-100 per quiz
- Answers: 2-6 per question
- Exactly one answer must be marked correct

### "Quiz not found"

- Check the quiz ID is valid
- Quiz may have been deleted

## Test Commands

```bash
# Run all quiz tests
pytest backend/tests -k quiz -v

# Run contract tests only
pytest backend/tests/contract/test_quiz_api.py -v

# Run with coverage
pytest backend/tests -k quiz --cov=src.services.quiz --cov=src.api.quiz
```

## Next Steps

After verifying quiz creation works:

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement tests first (TDD per constitution)
3. Build P1 story (create), verify, then P2 (edit), then P3 (delete)
4. Proceed to dependent features (Admin Roles for point editing)
