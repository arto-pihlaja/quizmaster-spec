# Tasks: Admin Roles

**Input**: Design documents from `/specs/003-admin-roles/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First Development required)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` (per plan.md structure)

---

## Phase 1: Setup

**Purpose**: Database schema modifications and project structure initialization

- [ ] T001 Create database migration to add is_admin column to users table in backend/src/db/migrations/
- [ ] T002 [P] Create database migration to add points column to questions table in backend/src/db/migrations/
- [ ] T003 [P] Create database migration for admin_action_logs table in backend/src/db/migrations/
- [ ] T004 [P] Create backend/src/services/admin.py file structure
- [ ] T005 [P] Create backend/src/api/admin.py file structure
- [ ] T006 [P] Create frontend/static/js/admin.js file structure
- [ ] T007 [P] Create frontend/templates/admin/ directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, schemas, and infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Add is_admin field to User SQLAlchemy model in backend/src/models/user.py
- [ ] T009 Add points field (default=1) to Question SQLAlchemy model in backend/src/models/question.py
- [ ] T010 Create AdminActionLog SQLAlchemy model in backend/src/models/admin_log.py
- [ ] T011 [P] Update models __init__.py to export AdminActionLog in backend/src/models/__init__.py
- [ ] T012 [P] Create Pydantic schemas (UserAdminResponse, EditQuestionRequest, SetPointsRequest, EditAnswerRequest) in backend/src/schemas/admin.py
- [ ] T013 [P] Create AdminActionLogEntry and AdminLogResponse schemas in backend/src/schemas/admin.py
- [ ] T014 [P] Create AdminStatsResponse schema in backend/src/schemas/admin.py
- [ ] T015 Create AdminService skeleton with dependency injection in backend/src/services/admin.py
- [ ] T016 Create require_admin dependency in backend/src/api/dependencies.py
- [ ] T017 Create FastAPI admin router in backend/src/api/admin.py
- [ ] T018 Register admin API router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - First User Becomes Admin (Priority: P1)

**Goal**: First registered user automatically receives admin privileges

**Independent Test**: Register on fresh system, verify is_admin=True; register second user, verify is_admin=False

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US1] Contract test for first user gets admin in backend/tests/contract/test_admin_api.py
- [ ] T020 [P] [US1] Unit test for first-user-is-admin logic in backend/tests/unit/test_auth_service.py
- [ ] T021 [US1] Integration test for registration admin assignment in backend/tests/integration/test_admin_flow.py

### Implementation for User Story 1

- [ ] T022 [US1] Implement user count check in AuthService.register_user() in backend/src/services/auth.py
- [ ] T023 [US1] Set is_admin=True for first user in AuthService.register_user() in backend/src/services/auth.py
- [ ] T024 [US1] Add is_admin field to registration response in backend/src/api/auth.py
- [ ] T025 [US1] Display admin indicator in user profile/nav when is_admin=True in frontend/templates/base.html

**Checkpoint**: User Story 1 complete - first user is automatically admin

---

## Phase 4: User Story 2 - Appoint Another Admin (Priority: P1)

**Goal**: Admin can grant admin privileges to regular users

**Independent Test**: Login as admin, promote regular user, verify new admin can access admin endpoints

### Tests for User Story 2

- [ ] T026 [P] [US2] Contract test for GET /admin/users in backend/tests/contract/test_admin_api.py
- [ ] T027 [P] [US2] Contract test for POST /admin/users/{id}/promote in backend/tests/contract/test_admin_api.py
- [ ] T028 [P] [US2] Unit test for AdminService.promote_user() in backend/tests/unit/test_admin_service.py
- [ ] T029 [US2] Integration test for user promotion flow in backend/tests/integration/test_admin_flow.py

### Implementation for User Story 2

- [ ] T030 [US2] Implement AdminService.list_users() in backend/src/services/admin.py
- [ ] T031 [US2] Implement AdminService.promote_user() in backend/src/services/admin.py
- [ ] T032 [US2] Implement AdminService.log_action() for audit trail in backend/src/services/admin.py
- [ ] T033 [US2] Implement GET /admin/users endpoint in backend/src/api/admin.py
- [ ] T034 [US2] Implement POST /admin/users/{id}/promote endpoint in backend/src/api/admin.py
- [ ] T035 [US2] Create users.html admin template with user list in frontend/templates/admin/users.html
- [ ] T036 [US2] Implement GET /admin/users-page HTML endpoint in backend/src/api/admin.py
- [ ] T037 [US2] Add "Make Admin" button to user list in frontend/templates/admin/users.html
- [ ] T038 [US2] Implement promote action in frontend/static/js/admin.js

**Checkpoint**: User Stories 1 AND 2 complete - admins can promote users (MVP for admin management)

---

## Phase 5: User Story 3 - Edit Quiz Questions (Priority: P2)

**Goal**: Admin can edit any quiz question text regardless of owner

**Independent Test**: Create quiz as regular user, edit question as admin, verify change persists

### Tests for User Story 3

