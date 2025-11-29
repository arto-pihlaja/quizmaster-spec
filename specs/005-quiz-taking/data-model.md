# Data Model: Quiz Taking

**Feature**: 005-quiz-taking
**Date**: 2025-11-29
**Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Entity Overview

```
┌──────────────────┐      ┌──────────────────┐
│      users       │      │     quizzes      │
├──────────────────┤      ├──────────────────┤
│ id (PK)          │      │ id (PK)          │
│ display_name     │      │ title            │
│ ...              │      │ owner_id         │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         │ 1                       │ 1
         │                         │
         ▼ *                       ▼ *
┌──────────────────────────────────────────────┐
│                quiz_attempts                  │
├──────────────────────────────────────────────┤
│ id (PK)                                      │
│ user_id (FK) ─────────────────────────────┐  │
│ quiz_id (FK, nullable) ────────────────┐  │  │
│ quiz_title_snapshot                    │  │  │
│ total_points_possible                  │  │  │
│ total_score                            │  │  │
│ started_at                             │  │  │
│ submitted_at                           │  │  │
│ status (in_progress | submitted)       │  │  │
└────────────────────────────────────────┴──┴──┘
         │
         │ 1
         │
         ▼ *
┌──────────────────────────────────────────────┐
│              attempt_answers                  │
├──────────────────────────────────────────────┤
│ id (PK)                                      │
│ attempt_id (FK) ─────────────────────────────┤
│ question_id (FK, nullable)                   │
│ question_order                               │
│ question_text_snapshot                       │
│ question_points                              │
│ selected_answer_text                         │
│ correct_answer_text                          │
│ is_correct                                   │
│ points_earned                                │
└──────────────────────────────────────────────┘
```

## Entity Definitions

### QuizAttempt

Represents a single attempt by a user to complete a quiz.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → users.id, NOT NULL | User taking the quiz |
| quiz_id | UUID | FK → quizzes.id, NULL | Original quiz (nullable for deleted quizzes) |
| quiz_title_snapshot | VARCHAR(200) | NOT NULL | Quiz title at start time |
| total_points_possible | INTEGER | NOT NULL | Sum of all question points |
| total_score | INTEGER | NULL | Points earned (NULL until submitted) |
| started_at | DATETIME | NOT NULL | When attempt began |
| submitted_at | DATETIME | NULL | When submitted (NULL if in-progress) |
| status | VARCHAR(20) | NOT NULL | 'in_progress' or 'submitted' |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (user_id, quiz_id) - For user's attempts on a quiz
- INDEX (user_id, submitted_at DESC) - For user's recent attempts
- INDEX (quiz_id) - For quiz statistics

**Notes**:
- quiz_id is nullable to support quiz deletion after attempt
- Snapshot fields preserve quiz state at start time
- status transitions: in_progress → submitted (one-way)

### AttemptAnswer

Stores the user's answer for each question in an attempt.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| attempt_id | UUID | FK → quiz_attempts.id, NOT NULL | Parent attempt |
| question_id | UUID | FK → questions.id, NULL | Original question (nullable) |
| question_order | INTEGER | NOT NULL | Position in quiz (1-indexed) |
| question_text_snapshot | VARCHAR(1000) | NOT NULL | Question text at start |
| question_points | INTEGER | NOT NULL | Points available for question |
| selected_answer_text | VARCHAR(500) | NULL | User's selected answer (NULL until answered) |
| correct_answer_text | VARCHAR(500) | NOT NULL | Correct answer text |
| is_correct | BOOLEAN | NULL | Whether answer was correct (NULL until submitted) |
| points_earned | INTEGER | NULL | Points earned (NULL until submitted) |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (attempt_id, question_order) - For ordered retrieval
- UNIQUE (attempt_id, question_id) - One answer per question

**Notes**:
- Snapshots enable quiz to be modified/deleted post-attempt
- is_correct and points_earned populated on submission
- selected_answer_text NULL means unanswered

## SQLite Schema

