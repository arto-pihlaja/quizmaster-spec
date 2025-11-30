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

- [x] T001 Create database migration for user_scores table in backend/src/db/migrations/
- [x] T002 [P] Create index idx_user_scores_ranking on (total_score DESC, user_id) in backend/src/db/migrations/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, schemas, and infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create UserScore SQLAlchemy model in backend/src/models/user_score.py
- [x] T004 [P] Update models __init__.py to export UserScore in backend/src/models/__init__.py
- [x] T005 [P] Create ScoreboardEntry Pydantic response schema in backend/src/schemas/scoreboard.py
- [x] T006 [P] Create Pagination Pydantic schema in backend/src/schemas/scoreboard.py
- [x] T007 [P] Create ScoreboardResponse Pydantic schema in backend/src/schemas/scoreboard.py
- [x] T008 [P] Create MyRankResponse Pydantic schema in backend/src/schemas/scoreboard.py
- [x] T009 [P] Create ScoreboardStats Pydantic schema in backend/src/schemas/scoreboard.py
- [x] T010 Create ScoreboardService skeleton with dependency injection in backend/src/services/scoreboard.py
- [x] T011 Register scoreboard API router in backend/src/main.py
- [x] T012 [P] Add scoreboard link to base navigation template in frontend/templates/base.html

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View the Scoreboard (Priority: P1)

**Goal**: Any user can view the scoreboard and see a ranked list of all users with their total scores

**Independent Test**: Navigate to scoreboard page, verify users are displayed in ranked order by score

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Contract test for GET /api/scoreboard in backend/tests/contract/test_scoreboard_api.py
- [x] T014 [P] [US1] Contract test for GET /scoreboard HTML page in backend/tests/contract/test_scoreboard_api.py
- [x] T015 [P] [US1] Unit test for ScoreboardService.get_scoreboard() in backend/tests/unit/test_scoreboard_service.py
- [x] T016 [US1] Integration test for scoreboard display flow in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 1

- [x] T017 [US1] Implement ScoreboardService.get_scoreboard() with RANK() window function in backend/src/services/scoreboard.py
- [x] T018 [US1] Implement ScoreboardService.get_total_count() in backend/src/services/scoreboard.py
- [x] T019 [US1] Implement GET /api/scoreboard endpoint in backend/src/api/scoreboard.py
- [x] T020 [US1] Implement GET /scoreboard HTML page endpoint in backend/src/api/scoreboard.py
- [x] T021 [US1] Create scoreboard.html template with table layout in frontend/templates/scoreboard.html
- [x] T022 [US1] Add basic scoreboard table styles to frontend/static/css/styles.css

**Checkpoint**: User Story 1 complete - users can view ranked scoreboard

---

## Phase 4: User Story 2 - See Score Details (Priority: P2)

**Goal**: Each scoreboard entry shows rank position, display name, and total score with proper formatting

**Independent Test**: Verify each entry displays rank, display name, total score, and quizzes completed

### Tests for User Story 2

- [x] T023 [P] [US2] Contract test for ScoreboardEntry structure validation in backend/tests/contract/test_scoreboard_api.py
- [x] T024 [P] [US2] Contract test for GET /api/scoreboard/stats in backend/tests/contract/test_scoreboard_api.py
- [x] T025 [P] [US2] Unit test for competition ranking (tied scores) in backend/tests/unit/test_scoreboard_service.py
- [x] T026 [US2] Integration test for score details accuracy in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 2

- [x] T027 [US2] Implement ScoreboardService.get_stats() for aggregate statistics in backend/src/services/scoreboard.py
- [x] T028 [US2] Implement GET /api/scoreboard/stats endpoint in backend/src/api/scoreboard.py
- [x] T029 [US2] Update scoreboard.html to display quizzes_completed column in frontend/templates/scoreboard.html
- [x] T030 [US2] Add empty state message "No scores yet" to scoreboard.html in frontend/templates/scoreboard.html
- [x] T031 [US2] Add scoreboard stats summary section to scoreboard.html in frontend/templates/scoreboard.html

**Checkpoint**: User Stories 1 AND 2 complete - users see full score details

---

## Phase 5: User Story 3 - Find Myself on the Scoreboard (Priority: P2)

**Goal**: Logged-in user's entry is highlighted and they can jump to their position

**Independent Test**: Log in, view scoreboard, verify own entry is highlighted and "Jump to my rank" works

### Tests for User Story 3

- [x] T032 [P] [US3] Contract test for GET /api/scoreboard/my-rank in backend/tests/contract/test_scoreboard_api.py
- [x] T033 [P] [US3] Contract test for my-rank 401 when not authenticated in backend/tests/contract/test_scoreboard_api.py
- [x] T034 [P] [US3] Unit test for ScoreboardService.get_user_rank() in backend/tests/unit/test_scoreboard_service.py
- [x] T035 [US3] Integration test for user highlighting flow in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 3