- [ ] T039 [P] [US3] Contract test for PUT /admin/questions/{id} in backend/tests/contract/test_admin_api.py
- [ ] T040 [P] [US3] Unit test for AdminService.edit_question() in backend/tests/unit/test_admin_service.py
- [ ] T041 [US3] Integration test for admin question editing in backend/tests/integration/test_admin_flow.py

### Implementation for User Story 3

- [ ] T042 [US3] Implement AdminService.edit_question() with audit logging in backend/src/services/admin.py
- [ ] T043 [US3] Implement PUT /admin/questions/{id} endpoint in backend/src/api/admin.py
- [ ] T044 [US3] Add admin edit button to question display in frontend/templates/quiz/edit.html
- [ ] T045 [US3] Implement question edit modal in frontend/static/js/admin.js

**Checkpoint**: User Stories 1-3 complete - admins can edit questions

---

## Phase 6: User Story 4 - Edit Answer Options and Correct Answer (Priority: P2)

**Goal**: Admin can edit any answer text and change which answer is correct

**Independent Test**: Edit answer text, change correct answer, verify quiz scoring uses updated answer

### Tests for User Story 4

- [ ] T046 [P] [US4] Contract test for PUT /admin/answers/{id} in backend/tests/contract/test_admin_api.py
- [ ] T047 [P] [US4] Unit test for AdminService.edit_answer() in backend/tests/unit/test_admin_service.py
- [ ] T048 [US4] Integration test for admin answer editing in backend/tests/integration/test_admin_flow.py

### Implementation for User Story 4

- [ ] T049 [US4] Implement AdminService.edit_answer() with audit logging in backend/src/services/admin.py
- [ ] T050 [US4] Implement PUT /admin/answers/{id} endpoint in backend/src/api/admin.py
- [ ] T051 [US4] Add admin edit controls for answers in frontend/templates/quiz/edit.html
- [ ] T052 [US4] Add correct answer toggle in frontend/static/js/admin.js

**Checkpoint**: User Stories 1-4 complete - admins can edit questions and answers

---

## Phase 7: User Story 5 - Assign Points Per Question (Priority: P2)

**Goal**: Admin can set variable point values (1-100) for each question

**Independent Test**: Set different points for questions, complete quiz, verify score reflects point values

### Tests for User Story 5

- [ ] T053 [P] [US5] Contract test for PUT /admin/questions/{id}/points in backend/tests/contract/test_admin_api.py
- [ ] T054 [P] [US5] Unit test for points validation (1-100) in backend/tests/unit/test_admin_service.py
- [ ] T055 [P] [US5] Unit test for score calculation with variable points in backend/tests/unit/test_quiz_service.py
- [ ] T056 [US5] Integration test for variable point scoring in backend/tests/integration/test_admin_flow.py

### Implementation for User Story 5

- [ ] T057 [US5] Implement AdminService.set_question_points() with validation in backend/src/services/admin.py
- [ ] T058 [US5] Implement PUT /admin/questions/{id}/points endpoint in backend/src/api/admin.py
- [ ] T059 [US5] Update score calculation to use question.points in backend/src/services/quiz.py
- [ ] T060 [US5] Add points input field to question editor in frontend/templates/quiz/edit.html
- [ ] T061 [US5] Display point values in quiz view in frontend/templates/quiz/view.html

**Checkpoint**: User Stories 1-5 complete - full content editing with variable scoring

---

## Phase 8: User Story 6 - Revoke Admin Privileges (Priority: P3)

**Goal**: Admin can revoke admin status from other admins (with last-admin protection)

**Independent Test**: Promote then demote user, verify they lose admin access; verify last admin cannot be demoted

### Tests for User Story 6

- [ ] T062 [P] [US6] Contract test for POST /admin/users/{id}/revoke in backend/tests/contract/test_admin_api.py
- [ ] T063 [P] [US6] Unit test for AdminService.revoke_admin() in backend/tests/unit/test_admin_service.py
- [ ] T064 [P] [US6] Unit test for last-admin protection in backend/tests/unit/test_admin_service.py
- [ ] T065 [US6] Integration test for admin revocation flow in backend/tests/integration/test_admin_flow.py

### Implementation for User Story 6

- [ ] T066 [US6] Implement admin count check in AdminService.revoke_admin() in backend/src/services/admin.py
- [ ] T067 [US6] Implement AdminService.revoke_admin() with audit logging in backend/src/services/admin.py
- [ ] T068 [US6] Implement POST /admin/users/{id}/revoke endpoint in backend/src/api/admin.py
- [ ] T069 [US6] Add "Remove Admin" button to user list for admins in frontend/templates/admin/users.html
- [ ] T070 [US6] Add confirmation dialog for revoke action in frontend/static/js/admin.js

**Checkpoint**: All 6 user stories complete - full admin management implemented

---

## Phase 9: Audit & Statistics

**Purpose**: Admin audit log viewing and statistics

