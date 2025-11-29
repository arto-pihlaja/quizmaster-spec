# Research: Quiz Taking

**Feature**: 005-quiz-taking
**Date**: 2025-11-29
**Status**: Complete

## Research Questions

### RQ-001: Quiz Version Snapshotting Strategy

**Question**: How should we handle the requirement that users see the quiz version they started with, even if it's modified during their attempt?

**Options Considered**:
1. **Copy-on-start**: Deep copy quiz/questions/answers into attempt tables when user starts
2. **Reference with version ID**: Add version column to quiz, store version reference in attempt
3. **Immutable quiz after first attempt**: Prevent quiz edits once any attempt exists
4. **No snapshotting**: User sees current version (reject requirement)

**Decision**: Copy-on-start (denormalized snapshot)

**Rationale**:
- Simplest to implement: just copy question text, answers, and correct answer ID at start time
- No complex versioning logic needed
- Supports quiz deletion (attempt data is self-contained)
- Matches spec requirement: "user sees quiz as it was when they started"
- Storage cost is acceptable (text data is small)

**Implementation Notes**:
- `quiz_attempts` stores: quiz_id (reference only), quiz_title_snapshot, total_points_possible
- `attempt_answers` stores: question_text_snapshot, answer_text_snapshot, correct_answer_text_snapshot, is_correct, points_earned
- Original quiz can be modified/deleted without affecting in-progress attempts
- Submission validates against snapshot, not current quiz

---

### RQ-002: Answer Storage During Quiz Taking

**Question**: Should answers be stored server-side during quiz taking, or only on submission?

**Options Considered**:
1. **Client-only until submit**: JavaScript holds answers, sent on submit
2. **Server-side draft**: Save answers to DB as user selects them (auto-save)
3. **Hybrid**: Local storage + periodic sync to server

**Decision**: Client-only until submit

**Rationale**:
- Simplest implementation (YAGNI principle)
- Spec says "unsaved progress is lost" on session expiry - this is acceptable
- No need for partial attempt records cluttering database
- Reduces server load during quiz taking
- Single atomic submission transaction

**Implementation Notes**:
- JavaScript object holds `{question_id: selected_answer_id}` mapping
- On submit: POST entire answer set to server
- Server validates all questions answered, calculates score, saves attempt
- No partial saves or draft state needed

---

### RQ-003: Score Calculation and Scoreboard Update

**Question**: How should score calculation and scoreboard update work on submission?

**Options Considered**:
1. **Synchronous in transaction**: Calculate score, save attempt, update scoreboard in one transaction
2. **Async background job**: Save attempt, queue scoreboard update
3. **Materialized view**: Let database compute totals on demand

**Decision**: Synchronous in transaction

**Rationale**:
- Spec requires "scoreboard totals update within 5 seconds" - synchronous achieves this
- SQLite doesn't support true async well anyway
- Atomic transaction ensures consistency
- Simple to implement and test
- Scale (10k users) doesn't require async optimization yet

**Implementation Notes**:
```python
async def submit_quiz(user_id, quiz_id, answers):
    async with db.transaction():
        # 1. Validate all questions answered
        # 2. Calculate score (compare to snapshot correct answers)
        # 3. Save QuizAttempt with total_score
        # 4. Save AttemptAnswers with per-question results
        # 5. Update UserScore if this is new best for quiz
    return attempt_with_results
```

---

### RQ-004: Best Score Tracking for Scoreboard

**Question**: How should we track only the best score per quiz for scoreboard totals?

**Options Considered**:
1. **Compute on demand**: `MAX(score) GROUP BY quiz_id` query each time
2. **Best score column on attempt**: Flag best attempt per user/quiz
3. **Separate best_scores table**: Store user_id, quiz_id, best_score, attempt_id
4. **Update UserScore table**: From 004-scoreboard, increment/decrement total

**Decision**: Compute best on submit, update UserScore

**Rationale**:
- UserScore table already exists from 004-scoreboard feature
- On submission: compare new score to previous best for this quiz
- If new score > old best: update UserScore.total_score by difference
- Efficient: O(1) lookup for scoreboard display
- Handles retakes correctly

**Implementation Notes**:
```python
# On submission:
previous_best = get_best_score(user_id, quiz_id)  # MAX query or NULL
new_score = calculate_score(answers)

if previous_best is None:
    # First attempt: add full score
    increment_user_score(user_id, new_score)
elif new_score > previous_best:
    # New best: add the difference
    increment_user_score(user_id, new_score - previous_best)
# else: no update (worse than previous best)
```

---

### RQ-005: Concurrent Submission Handling (Same User, Multiple Tabs)

**Question**: How should we handle the edge case of same user submitting quiz from multiple tabs?

**Options Considered**:
1. **Last write wins**: Accept both submissions, both count as attempts
2. **First write wins**: Second submission fails with error
3. **Optimistic locking**: Check for existing submission, reject duplicates
4. **Prevent at start**: Only one in-progress attempt allowed per user/quiz

**Decision**: Last write wins (both submissions accepted)

**Rationale**:
- Spec says "last submission wins; other tab shows error if submitted after"
- But simpler: just accept both as separate attempts
- Both attempts recorded (spec: "record all attempts for history")
- Best score calculation handles which one counts
- No complex locking needed

**Implementation Notes**:
- No prevention mechanism needed
- Each submission creates a new QuizAttempt
- User sees their latest attempt's results
- Best score is recalculated including all attempts
- History page shows all attempts

---

### RQ-006: Quiz Deletion During In-Progress Attempt

**Question**: How should we handle quiz deletion while someone is taking it?

**Options Considered**:
1. **Block deletion**: Prevent if any in-progress attempts exist
2. **Graceful failure**: Submission fails with "quiz no longer exists" message
3. **Allow completion**: Snapshot allows completion even if original deleted

**Decision**: Allow completion with snapshot (graceful handling)

**Rationale**:
- Snapshot approach (RQ-001) means attempt is self-contained
- User can complete and see results even if original quiz deleted
- No need to track "in-progress" state on quiz
- Simpler than blocking deletions
- Spec says "user receives error" but we can do better with snapshots

**Implementation Notes**:
- Quiz deletion cascades to future attempts (foreign key optional)
- Existing attempt snapshots remain valid
- Submission succeeds using snapshot data
- Results page works from snapshot
- Only scoreboard update might fail if quiz_id reference needed (handle gracefully)

---

## Dependencies Identified

| Dependency | Source | Purpose |
|------------|--------|---------|
| User model | 002-user-management | User authentication and identification |
| Quiz/Question/Answer models | 001-quiz-creation | Quiz structure and correct answers |
| UserScore model | 004-scoreboard | Total score tracking |
| Session authentication | 002-user-management | Protect quiz-taking endpoints |

## Integration Points

### With 001-quiz-creation
- Read Quiz, Question, Answer for quiz browser and taking
- Use question.points for score calculation
- No writes to quiz tables

### With 002-user-management
- Require authenticated user for all endpoints
- User.id as foreign key in attempts

### With 004-scoreboard
- Update UserScore.total_score on submission
- Best-score-per-quiz logic integrated with scoreboard totals

## Open Questions Resolved

- ✅ Quiz snapshotting: Copy-on-start approach
- ✅ Answer storage: Client-only until submit
- ✅ Score calculation: Synchronous in transaction
- ✅ Best score tracking: Update UserScore on submit
- ✅ Concurrent submissions: Accept both, best score wins
- ✅ Quiz deletion: Graceful with snapshot

## Next Steps

Proceed to Phase 1: Generate data model and API contracts.
