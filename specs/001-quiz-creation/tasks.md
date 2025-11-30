# Tasks: Quiz Creation

**Input**: Design documents from `/specs/001-quiz-creation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First Development required)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` (per plan.md structure)

---

## Phase 1: Setup

**Purpose**: Database schema and project structure initialization

- [x] T001 Create backend project structure with src/, tests/ directories at backend/
- [x] T002 [P] Create requirements.txt with FastAPI, uvicorn, sqlalchemy, jinja2, pytest, pytest-asyncio, httpx in backend/
- [x] T003 [P] Create frontend directory structure with static/css/, static/js/, templates/ at frontend/
- [x] T004 Create database migration for quizzes table in backend/src/db/migrations/
- [x] T005 Create database migration for questions table in backend/src/db/migrations/
- [x] T006 Create database migration for answers table in backend/src/db/migrations/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, schemas, and infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create database connection and session management in backend/src/db.py
- [x] T008 Create Quiz SQLAlchemy model in backend/src/models/quiz.py
- [x] T009 Create Question SQLAlchemy model in backend/src/models/question.py
- [x] T010 Create Answer SQLAlchemy model in backend/src/models/answer.py
- [x] T011 [P] Create models __init__.py exporting all models in backend/src/models/__init__.py
- [x] T012 [P] Create Pydantic request schemas (QuizCreate, QuestionCreate, AnswerCreate) in backend/src/schemas/quiz.py
- [x] T013 [P] Create Pydantic response schemas (QuizResponse, QuestionResponse, AnswerResponse, QuizListItem, QuizListResponse) in backend/src/schemas/quiz.py
- [x] T014 Create QuizService skeleton with dependency injection in backend/src/services/quiz.py
- [x] T015 Create FastAPI app entry point in backend/src/main.py
- [x] T016 Register quiz API router in backend/src/main.py
- [x] T017 [P] Create base CSS styles in frontend/static/css/styles.css

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create a Basic Quiz (Priority: P1) 🎯 MVP

**Goal**: User can create a new quiz with title and questions, save it, and see it in their quiz list

**Independent Test**: Create quiz with 3 questions, save, verify it appears in quiz list with all questions intact

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T018 [P] [US1] Contract test for POST /quizzes (create quiz) in backend/tests/contract/test_quiz_api.py
- [x] T019 [P] [US1] Contract test for GET /quizzes (list my quizzes) in backend/tests/contract/test_quiz_api.py
- [x] T020 [P] [US1] Unit test for QuizService.create_quiz() in backend/tests/unit/test_quiz_service.py
- [x] T021 [P] [US1] Unit test for QuizService.list_quizzes() in backend/tests/unit/test_quiz_service.py
- [x] T022 [US1] Integration test for quiz creation flow in backend/tests/integration/test_quiz_crud.py

### Implementation for User Story 1

- [x] T023 [US1] Implement QuizService.create_quiz() with validation in backend/src/services/quiz.py
- [x] T024 [US1] Implement QuizService.list_quizzes() for owner in backend/src/services/quiz.py
- [x] T025 [US1] Implement POST /quizzes endpoint in backend/src/api/quiz.py
- [x] T026 [US1] Implement GET /quizzes endpoint in backend/src/api/quiz.py
- [x] T027 [US1] Create quiz_list.html template showing user's quizzes in frontend/templates/quiz_list.html
- [x] T028 [US1] Create quiz_create.html template with form in frontend/templates/quiz_create.html
- [x] T029 [US1] Create quiz.js for dynamic question/answer management in frontend/static/js/quiz.js
- [x] T030 [US1] Implement GET /my-quizzes HTML page endpoint in backend/src/api/quiz.py
- [x] T031 [US1] Implement GET /quizzes/new HTML page endpoint in backend/src/api/quiz.py
- [x] T032 [US1] Add validation error handling and display in frontend/static/js/quiz.js

**Checkpoint**: User Story 1 complete - users can create quizzes and see them in list

---

## Phase 4: User Story 2 - Edit an Existing Quiz (Priority: P2)

**Goal**: User can select a quiz, modify any content, and save changes

**Independent Test**: Create quiz, edit title and one question, save, verify changes persist

### Tests for User Story 2

- [x] T033 [P] [US2] Contract test for GET /quizzes/{id} (get quiz details) in backend/tests/contract/test_quiz_api.py
- [x] T034 [P] [US2] Contract test for PUT /quizzes/{id} (update quiz) in backend/tests/contract/test_quiz_api.py
- [x] T035 [P] [US2] Unit test for QuizService.get_quiz() in backend/tests/unit/test_quiz_service.py
- [x] T036 [P] [US2] Unit test for QuizService.update_quiz() in backend/tests/unit/test_quiz_service.py
- [x] T037 [US2] Integration test for quiz edit flow in backend/tests/integration/test_quiz_crud.py

### Implementation for User Story 2