- [ ] T071 [P] Contract test for GET /admin/logs in backend/tests/contract/test_admin_api.py
- [ ] T072 [P] Contract test for GET /admin/stats in backend/tests/contract/test_admin_api.py
- [ ] T073 Implement AdminService.get_logs() with filtering in backend/src/services/admin.py
- [ ] T074 Implement AdminService.get_stats() in backend/src/services/admin.py
- [ ] T075 Implement GET /admin/logs endpoint in backend/src/api/admin.py
- [ ] T076 Implement GET /admin/stats endpoint in backend/src/api/admin.py
- [ ] T077 Create audit.html template for log viewing in frontend/templates/admin/audit.html
- [ ] T078 Implement GET /admin/audit-page HTML endpoint in backend/src/api/admin.py

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, authorization checks, and refinements

- [ ] T079 [P] Add 403 Forbidden handling for non-admin access in backend/src/api/admin.py
- [ ] T080 [P] Add 404 Not Found handling for missing users/questions/answers in backend/src/api/admin.py
- [ ] T081 [P] Add 400 Bad Request handling for invalid points (out of range) in backend/src/api/admin.py
- [ ] T082 [P] Add logging for all admin operations in backend/src/services/admin.py
- [ ] T083 [P] Add admin badge/indicator to navigation in frontend/templates/base.html
- [ ] T084 [P] Add admin menu dropdown with links to admin pages in frontend/templates/base.html
- [ ] T085 Run quickstart.md verification steps
- [ ] T086 Code cleanup and final review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (First Admin) must complete first - provides initial admin
  - US2 (Promote) depends on US1 - needs admin to promote
  - US3-US5 (Content Editing) depend on US2 - need admin users
  - US6 (Revoke) depends on US2 - need multiple admins to test revocation
- **Audit (Phase 9)**: Depends on US2 completion (audit logs need actions to display)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - bootstraps admin system
- **US2 (P1)**: Requires US1 - needs first admin to promote others
- **US3 (P2)**: Requires US2 - needs admin to edit questions
- **US4 (P2)**: Requires US2 - needs admin to edit answers
- **US5 (P2)**: Requires US2 - needs admin to set points
- **US6 (P3)**: Requires US2 - needs multiple admins for revocation testing

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
T001 (is_admin migration) || T002 (points migration) || T003 (admin_log migration)
T004 (admin service) || T005 (admin api) || T006 (admin.js) || T007 (admin templates)
```

**Phase 2 (Foundational)**:
```bash
# After models created, these can be parallel:
T011 (models init) || T012 (schemas) || T013 (log schemas) || T014 (stats schema)
```

**Phase 3 (US1 Tests)**:
```bash
# All US1 tests can be written in parallel:
T019 || T020
```

**After US2 Completion**:
```bash
# US3, US4, US5 can proceed in parallel (different content types):
Phase 5 (US3 - questions) || Phase 6 (US4 - answers) || Phase 7 (US5 - points)
```

---

## Parallel Example: Content Editing Stories

```bash
# After US2 (Promote) completes, content editing stories can run in parallel:

# Developer A - User Story 3 (Edit Questions)
Task: "Contract test for PUT /admin/questions/{id}" (T039)
Task: "Implement edit_question()" (T042)

# Developer B - User Story 4 (Edit Answers)
Task: "Contract test for PUT /admin/answers/{id}" (T046)
Task: "Implement edit_answer()" (T049)

# Developer C - User Story 5 (Set Points)
Task: "Contract test for PUT /admin/questions/{id}/points" (T053)
Task: "Implement set_question_points()" (T057)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup (migrations, file structure)
2. Complete Phase 2: Foundational (models, schemas, dependencies)
3. Complete Phase 3: User Story 1 (first user admin)
4. Complete Phase 4: User Story 2 (promote users)
5. **STOP and VALIDATE**: Admin system bootstraps, admins can be promoted
6. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 -> Test -> Deploy (first admin bootstrapped!)
3. Add US2 -> Test -> Deploy (admin promotion - MVP complete!)
4. Add US3 -> Test -> Deploy (question editing)
5. Add US4 -> Test -> Deploy (answer editing)
6. Add US5 -> Test -> Deploy (variable points)
7. Add US6 -> Test -> Deploy (admin revocation)
8. Each story adds value without breaking previous stories

---

## Cross-Feature Dependencies

This feature depends on:
- **001-quiz-creation**: Quiz, Question, Answer entities
- **002-user-management**: User entity with authentication

This feature modifies:
- **User model**: Adds is_admin field
- **Question model**: Adds points field
- **Score calculation**: Must use question.points

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 7 | 6 |
| Foundational | 11 | 4 |
| US1 (P1) | 7 | 2 |
| US2 (P1) | 14 | 3 |
| US3 (P2) | 7 | 2 |
| US4 (P2) | 7 | 2 |
| US5 (P2) | 9 | 3 |
| US6 (P3) | 9 | 3 |
| Audit | 8 | 2 |
| Polish | 8 | 5 |
| **Total** | **87** | **32** |

**MVP Scope**: Phases 1-4 (39 tasks) delivers User Stories 1 & 2 - admin system bootstraps and admins can promote other users
