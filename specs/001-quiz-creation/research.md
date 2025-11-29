# Research: Quiz Creation Feature

**Feature**: 001-quiz-creation
**Date**: 2025-11-29

## Research Tasks

### 1. Quiz Data Model Structure

**Question**: How to model hierarchical quiz → questions → answers in SQLite?

**Decision**: Three separate tables with foreign key relationships.

**Rationale**:
- Clear separation of concerns
- Efficient queries for individual entities
- Cascade delete simplifies cleanup
- Aligns with RESTful resource modeling

**Alternatives Considered**:
- Single denormalized table: Complex queries, data duplication
- JSON blob for questions: Loses relational benefits, harder to query

**Implementation Notes**:
```
quizzes (id, title, owner_id, created_at, updated_at)
    └── questions (id, quiz_id, text, display_order, points)
            └── answers (id, question_id, text, is_correct)
```

### 2. Question Ordering Strategy

**Question**: How to handle question display order?

**Decision**: Integer `display_order` column, reordered on save.

**Rationale**:
- Simple integer comparison for sorting
- Allows reordering without changing IDs
- Frontend can drag-and-drop; backend normalizes on save

**Alternatives Considered**:
- Linked list (next_id): Complex updates, harder to bulk reorder
- Alphabetical: No control over order
- Timestamp-based: Can't reorder

**Implementation Notes**:
- On quiz save, normalize order: 1, 2, 3... (no gaps)
- Query: `ORDER BY display_order ASC`

### 3. Answer Option Validation

**Question**: How to enforce "exactly one correct answer" per question?

**Decision**: Application-level validation in service layer.

**Rationale**:
- Database constraints for "exactly one" are complex
- Service layer can provide clear error messages
- Validation runs before any database write

**Alternatives Considered**:
- Database CHECK constraint: SQLite limitations, poor error messages
- Frontend-only validation: Can be bypassed, security risk

**Validation Logic**:
```python
def validate_question(question: QuestionCreate) -> None:
    correct_count = sum(1 for a in question.answers if a.is_correct)
    if correct_count != 1:
        raise ValueError("Question must have exactly one correct answer")
    if not (2 <= len(question.answers) <= 6):
        raise ValueError("Question must have 2-6 answer options")
```

### 4. Quiz Ownership and Authorization

**Question**: How to enforce that only quiz owners can edit/delete?

**Decision**: Check `quiz.owner_id == current_user.id` in service layer.

**Rationale**:
- Simple comparison, no complex ACL system
- Clear separation: service handles authz, API handles authn
- Aligns with simplicity principle (YAGNI)

**Alternatives Considered**:
- Role-based ACL: Overkill for owner-only access
- Database row-level security: SQLite doesn't support this

**Implementation Notes**:
```python
def get_quiz_for_edit(quiz_id: UUID, user_id: UUID) -> Quiz:
    quiz = db.get(Quiz, quiz_id)
    if not quiz:
        raise NotFound("Quiz not found")
    if quiz.owner_id != user_id:
        raise Forbidden("Not authorized to edit this quiz")
    return quiz
```

### 5. Quiz Save Strategy (Create vs Update)

**Question**: How to handle nested quiz/question/answer saves atomically?

**Decision**: Transaction wrapper with full replacement strategy.

**Rationale**:
- SQLite supports transactions
- Full replacement simplifies logic (delete old questions, insert new)
- Atomic: either all changes succeed or none

**Alternatives Considered**:
- Partial update (diff): Complex tracking, edge cases
- Separate API calls per entity: No atomicity

**Implementation Notes**:
```python
def save_quiz(quiz_data: QuizUpdate, existing_quiz: Quiz) -> Quiz:
    with db.begin():
        # Delete existing questions (cascades to answers)
        db.execute(delete(Question).where(Question.quiz_id == existing_quiz.id))
        # Update quiz metadata
        existing_quiz.title = quiz_data.title
        existing_quiz.updated_at = datetime.utcnow()
        # Insert new questions and answers
        for i, q in enumerate(quiz_data.questions):
            question = Question(quiz_id=existing_quiz.id, text=q.text, display_order=i+1)
            db.add(question)
            for a in q.answers:
                db.add(Answer(question_id=question.id, text=a.text, is_correct=a.is_correct))
    return existing_quiz
```

### 6. Frontend Form for Dynamic Questions

**Question**: How to handle dynamic add/remove questions in plain HTML/JS?

**Decision**: Vanilla JS with DOM manipulation and form arrays.

**Rationale**:
- No framework dependency
- Form data sent as JSON to API
- Simple enough for CRUD operations

**Alternatives Considered**:
- HTML form arrays (name="questions[0][text]"): Parsing complexity
- React/Vue: Framework overhead, violates user requirement

**Implementation Notes**:
- JS maintains local state array of questions
- "Add Question" appends to array, re-renders
- "Remove Question" filters array, re-renders
- "Save" serializes to JSON, POSTs to API

## Dependencies Identified

| Dependency | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| FastAPI | 0.100+ | Web framework | Constitution-mandated |
| Uvicorn | 0.20+ | ASGI server | Standard FastAPI runner |
| SQLAlchemy | 2.0+ | ORM/Query builder | Type-safe DB access |
| Jinja2 | 3.0+ | HTML templating | Built into FastAPI |
| Pydantic | 2.0+ | Validation | Built into FastAPI |
| pytest | 7.0+ | Testing | Constitution-mandated |
| pytest-asyncio | 0.21+ | Async test support | FastAPI is async |
| httpx | 0.24+ | Test client | FastAPI test standard |

## Open Questions Resolved

All technical decisions made:

1. **Data model**: Three normalized tables with FK relationships
2. **Question ordering**: Integer display_order column
3. **Answer validation**: Application-level, exactly one correct
4. **Authorization**: Owner check in service layer
5. **Save strategy**: Transactional full replacement
6. **Frontend forms**: Vanilla JS with JSON serialization
