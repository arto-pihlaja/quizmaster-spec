# Tasks: Quiz Taking

**Input**: Design documents from `/specs/005-quiz-taking/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First Development required)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` (per plan.md structure)

---

## Phase 1: Setup

**Purpose**: Database schema and project structure

- [x] T001 Create database migration for quiz_attempts table in backend/src/db/migrations/
- [x] T002 Create database migration for attempt_answers table in backend/src/db/migrations/
- [x] T003 [P] Verify backend/src/models/ directory structure exists
- [x] T004 [P] Verify backend/tests/ directory structure (contract/, integration/, unit/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and schemas that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create QuizAttempt SQLAlchemy model in backend/src/models/attempt.py
- [x] T006 Create AttemptAnswer SQLAlchemy model in backend/src/models/attempt_answer.py
- [x] T007 [P] Create Pydantic request schemas (StartQuizRequest, SubmitRequest, AnswerSubmission) in backend/src/schemas/attempt.py
- [x] T008 [P] Create Pydantic response schemas (QuizTakingView, QuizTakingQuestion, QuizTakingAnswer) in backend/src/schemas/attempt.py
- [x] T009 [P] Create Pydantic response schemas (AttemptResult, AttemptResultAnswer) in backend/src/schemas/attempt.py
- [x] T010 [P] Create Pydantic response schemas (QuizBrowserItem, QuizBrowserResponse) in backend/src/schemas/attempt.py
- [x] T011 [P] Create Pydantic response schemas (AttemptHistoryItem, AttemptHistoryResponse, MyAttemptsResponse) in backend/src/schemas/attempt.py
- [x] T012 Create AttemptService skeleton in backend/src/services/attempt.py
- [x] T013 Register attempt API router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Start and Complete a Quiz (Priority: P1) 🎯 MVP

**Goal**: User can start a quiz, see questions without correct answers, submit answers, and receive a score

**Independent Test**: Start quiz, answer all questions, submit, verify score calculated and saved

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US1] Contract test for POST /quizzes/{quiz_id}/start in backend/tests/contract/test_attempt_api.py
- [x] T015 [P] [US1] Contract test for POST /attempts/{attempt_id}/submit in backend/tests/contract/test_attempt_api.py
- [x] T016 [P] [US1] Unit test for AttemptService.start_quiz() in backend/tests/unit/test_attempt_service.py
- [x] T017 [P] [US1] Unit test for AttemptService.submit_quiz() in backend/tests/unit/test_attempt_service.py
- [x] T018 [US1] Integration test for complete quiz flow in backend/tests/integration/test_quiz_taking.py

### Implementation for User Story 1

- [x] T019 [US1] Implement AttemptService.start_quiz() with snapshot creation in backend/src/services/attempt.py
- [x] T020 [US1] Implement AttemptService.submit_quiz() with score calculation in backend/src/services/attempt.py
- [x] T021 [US1] Implement AttemptService.update_scoreboard() for best-score logic in backend/src/services/attempt.py
- [x] T022 [US1] Implement POST /quizzes/{quiz_id}/start endpoint in backend/src/api/attempt.py
- [x] T023 [US1] Implement POST /attempts/{attempt_id}/submit endpoint in backend/src/api/attempt.py
- [x] T024 [US1] Create quiz_take.html template (questions without correct answers shown) in frontend/templates/quiz_take.html
- [x] T025 [US1] Implement GET /take/{quiz_id} HTML page endpoint in backend/src/api/attempt.py

**Checkpoint**: User Story 1 should be fully functional - users can complete a quiz and get scored

---

## Phase 4: User Story 2 - Change Answers Before Submission (Priority: P1)

**Goal**: User can change any answer before submitting without penalty

**Independent Test**: Select answer A, change to B, submit, verify only B is recorded

### Tests for User Story 2

- [x] T026 [US2] Frontend test for answer selection and change in frontend/tests/test_attempt.js (manual or automated)

### Implementation for User Story 2

- [x] T027 [US2] Create attempt.js with answer tracking object in frontend/static/js/attempt.js
- [x] T028 [US2] Implement answer selection click handlers in frontend/static/js/attempt.js
- [x] T029 [US2] Implement visual feedback for selected answers in frontend/static/js/attempt.js
- [x] T030 [US2] Add validation preventing submit with unanswered questions in frontend/static/js/attempt.js

**Checkpoint**: User Stories 1 AND 2 complete - full quiz-taking flow with answer changes

---

## Phase 5: User Story 3 - View Quiz Results After Submission (Priority: P2)

**Goal**: User sees detailed results after submission with correct/incorrect feedback

**Independent Test**: Submit quiz, verify results page shows score and per-question feedback

### Tests for User Story 3

- [x] T031 [P] [US3] Contract test for GET /attempts/{attempt_id}/results in backend/tests/contract/test_attempt_api.py
- [x] T032 [US3] Integration test for results page in backend/tests/integration/test_quiz_taking.py

### Implementation for User Story 3

- [x] T033 [US3] Implement AttemptService.get_results() in backend/src/services/attempt.py
- [x] T034 [US3] Implement GET /attempts/{attempt_id}/results endpoint in backend/src/api/attempt.py
- [x] T035 [US3] Create quiz_results.html template with score and per-question feedback in frontend/templates/quiz_results.html
- [x] T036 [US3] Implement GET /results/{attempt_id} HTML page endpoint in backend/src/api/attempt.py
- [x] T037 [US3] Add CSS styling for correct/incorrect answer display in frontend/static/css/styles.css