```sql
-- Quiz attempts table
CREATE TABLE quiz_attempts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id TEXT REFERENCES quizzes(id) ON DELETE SET NULL,
    quiz_title_snapshot TEXT NOT NULL,
    total_points_possible INTEGER NOT NULL,
    total_score INTEGER,
    started_at TEXT NOT NULL,
    submitted_at TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress',
    CHECK (status IN ('in_progress', 'submitted')),
    CHECK (total_points_possible > 0),
    CHECK (total_score IS NULL OR total_score >= 0)
);

CREATE INDEX idx_attempts_user_quiz ON quiz_attempts(user_id, quiz_id);
CREATE INDEX idx_attempts_user_recent ON quiz_attempts(user_id, submitted_at DESC);
CREATE INDEX idx_attempts_quiz ON quiz_attempts(quiz_id);

-- Attempt answers table
CREATE TABLE attempt_answers (
    id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id TEXT REFERENCES questions(id) ON DELETE SET NULL,
    question_order INTEGER NOT NULL,
    question_text_snapshot TEXT NOT NULL,
    question_points INTEGER NOT NULL,
    selected_answer_text TEXT,
    correct_answer_text TEXT NOT NULL,
    is_correct INTEGER,
    points_earned INTEGER,
    CHECK (question_order >= 1),
    CHECK (question_points >= 1),
    CHECK (points_earned IS NULL OR points_earned >= 0)
);

CREATE INDEX idx_attempt_answers_attempt ON attempt_answers(attempt_id, question_order);
CREATE UNIQUE INDEX idx_attempt_answers_unique ON attempt_answers(attempt_id, question_id);
```

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| QuizAttempt | User | Many-to-One | User has many attempts |
| QuizAttempt | Quiz | Many-to-One (optional) | Quiz has many attempts |
| AttemptAnswer | QuizAttempt | Many-to-One | Attempt has many answers |
| AttemptAnswer | Question | Many-to-One (optional) | Question referenced in answer |

## Cascade Behavior