- [x] T036 [US3] Implement ScoreboardService.get_user_rank() in backend/src/services/scoreboard.py
- [x] T037 [US3] Implement GET /api/scoreboard/my-rank endpoint in backend/src/api/scoreboard.py
- [x] T038 [US3] Add current_user_id to scoreboard response when authenticated in backend/src/api/scoreboard.py
- [x] T039 [US3] Add .highlight CSS class for current user row in frontend/static/css/styles.css
- [x] T040 [US3] Update scoreboard.html to highlight current user row in frontend/templates/scoreboard.html
- [x] T041 [US3] Add "Jump to My Rank" button to scoreboard.html in frontend/templates/scoreboard.html
- [x] T042 [US3] Create scoreboard.js with jump-to-rank functionality in frontend/static/js/scoreboard.js

**Checkpoint**: User Stories 1, 2, AND 3 complete - users can find themselves on scoreboard

---

## Phase 6: User Story 4 - Refresh Scoreboard Data (Priority: P3)

**Goal**: Users can manually refresh scoreboard data without full page reload

**Independent Test**: Complete a quiz, click refresh on scoreboard, verify new score appears without page reload

### Tests for User Story 4

- [x] T043 [P] [US4] Contract test for refresh response structure in backend/tests/contract/test_scoreboard_api.py
- [x] T044 [US4] Integration test for score update after quiz completion in backend/tests/integration/test_scoreboard.py

### Implementation for User Story 4

- [x] T045 [US4] Add Refresh button to scoreboard.html in frontend/templates/scoreboard.html
- [x] T046 [US4] Implement fetch-based refresh in scoreboard.js in frontend/static/js/scoreboard.js
- [x] T047 [US4] Add DOM update logic for table refresh in frontend/static/js/scoreboard.js
- [x] T048 [US4] Add loading indicator during refresh in frontend/static/js/scoreboard.js
- [x] T049 [US4] Add error handling and user-friendly error display in frontend/static/js/scoreboard.js

**Checkpoint**: All 4 user stories complete - full scoreboard functionality implemented

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, pagination, and refinements across all stories

- [x] T050 [P] Add pagination controls to scoreboard.html in frontend/templates/scoreboard.html
- [x] T051 [P] Implement pagination navigation in scoreboard.js in frontend/static/js/scoreboard.js
- [x] T052 [P] Add 400 Bad Request handling for invalid page parameters in backend/src/api/scoreboard.py
- [x] T053 [P] Add logging for scoreboard queries in backend/src/services/scoreboard.py
- [x] T054 Implement ScoreboardService.update_user_score() for quiz completion hook in backend/src/services/scoreboard.py
- [x] T055 Run quickstart.md verification steps
- [x] T056 Code cleanup and final review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (View) must complete before US2 (Details) - details enhance basic view
  - US1 (View) must complete before US3 (Find Myself) - highlighting requires scoreboard
  - US1 (View) must complete before US4 (Refresh) - refresh updates existing view
  - US2, US3, US4 can proceed in parallel after US1
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - core MVP
- **US2 (P2)**: Requires US1 for base scoreboard display
- **US3 (P2)**: Requires US1 for highlighting in context
- **US4 (P3)**: Requires US1 for refresh target

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/schemas before services
- Services before endpoints
- Backend before frontend templates
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# Migration can run alone, then index
T001 (migration) → T002 (index)
```

**Phase 2 (Foundational)**:
```bash
# Model first, then these can be parallel:
T003 (UserScore model) → T004 || T005 || T006 || T007 || T008 || T009 || T012
```

**Phase 3 (US1 Tests)**:
```bash
# All US1 tests can be written in parallel:
T013 || T014 || T015
```

**After US1 Completion**:
```bash
# US2, US3, and US4 can proceed in parallel:
Phase 4 (US2) || Phase 5 (US3) || Phase 6 (US4)
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /api/scoreboard" (T013)
Task: "Contract test for GET /scoreboard HTML" (T014)
Task: "Unit test for get_scoreboard()" (T015)

# After tests pass (red), implement services:
Task: "Implement get_scoreboard()" (T017) → T019 (endpoint)
Task: "Implement get_total_count()" (T018) - parallel with T017
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migrations, indexes)
2. Complete Phase 2: Foundational (models, schemas, router)
3. Complete Phase 3: User Story 1 (basic scoreboard view)
4. **STOP and VALIDATE**: Users can view ranked scoreboard
5. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test → Deploy (MVP - users can view scoreboard!)
3. Add US2 → Test → Deploy (details - richer information)
4. Add US3 → Test → Deploy (find myself - personalization)
5. Add US4 → Test → Deploy (refresh - better UX)
6. Each story adds value without breaking previous stories

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 2 | 1 |
| Foundational | 10 | 7 |
| US1 (P1) | 10 | 3 |
| US2 (P2) | 9 | 3 |
| US3 (P2) | 11 | 3 |
| US4 (P3) | 7 | 1 |
| Polish | 7 | 4 |
| **Total** | **56** | **22** |

**MVP Scope**: Phases 1-3 (22 tasks) delivers User Story 1 - users can view the ranked scoreboard