- [x] T038 [US2] Implement QuizService.get_quiz() with owner check in backend/src/services/quiz.py
- [x] T039 [US2] Implement QuizService.update_quiz() with atomic replacement in backend/src/services/quiz.py
- [x] T040 [US2] Implement GET /quizzes/{id} endpoint in backend/src/api/quiz.py
- [x] T041 [US2] Implement PUT /quizzes/{id} endpoint in backend/src/api/quiz.py
- [x] T042 [US2] Create quiz_edit.html template with pre-filled form in frontend/templates/quiz_edit.html
- [x] T043 [US2] Implement GET /quizzes/{id}/edit HTML page endpoint in backend/src/api/quiz.py
- [x] T044 [US2] Add edit button to quiz_list.html template in frontend/templates/quiz_list.html

**Checkpoint**: User Stories 1 AND 2 complete - users can create and edit quizzes

---

## Phase 5: User Story 3 - Delete a Quiz (Priority: P3)

**Goal**: User can delete quizzes with confirmation, removing them permanently

**Independent Test**: Create quiz, delete it, verify it no longer appears in quiz list

### Tests for User Story 3

- [x] T045 [P] [US3] Contract test for DELETE /quizzes/{id} in backend/tests/contract/test_quiz_api.py
- [x] T046 [P] [US3] Unit test for QuizService.delete_quiz() in backend/tests/unit/test_quiz_service.py
- [x] T047 [US3] Integration test for quiz deletion flow in backend/tests/integration/test_quiz_crud.py

### Implementation for User Story 3

- [x] T048 [US3] Implement QuizService.delete_quiz() with owner check in backend/src/services/quiz.py
- [x] T049 [US3] Implement DELETE /quizzes/{id} endpoint in backend/src/api/quiz.py
- [x] T050 [US3] Add delete button with confirmation dialog to quiz_list.html in frontend/templates/quiz_list.html
- [x] T051 [US3] Implement delete confirmation JavaScript in frontend/static/js/quiz.js

**Checkpoint**: All 3 user stories complete - full quiz CRUD implemented

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, authorization, and refinements across all stories

- [x] T052 [P] Add 403 Forbidden handling for non-owner access in backend/src/api/quiz.py
- [x] T053 [P] Add 404 Not Found handling for missing quizzes in backend/src/api/quiz.py
- [x] T054 [P] Add logging for quiz CRUD operations in backend/src/services/quiz.py
- [x] T055 [P] Add input sanitization for quiz title and question text in backend/src/services/quiz.py
- [x] T056 Run quickstart.md verification steps
- [x] T057 Code cleanup and final review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Create) must complete before US2 (Edit) - edit requires existing quiz
  - US1 (Create) must complete before US3 (Delete) - delete requires existing quiz
  - US2 and US3 can proceed in parallel after US1
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - core MVP
- **US2 (P2)**: Requires US1 to be able to edit existing quizzes
- **US3 (P3)**: Requires US1 to be able to delete existing quizzes

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/schemas before services
- Services before endpoints
- Backend before frontend templates
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# These can run in parallel:
T002 (requirements.txt) || T003 (frontend structure)
```

**Phase 2 (Foundational)**:
```bash
# Models can be created in sequence (dependencies), but these can be parallel:
T011 (models init) || T012 (request schemas) || T013 (response schemas) || T017 (CSS)
```

**Phase 3 (US1 Tests)**:
```bash
# All US1 tests can be written in parallel:
T018 || T019 || T020 || T021
```

**After US1 Completion**:
```bash
# US2 and US3 can proceed in parallel by different developers:
Phase 4 (US2) || Phase 5 (US3)
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /quizzes" (T018)
Task: "Contract test for GET /quizzes" (T019)
Task: "Unit test for create_quiz()" (T020)
Task: "Unit test for list_quizzes()" (T021)

# After tests pass (red), launch services in parallel where possible:
Task: "Implement create_quiz()" (T023) - then T025 (endpoint)
Task: "Implement list_quizzes()" (T024) - then T026 (endpoint)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migrations, project structure)
2. Complete Phase 2: Foundational (models, schemas, router)
3. Complete Phase 3: User Story 1 (create quiz, list quizzes)
4. **STOP and VALIDATE**: User can create quizzes and see them in list
5. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test → Deploy (MVP - users can create quizzes!)
3. Add US2 → Test → Deploy (editing - improve existing quizzes)
4. Add US3 → Test → Deploy (deletion - housekeeping)
5. Each story adds value without breaking previous stories

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 6 | 2 |
| Foundational | 11 | 4 |
| US1 (P1) | 15 | 4 |
| US2 (P2) | 12 | 4 |
| US3 (P3) | 7 | 2 |
| Polish | 6 | 4 |
| **Total** | **57** | **20** |

**MVP Scope**: Phases 1-3 (32 tasks) delivers User Story 1 - users can create quizzes and view them