| Parent | Child | On Delete |
|--------|-------|-----------|
| users | quiz_attempts | CASCADE (delete user's attempts) |
| quizzes | quiz_attempts | SET NULL (keep attempts, clear reference) |
| quiz_attempts | attempt_answers | CASCADE (delete attempt's answers) |
| questions | attempt_answers | SET NULL (keep answers, clear reference) |

## State Transitions

### Attempt Lifecycle

```
[Start Quiz] ──→ in_progress
                    │
                    │ (user answers questions - client-side only)
                    │
                    ▼
[Submit Quiz] ──→ submitted
                    │
                    ├──→ Score calculated
                    ├──→ Answers marked correct/incorrect
                    └──→ Scoreboard updated (if best score)
```

### Answer States

```
[Quiz Started] ──→ AttemptAnswer created with snapshots
                       │ selected_answer_text = NULL
                       │ is_correct = NULL
                       │ points_earned = NULL
                       │
[User Selects] ────────┘ (client-side only, not persisted)
                       │
[Submit] ──────────────┴──→ selected_answer_text set
                            is_correct calculated
                            points_earned calculated
```

## Query Patterns

### Start Quiz (Create Attempt with Snapshots)

```sql
-- 1. Create attempt
INSERT INTO quiz_attempts (id, user_id, quiz_id, quiz_title_snapshot,
                          total_points_possible, started_at, status)
SELECT :attempt_id, :user_id, q.id, q.title,
       (SELECT SUM(points) FROM questions WHERE quiz_id = q.id),
       :now, 'in_progress'
FROM quizzes q WHERE q.id = :quiz_id;

-- 2. Create answer snapshots for all questions
INSERT INTO attempt_answers (id, attempt_id, question_id, question_order,
                            question_text_snapshot, question_points,
                            correct_answer_text)
SELECT :answer_id, :attempt_id, q.id, q.display_order, q.text, q.points,
       (SELECT a.text FROM answers a WHERE a.question_id = q.id AND a.is_correct = 1)
FROM questions q
WHERE q.quiz_id = :quiz_id
ORDER BY q.display_order;
```

### Submit Quiz

```sql
-- 1. Update answers with user selections and correctness
UPDATE attempt_answers
SET selected_answer_text = :selected_text,
    is_correct = (selected_answer_text = correct_answer_text),
    points_earned = CASE WHEN selected_answer_text = correct_answer_text
                        THEN question_points ELSE 0 END
WHERE attempt_id = :attempt_id AND question_id = :question_id;

-- 2. Calculate total score
UPDATE quiz_attempts
SET total_score = (SELECT SUM(points_earned) FROM attempt_answers WHERE attempt_id = :attempt_id),
    submitted_at = :now,
    status = 'submitted'
WHERE id = :attempt_id;

-- 3. Update scoreboard if new best (see 004-scoreboard integration)
```

### Get User's Best Score for Quiz

```sql
SELECT MAX(total_score) as best_score
FROM quiz_attempts
WHERE user_id = :user_id AND quiz_id = :quiz_id AND status = 'submitted';
```

### Get User's Attempt History for Quiz

```sql
SELECT id, quiz_title_snapshot, total_score, total_points_possible,
       submitted_at, status
FROM quiz_attempts
WHERE user_id = :user_id AND quiz_id = :quiz_id
ORDER BY submitted_at DESC;
```

### Get Attempt Results with All Answers

```sql
SELECT qa.*, aa.question_order, aa.question_text_snapshot, aa.question_points,
       aa.selected_answer_text, aa.correct_answer_text, aa.is_correct, aa.points_earned
FROM quiz_attempts qa
JOIN attempt_answers aa ON aa.attempt_id = qa.id
WHERE qa.id = :attempt_id
ORDER BY aa.question_order;
```

### Browse Available Quizzes

```sql
SELECT q.id, q.title, COUNT(qu.id) as question_count,
       (SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = q.id
        AND user_id = :user_id AND status = 'submitted') as user_attempts
FROM quizzes q
LEFT JOIN questions qu ON qu.quiz_id = q.id
GROUP BY q.id
ORDER BY q.created_at DESC;
```

## Pydantic Schemas

### Request Schemas

```python
class StartQuizRequest(BaseModel):
    quiz_id: UUID

class AnswerSubmission(BaseModel):
    question_id: UUID
    selected_answer_id: UUID

class SubmitQuizRequest(BaseModel):
    attempt_id: UUID
    answers: list[AnswerSubmission] = Field(min_length=1)
```

### Response Schemas

```python
class QuizBrowserItem(BaseModel):
    id: UUID
    title: str
    question_count: int
    user_attempts: int  # How many times current user completed it
    user_best_score: int | None  # User's best score if attempted

class QuizTakingQuestion(BaseModel):
    id: UUID
    order: int
    text: str
    answers: list[QuizTakingAnswer]  # No is_correct field!

class QuizTakingAnswer(BaseModel):
    id: UUID
    text: str
    # NOTE: is_correct intentionally omitted

class QuizTakingView(BaseModel):
    attempt_id: UUID
    quiz_title: str
    questions: list[QuizTakingQuestion]
    total_questions: int

class AttemptResultAnswer(BaseModel):
    question_order: int
    question_text: str
    question_points: int
    selected_answer: str | None
    correct_answer: str
    is_correct: bool
    points_earned: int

class AttemptResult(BaseModel):
    attempt_id: UUID
    quiz_title: str
    total_score: int
    total_points_possible: int
    percentage: float
    submitted_at: datetime
    answers: list[AttemptResultAnswer]

class AttemptHistoryItem(BaseModel):
    attempt_id: UUID
    quiz_title: str
    total_score: int
    total_points_possible: int
    percentage: float
    submitted_at: datetime
    is_best: bool
```

## Integration with Scoreboard (004)

When a quiz is submitted, integrate with UserScore:

```python
async def update_scoreboard_on_submit(user_id: UUID, quiz_id: UUID, new_score: int):
    """Update user's total score if this attempt is a new best."""
    # Get previous best for this quiz
    previous_best = await get_best_score(user_id, quiz_id, exclude_latest=True)

    if previous_best is None:
        # First completion of this quiz
        await increment_user_total_score(user_id, new_score)
    elif new_score > previous_best:
        # New best score - add the improvement
        improvement = new_score - previous_best
        await increment_user_total_score(user_id, improvement)
    # else: not a new best, no scoreboard change
```
