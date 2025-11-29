# Quickstart: Scoreboard Feature

**Feature**: 004-scoreboard
**Date**: 2025-11-29

## Prerequisites

- Python 3.11+ installed
- QuizMaster backend running (from previous features)
- SQLite database initialized with user and quiz tables
- At least one user account created
- (Optional) Quiz completion data for testing rankings

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

Run the migration to add the `user_scores` table:

```bash
# If using Alembic
alembic upgrade head

# Or run the migration script directly
python -m src.db.migrations.add_user_scores
```

### 3. Seed Test Data (Optional)

For development, seed some score data:

```bash
python -m src.db.seed_scores --users 100
```

This creates 100 test users with random scores for testing pagination and ranking.

## Running the Feature

### Start the Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Scoreboard

- **Browser**: http://localhost:8000/scoreboard
- **API (JSON)**: http://localhost:8000/api/scoreboard
- **My Rank**: http://localhost:8000/api/scoreboard/my-rank (requires login)

## Verification Steps

### User Story 1: View the Scoreboard (P1)

1. Open http://localhost:8000/scoreboard in your browser
2. Verify: Page displays a table with Rank, Name, Score columns
3. Verify: Users are sorted by score (highest first)
4. Verify: Page loads within 2 seconds

```bash
# API test
curl http://localhost:8000/api/scoreboard | jq '.entries[:3]'
```

Expected: JSON array with top 3 users, each having `rank`, `display_name`, `total_score`.

### User Story 2: See Score Details (P2)

1. View any scoreboard entry
2. Verify: Each row shows rank number, display name, and total score
3. Verify: Tied scores have the same rank (e.g., 1, 2, 2, 4)

```bash
# Check competition ranking
curl http://localhost:8000/api/scoreboard | jq '.entries | map({rank, score: .total_score})'
```

### User Story 3: Find Myself (P2)

1. Log in to your account
2. Navigate to http://localhost:8000/scoreboard
3. Verify: Your row is highlighted (different background color)
4. Click "Jump to My Rank" button
5. Verify: Page scrolls/navigates to your position

```bash
# Test my-rank endpoint (requires session cookie)
curl -b "session_id=YOUR_SESSION" http://localhost:8000/api/scoreboard/my-rank
```

Expected: `{"user_id": "...", "rank": 42, "page": 1, "total_score": 1500}`

### User Story 4: Refresh Data (P3)

1. Open scoreboard in browser
2. Complete a quiz in another tab (earning points)
3. Click the "Refresh" button on scoreboard
4. Verify: Your score updates without full page reload
5. Verify: Table body updates, no page flicker

## API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/scoreboard` | GET | No | HTML page |
| `/api/scoreboard` | GET | No | JSON data |
| `/api/scoreboard?page=2` | GET | No | Page 2 of results |
| `/api/scoreboard/my-rank` | GET | Yes | Current user's rank |
| `/api/scoreboard/stats` | GET | No | Aggregate statistics |

## Common Issues

### "No scores displayed"

- Ensure `user_scores` table exists
- Run score aggregation: `python -m src.services.scoreboard.recalculate_all`

### "My rank shows 401"

- You must be logged in (session cookie required)
- Verify session: `curl -b "session_id=..." http://localhost:8000/api/auth/me`

### "Slow page load"

- Check database indexes: `sqlite3 quizmaster.db ".indexes user_scores"`
- Expected index: `idx_user_scores_ranking`

## Test Commands

```bash
# Run all scoreboard tests
pytest backend/tests -k scoreboard -v

# Run contract tests only
pytest backend/tests/contract/test_scoreboard.py -v

# Run with coverage
pytest backend/tests -k scoreboard --cov=src.services.scoreboard --cov=src.api.scoreboard
```

## Next Steps

After verifying the scoreboard works:

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement tests first (TDD per constitution)
3. Build P1 story, verify, then proceed to P2/P3
