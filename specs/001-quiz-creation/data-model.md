# Data Model: Quiz Creation

**Feature**: 001-quiz-creation
**Date**: 2025-11-29

## Entities

### Quiz

The core entity representing a quiz created by a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| title | VARCHAR(200) | NOT NULL | Quiz title (1-200 chars) |
| owner_id | UUID | FK(users.id), NOT NULL | Creator of the quiz |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last modification timestamp |

**Indexes**:
- `idx_quizzes_owner`: `(owner_id)` - For "my quizzes" queries
- `idx_quizzes_created`: `(created_at DESC)` - For recent quizzes

### Question

A single question within a quiz.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| quiz_id | UUID | FK(quizzes.id), NOT NULL | Parent quiz |
| text | VARCHAR(1000) | NOT NULL | Question text (1-1000 chars) |
| display_order | INTEGER | NOT NULL | Position in quiz (1-indexed) |
| points | INTEGER | NOT NULL, DEFAULT 1 | Points for correct answer (1-100) |

**Indexes**:
- `idx_questions_quiz`: `(quiz_id, display_order)` - For ordered retrieval

**Constraints**:
- `CHECK (display_order >= 1)`
- `CHECK (points >= 1 AND points <= 100)`

### Answer

A possible answer option for a question.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| question_id | UUID | FK(questions.id), NOT NULL | Parent question |
| text | VARCHAR(500) | NOT NULL | Answer text (1-500 chars) |
| is_correct | BOOLEAN | NOT NULL, DEFAULT FALSE | True if correct answer |
| display_order | INTEGER | NOT NULL | Position in options (1-indexed) |

**Indexes**:
- `idx_answers_question`: `(question_id, display_order)` - For ordered retrieval

## Relationships

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   users     │ 1───* │     quizzes     │ 1───* │   questions     │
│             │       │                 │       │                 │
│ id (PK)     │◄──────│ owner_id (FK)   │       │ quiz_id (FK)    │──────┐
│ display_name│       │ id (PK)         │◄──────│ id (PK)         │      │
│ ...         │       │ title           │       │ text            │      │
└─────────────┘       │ created_at      │       │ display_order   │      │
                      │ updated_at      │       │ points          │      │
                      └─────────────────┘       └─────────────────┘      │
                                                        │                │
                                                        │ 1              │
                                                        │                │
                                                        ▼ *              │
                                                ┌─────────────────┐      │
                                                │    answers      │      │
                                                │                 │      │
                                                │ question_id(FK) │──────┘
                                                │ id (PK)         │
                                                │ text            │
                                                │ is_correct      │
                                                │ display_order   │
                                                └─────────────────┘
```

## Cascade Rules

| Parent | Child | On Delete |
|--------|-------|-----------|
| users | quizzes | CASCADE (delete user's quizzes) |
| quizzes | questions | CASCADE (delete quiz's questions) |
| questions | answers | CASCADE (delete question's answers) |

## Validation Rules

### Quiz

| Field | Rule | Error Message |
|-------|------|---------------|
| title | 1-200 characters | "Title must be 1-200 characters" |
| title | Not empty after trim | "Title is required" |
| questions | 1-100 items | "Quiz must have 1-100 questions" |

### Question

| Field | Rule | Error Message |
|-------|------|---------------|
| text | 1-1000 characters | "Question must be 1-1000 characters" |
| text | Not empty after trim | "Question text is required" |
| answers | 2-6 items | "Question must have 2-6 answers" |
| answers | Exactly 1 is_correct=true | "Question must have exactly one correct answer" |
| points | 1-100 | "Points must be between 1 and 100" |

### Answer

| Field | Rule | Error Message |
|-------|------|---------------|
| text | 1-500 characters | "Answer must be 1-500 characters" |
| text | Not empty after trim | "Answer text is required" |

## State Transitions

### Quiz Lifecycle

```
[Create] → Draft (id assigned, questions added)
              │
              ▼
[Save] ───→ Saved (persisted to DB)
              │
              ▼
[Edit] ───→ Draft (loaded for modification)
              │
              ▼
[Save] ───→ Saved (updated in DB)
              │
              ▼
[Delete] ──→ (removed from DB, cascade deletes questions/answers)
```

### Question/Answer Management

```
[Add Question] → Question added to in-memory quiz
                     │
[Add Answer] ────────┼──→ Answer added to in-memory question
                     │
[Mark Correct] ──────┼──→ One answer marked is_correct=true
                     │
[Remove Answer] ─────┼──→ Answer removed from in-memory question
                     │
[Remove Question] ───┼──→ Question removed from in-memory quiz
                     │
[Save Quiz] ─────────┴──→ All changes persisted atomically
```

## Query Patterns

### Get User's Quizzes

```sql
SELECT q.id, q.title, q.created_at, q.updated_at,
       COUNT(qu.id) as question_count
FROM quizzes q
LEFT JOIN questions qu ON qu.quiz_id = q.id
WHERE q.owner_id = :user_id
GROUP BY q.id
ORDER BY q.updated_at DESC;
```

### Get Quiz with All Details

```sql
-- Quiz
SELECT * FROM quizzes WHERE id = :quiz_id;

-- Questions
SELECT * FROM questions WHERE quiz_id = :quiz_id ORDER BY display_order;

-- Answers (for all questions)
SELECT a.* FROM answers a
JOIN questions q ON a.question_id = q.id
WHERE q.quiz_id = :quiz_id
ORDER BY q.display_order, a.display_order;
```

### Delete Quiz

```sql
-- Cascade handles questions and answers automatically
DELETE FROM quizzes WHERE id = :quiz_id AND owner_id = :user_id;
```

## Pydantic Schemas

### Request Schemas

```python
class AnswerCreate(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    is_correct: bool = False

class QuestionCreate(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    answers: list[AnswerCreate] = Field(min_length=2, max_length=6)
    points: int = Field(default=1, ge=1, le=100)

class QuizCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    questions: list[QuestionCreate] = Field(min_length=1, max_length=100)
```

### Response Schemas

```python
class AnswerResponse(BaseModel):
    id: UUID
    text: str
    is_correct: bool

class QuestionResponse(BaseModel):
    id: UUID
    text: str
    answers: list[AnswerResponse]
    display_order: int
    points: int

class QuizResponse(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    questions: list[QuestionResponse]
    created_at: datetime
    updated_at: datetime

class QuizListItem(BaseModel):
    id: UUID
    title: str
    question_count: int
    created_at: datetime
    updated_at: datetime
```
