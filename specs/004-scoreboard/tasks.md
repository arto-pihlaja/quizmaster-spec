# Tasks: Scoreboard

**Input**: Design documents from `/specs/004-scoreboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First Development required)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` (per plan.md structure)

---

## Phase 1: Setup

**Purpose**: Database schema and project structure initialization

- [ ] T001 Create database migration for user_scores table in backend/src/db/migrations/
- [ ] T002 [P] Create backend/src/services/scoreboard.py file structure
- [ ] T003 [P] Create backend/src/api/scoreboard.py file structure
- [ ] T004 [P] Create frontend/static/js/scoreboard.js file structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, schemas, and infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create UserScore SQLAlchemy model in backend/src/models/score.py
- [ ] T006 [P] Create models __init__.py exporting UserScore in backend/src/models/__init__.py
- [ ] T007 [P] Create Pydantic schemas (ScoreboardEntry, ScoreboardResponse, Pagination) in backend/src/schemas/scoreboard.py
- [ ] T008 [P] Create MyRankResponse schema in backend/src/schemas/scoreboard.py
- [ ] T009 [P] Create ScoreboardStats schema in backend/src/schemas/scoreboard.py
- [ ] T010 Create ScoreboardService skeleton with dependency injection in backend/src/services/scoreboard.py
- [ ] T011 Create FastAPI scoreboard router in backend/src/api/scoreboard.py
- [ ] T012 Register scoreboard API router in backend/src/main.py
- [ ] T013 [P] Create optional auth dependency get_current_user_optional in backend/src/api/dependencies.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View the Scoreboard (Priority: P1)

**Goal**: Any user (logged in or not) can view the scoreboard with ranked users

**Independent Test**: Navigate to scoreboard page, verify users displayed in ranked order by total score

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Contract test for GET /scoreboard HTML page in backend/tests/contract/test_scoreboard_api.py
- [ ] T015 [P] [US1] Contract test for GET /api/scoreboard JSON in backend/tests/contract/test_scoreboard_api.py
- [ ] T016 [P] [US1] Unit test for ScoreboardService.get_scoreboard() in backend/tests/unit/test_scoreboard_service.py
- [ ] T017 [US1] Integration test for scoreboard page load in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 1

- [ ] T018 [US1] Implement competition ranking query with RANK() window function in backend/src/services/scoreboard.py
- [ ] T019 [US1] Implement ScoreboardService.get_scoreboard() with pagination in backend/src/services/scoreboard.py
- [ ] T020 [US1] Implement ScoreboardService.get_total_count() in backend/src/services/scoreboard.py
- [ ] T021 [US1] Implement GET /api/scoreboard JSON endpoint in backend/src/api/scoreboard.py
- [ ] T022 [US1] Create scoreboard.html Jinja2 template with ranked list in frontend/templates/scoreboard.html
- [ ] T023 [US1] Implement GET /scoreboard HTML page endpoint in backend/src/api/scoreboard.py
- [ ] T024 [US1] Add pagination controls to scoreboard.html template in frontend/templates/scoreboard.html
- [ ] T025 [US1] Handle empty scoreboard state with message in frontend/templates/scoreboard.html
- [ ] T026 [US1] Add scoreboard link to navigation in frontend/templates/base.html

**Checkpoint**: User Story 1 complete - anyone can view the public scoreboard

---

## Phase 4: User Story 2 - See Score Details (Priority: P2)

**Goal**: Each scoreboard entry shows rank, display name, total score, and quizzes completed

**Independent Test**: View scoreboard, verify each entry displays all required fields

### Tests for User Story 2

- [ ] T027 [P] [US2] Contract test for scoreboard entry fields in backend/tests/contract/test_scoreboard_api.py
- [ ] T028 [P] [US2] Unit test for score aggregation logic in backend/tests/unit/test_scoreboard_service.py
- [ ] T029 [US2] Integration test for score details display in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 2

- [ ] T030 [US2] Add quizzes_completed field to scoreboard query in backend/src/services/scoreboard.py
- [ ] T031 [US2] Update scoreboard.html to display rank, name, score, quiz count in frontend/templates/scoreboard.html
- [ ] T032 [US2] Add CSS styling for scoreboard table in frontend/static/css/styles.css
- [ ] T033 [US2] Handle users with zero completed quizzes (score=0) in backend/src/services/scoreboard.py

**Checkpoint**: User Stories 1 AND 2 complete - scoreboard shows full details

---

## Phase 5: User Story 3 - Find Myself on the Scoreboard (Priority: P2)

**Goal**: Logged-in users can see their entry highlighted and jump to their position

**Independent Test**: Log in, view scoreboard, verify own entry is highlighted; use "jump to my rank"

### Tests for User Story 3

- [ ] T034 [P] [US3] Contract test for GET /api/scoreboard/my-rank in backend/tests/contract/test_scoreboard_api.py
- [ ] T035 [P] [US3] Unit test for ScoreboardService.get_user_rank() in backend/tests/unit/test_scoreboard_service.py
- [ ] T036 [US3] Integration test for user highlighting in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 3

- [ ] T037 [US3] Implement ScoreboardService.get_user_rank() in backend/src/services/scoreboard.py
- [ ] T038 [US3] Implement GET /api/scoreboard/my-rank endpoint in backend/src/api/scoreboard.py
- [ ] T039 [US3] Pass current_user_id to scoreboard template when logged in in backend/src/api/scoreboard.py
- [ ] T040 [US3] Add CSS .highlight class for current user row in frontend/static/css/styles.css
- [ ] T041 [US3] Implement client-side row highlighting based on user ID in frontend/static/js/scoreboard.js
- [ ] T042 [US3] Add "Jump to my rank" button in frontend/templates/scoreboard.html
- [ ] T043 [US3] Implement jump-to-rank navigation logic in frontend/static/js/scoreboard.js
- [ ] T044 [US3] Hide "Jump to my rank" for unauthenticated users in frontend/templates/scoreboard.html