**Checkpoint**: User Stories 1, 2, AND 3 complete - users see detailed feedback after submission

---

## Phase 6: User Story 4 - Browse Available Quizzes (Priority: P2)

**Goal**: User can browse all quizzes with title, question count, and their attempt history

**Independent Test**: View browser, verify quizzes from multiple creators visible with counts

### Tests for User Story 4

- [x] T038 [P] [US4] Contract test for GET /quizzes/browse in backend/tests/contract/test_attempt_api.py
- [x] T039 [US4] Integration test for quiz browser in backend/tests/integration/test_quiz_taking.py

### Implementation for User Story 4

- [x] T040 [US4] Implement AttemptService.browse_quizzes() in backend/src/services/attempt.py
- [x] T041 [US4] Implement GET /quizzes/browse endpoint in backend/src/api/quiz.py
- [x] T042 [US4] Create quiz_browser.html template with quiz list in frontend/templates/quiz_browser.html
- [x] T043 [US4] Implement GET /browse HTML page endpoint in backend/src/api/attempt.py

**Checkpoint**: User Stories 1-4 complete - full browse → take → submit → results flow

---

## Phase 7: User Story 5 - Retake a Quiz (Priority: P3)

**Goal**: User can retake quizzes, all attempts recorded, only best score counts for scoreboard

**Independent Test**: Complete quiz twice, verify both recorded but only best counts in scoreboard

### Tests for User Story 5

- [x] T044 [P] [US5] Contract test for GET /quizzes/{quiz_id}/history in backend/tests/contract/test_attempt_api.py
- [x] T045 [P] [US5] Contract test for GET /my-attempts in backend/tests/contract/test_attempt_api.py
- [x] T046 [US5] Integration test for retake and best-score logic in backend/tests/integration/test_quiz_taking.py

### Implementation for User Story 5

- [x] T047 [US5] Implement AttemptService.get_quiz_history() in backend/src/services/attempt.py
- [x] T048 [US5] Implement AttemptService.get_my_attempts() in backend/src/services/attempt.py
- [x] T049 [US5] Implement GET /quizzes/{quiz_id}/history endpoint in backend/src/api/quiz.py
- [x] T050 [US5] Implement GET /my-attempts endpoint in backend/src/api/attempt.py
- [x] T051 [US5] Create attempt_history.html template showing all attempts with best flagged in frontend/templates/attempt_history.html
- [x] T052 [US5] Add "Retake" button to quiz browser for previously completed quizzes in frontend/templates/quiz_browser.html

**Checkpoint**: All 5 user stories complete - full quiz-taking feature implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T053 [P] Add error handling for quiz not found, attempt not found in backend/src/api/attempt.py
- [x] T054 [P] Add authorization checks (user can only access own attempts) in backend/src/api/attempt.py
- [x] T055 [P] Add input validation for all endpoints in backend/src/api/attempt.py
- [x] T056 [P] Add logging for quiz start, submit, and error events in backend/src/services/attempt.py
- [x] T057 Run quickstart.md verification steps
- [x] T058 Code cleanup and final review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel (US2 is frontend-only)
  - US3 depends on US1 (needs submit to work)
  - US4 can proceed in parallel with US1-US3
  - US5 depends on US1 (needs multiple attempts to test)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - core MVP
- **US2 (P1)**: Foundation only - enhances US1 but independently testable
- **US3 (P2)**: Requires US1 submit to work, but can develop in parallel
- **US4 (P2)**: Foundation only - can develop in parallel with US1-US3
- **US5 (P3)**: Requires US1 for multiple attempts - develop after US1 stable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/schemas before services
- Services before endpoints
- Backend before frontend templates
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational)**:
```bash
# Models can be created in parallel:
T005 (QuizAttempt model) || T006 (AttemptAnswer model)

# All schema tasks can run in parallel:
T007 || T008 || T009 || T010 || T011
```

**Phase 3 (US1 Tests)**:
```bash
# All US1 tests can be written in parallel:
T014 || T015 || T016 || T017
```

**Phase 4-6 (Different Stories)**:
```bash
# If multiple developers, these stories can run in parallel:
US2 (frontend) || US3 (results) || US4 (browse)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migrations)
2. Complete Phase 2: Foundational (models, schemas, router)
3. Complete Phase 3: User Story 1 (start, submit, score)
4. **STOP and VALIDATE**: User can complete a quiz and get scored
5. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test → Deploy (MVP - users can complete quizzes!)
3. Add US2 → Test → Deploy (better UX - answer changes)
4. Add US3 → Test → Deploy (feedback - see results)
5. Add US4 → Test → Deploy (discovery - browse quizzes)
6. Add US5 → Test → Deploy (improvement - retake for better score)

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 4 | 2 |
| Foundational | 9 | 6 |
| US1 (P1) | 12 | 5 |
| US2 (P1) | 5 | 0 |
| US3 (P2) | 7 | 1 |
| US4 (P2) | 6 | 1 |
| US5 (P3) | 9 | 2 |
| Polish | 6 | 4 |
| **Total** | **58** | **21** |

**MVP Scope**: Phases 1-3 (25 tasks) delivers User Story 1 - users can complete quizzes
