# Data Model: Scoreboard

**Feature**: 004-scoreboard
**Date**: 2025-11-29

## Entities

### UserScore (New - This Feature)

Pre-aggregated score data for efficient scoreboard queries.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| user_id | UUID | PK, FK(users.id) | Reference to user |
| total_score | INTEGER | NOT NULL, DEFAULT 0 | Sum of best quiz attempts |
| quizzes_completed | INTEGER | NOT NULL, DEFAULT 0 | Count of unique quizzes completed |
| last_updated | DATETIME | NOT NULL | When score was last recalculated |

**Indexes**:
- `idx_user_scores_ranking`: `(total_score DESC, user_id)` - For ranked queries

**Notes**:
- One row per user (1:1 with users table)
- Updated when user completes a quiz
- `total_score` = sum of best attempt per quiz (not all attempts)

### ScoreboardEntry (View/Query Result)

Not a persisted entity; computed at query time.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| rank | INTEGER | RANK() window | Competition ranking position |
| user_id | UUID | user_scores.user_id | User identifier |
| display_name | STRING | users.display_name | User's display name |
| total_score | INTEGER | user_scores.total_score | Total points earned |
| quizzes_completed | INTEGER | user_scores.quizzes_completed | Number of quizzes done |

## Relationships

```
┌─────────────┐       ┌─────────────────┐
│   users     │ 1───1 │  user_scores    │
│             │       │                 │
│ id (PK)     │◄──────│ user_id (PK,FK) │
│ display_name│       │ total_score     │
│ email       │       │ quizzes_completed│
│ ...         │       │ last_updated    │
└─────────────┘       └─────────────────┘
        │
        │ 1
        │
        ▼ *
┌─────────────────┐
│  quiz_attempts  │  (from quiz-taking feature)
│                 │
│ id (PK)         │
│ user_id (FK)    │
│ quiz_id (FK)    │
│ score           │
│ completed_at    │
└─────────────────┘
```

## Dependent Entities (From Other Features)

### User (from 002-user-management)

| Field | Type | Used By Scoreboard |
|-------|------|-------------------|
| id | UUID | FK in user_scores |
| display_name | STRING | Shown on scoreboard |
| email | STRING | NOT used (privacy) |

### QuizAttempt (from quiz-taking feature - assumed)

| Field | Type | Used By Scoreboard |
|-------|------|-------------------|
| id | UUID | — |
| user_id | UUID | For score aggregation |
| quiz_id | UUID | For "best attempt" logic |
| score | INTEGER | Summed into total |
| completed_at | DATETIME | — |

## State Transitions

### UserScore Lifecycle

```
[User Registers] → UserScore created with total_score=0
                        │
                        ▼
[User Completes Quiz] → Recalculate total_score
                        │
                        ▼
[User Deletes Account] → UserScore deleted (CASCADE)
```

### Score Update Algorithm

```python
def update_user_score(user_id: UUID) -> None:
    """
    Recalculate user's total score from best quiz attempts.
    Called after each quiz completion.
    """
    # Get best score per quiz for this user
    best_scores = db.query(
        QuizAttempt.quiz_id,
        func.max(QuizAttempt.score).label('best')
    ).filter(
        QuizAttempt.user_id == user_id
    ).group_by(
        QuizAttempt.quiz_id
    ).all()

    total = sum(s.best for s in best_scores)
    count = len(best_scores)

    db.merge(UserScore(
        user_id=user_id,
        total_score=total,
        quizzes_completed=count,
        last_updated=datetime.utcnow()
    ))
```

## Validation Rules

| Entity | Field | Rule | Error Message |
|--------|-------|------|---------------|
| UserScore | total_score | >= 0 | "Score cannot be negative" |
| UserScore | quizzes_completed | >= 0 | "Quiz count cannot be negative" |

## Query Patterns

### Get Scoreboard Page

```sql
WITH ranked AS (
  SELECT
    us.user_id,
    u.display_name,
    us.total_score,
    us.quizzes_completed,
    RANK() OVER (ORDER BY us.total_score DESC, u.display_name ASC) as rank
  FROM user_scores us
  JOIN users u ON us.user_id = u.id
)
SELECT * FROM ranked
ORDER BY rank
LIMIT :page_size OFFSET :offset;
```

### Get User's Rank

```sql
WITH ranked AS (
  SELECT
    user_id,
    RANK() OVER (ORDER BY total_score DESC, display_name ASC) as rank
  FROM user_scores us
  JOIN users u ON us.user_id = u.id
)
SELECT rank FROM ranked WHERE user_id = :user_id;
```

### Get Total User Count

```sql
SELECT COUNT(*) FROM user_scores;
```