**Checkpoint**: User Stories 1, 2, AND 3 complete - users can find themselves on the scoreboard

---

## Phase 6: User Story 4 - Refresh Scoreboard Data (Priority: P3)

**Goal**: Users can refresh scoreboard data without full page reload

**Independent Test**: View scoreboard, click refresh, verify data updates without page reload

### Tests for User Story 4

- [ ] T045 [P] [US4] Contract test for refresh returns updated data in backend/tests/contract/test_scoreboard_api.py
- [ ] T046 [P] [US4] Unit test for stats endpoint in backend/tests/unit/test_scoreboard_service.py
- [ ] T047 [US4] Integration test for refresh functionality in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 4

- [ ] T048 [US4] Implement ScoreboardService.get_stats() in backend/src/services/scoreboard.py
- [ ] T049 [US4] Implement GET /api/scoreboard/stats endpoint in backend/src/api/scoreboard.py
- [ ] T050 [US4] Add refresh button to scoreboard.html in frontend/templates/scoreboard.html
- [ ] T051 [US4] Implement fetch() call to /api/scoreboard in frontend/static/js/scoreboard.js
- [ ] T052 [US4] Implement DOM update logic to replace table content in frontend/static/js/scoreboard.js
- [ ] T053 [US4] Add loading indicator during refresh in frontend/static/js/scoreboard.js
- [ ] T054 [US4] Add error handling for failed refresh in frontend/static/js/scoreboard.js
- [ ] T055 [US4] Display user-friendly error message on failure in frontend/templates/scoreboard.html

**Checkpoint**: All 4 user stories complete - full scoreboard functionality implemented

---

## Phase 7: Score Update Integration

**Purpose**: Connect scoreboard to quiz completion events (cross-feature integration)

- [ ] T056 Implement update_user_score() function in backend/src/services/scoreboard.py
- [ ] T057 Unit test for update_user_score() in backend/tests/unit/test_scoreboard_service.py
- [ ] T058 Create UserScore record on user registration (score=0) in backend/src/services/auth.py
- [ ] T059 Call update_user_score() on quiz completion in backend/src/services/quiz.py (integration point)

**Note**: T059 depends on quiz-taking feature (005). Can be stubbed initially.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, error handling, and refinements

- [ ] T060 [P] Add index on user_scores(total_score DESC, user_id) in backend/src/db/migrations/
- [ ] T061 [P] Add 400 Bad Request handling for invalid page parameters in backend/src/api/scoreboard.py
- [ ] T062 [P] Add logging for scoreboard queries in backend/src/services/scoreboard.py
- [ ] T063 [P] Add response caching headers (Cache-Control) in backend/src/api/scoreboard.py
- [ ] T064 Run quickstart.md verification steps
- [ ] T065 Code cleanup and final review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (View) is core - must complete first
  - US2 (Details) extends US1 display
  - US3 (Find Myself) extends US1 with user context
  - US4 (Refresh) extends US1 with client-side updates
- **Score Update (Phase 7)**: Depends on US1 completion
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - core scoreboard view
- **US2 (P2)**: Requires US1 (extends display with more fields)
- **US3 (P2)**: Requires US1 (adds highlighting to existing view)
- **US4 (P3)**: Requires US1 (adds refresh to existing view)

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
T002 (scoreboard service) || T003 (scoreboard api) || T004 (scoreboard.js)
```

**Phase 2 (Foundational)**:
```bash
# These can run in parallel:
T006 (models init) || T007 (schemas) || T008 (MyRank schema) || T009 (Stats schema) || T013 (optional auth)
```

**Phase 3 (US1 Tests)**:
```bash
# All US1 tests can be written in parallel:
T014 || T015 || T016
```

**After US1 Completion**:
```bash
# US2, US3, US4 can proceed in parallel (different concerns):
Phase 4 (US2 - details) || Phase 5 (US3 - highlighting) || Phase 6 (US4 - refresh)
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /scoreboard" (T014)
Task: "Contract test for GET /api/scoreboard" (T015)
Task: "Unit test for get_scoreboard()" (T016)

# After tests pass (red), launch services:
Task: "Implement ranking query" (T018)
Task: "Implement get_scoreboard()" (T019)
Task: "Implement get_total_count()" (T020)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migrations, file structure)
2. Complete Phase 2: Foundational (models, schemas, router)
3. Complete Phase 3: User Story 1 (view scoreboard with ranking)
4. **STOP and VALIDATE**: Public scoreboard displays ranked users
5. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 -> Test -> Deploy (MVP - scoreboard visible!)
3. Add US2 -> Test -> Deploy (richer details)
4. Add US3 -> Test -> Deploy (user highlighting - engagement)
5. Add US4 -> Test -> Deploy (refresh - better UX)
6. Each story adds value without breaking previous stories

---

## Cross-Feature Dependencies

This feature depends on:
- **002-user-management**: User entity with display_name
- **005-quiz-taking** (future): QuizAttempt entity for score aggregation

The `update_user_score()` function (T056-T059) integrates with quiz completion.
For isolated testing, mock quiz attempt data or create test fixtures.

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 4 | 3 |
| Foundational | 9 | 5 |
| US1 (P1) | 13 | 3 |
| US2 (P2) | 7 | 2 |
| US3 (P2) | 11 | 2 |
| US4 (P3) | 11 | 2 |
| Score Update | 4 | 0 |
| Polish | 6 | 4 |
| **Total** | **65** | **21** |

**MVP Scope**: Phases 1-3 (26 tasks) delivers User Story 1 - public scoreboard with ranked users
