# Tasks: User Management

**Input**: Design documents from `/specs/002-user-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First Development required)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` (per plan.md structure)

---

## Phase 1: Setup

**Purpose**: Database schema, dependencies, and project structure initialization

- [ ] T001 Create backend/src/security/ directory structure
- [ ] T002 [P] Add passlib, bcrypt to backend/requirements.txt
- [ ] T003 [P] Create database migration for users table in backend/src/db/migrations/
- [ ] T004 [P] Create database migration for sessions table in backend/src/db/migrations/
- [ ] T005 [P] Create database migration for login_attempts table in backend/src/db/migrations/
- [ ] T006 [P] Create database migration for password_resets table in backend/src/db/migrations/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, schemas, security utilities, and infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create User SQLAlchemy model in backend/src/models/user.py
- [ ] T008 Create Session SQLAlchemy model in backend/src/models/session.py
- [ ] T009 Create LoginAttempt SQLAlchemy model in backend/src/models/login_attempt.py
- [ ] T010 Create PasswordReset SQLAlchemy model in backend/src/models/password_reset.py
- [ ] T011 [P] Create models __init__.py exporting all models in backend/src/models/__init__.py
- [ ] T012 [P] Create Pydantic request schemas (UserRegister, UserLogin, ForgotPassword, ResetPassword, ProfileUpdate) in backend/src/schemas/auth.py
- [ ] T013 [P] Create Pydantic response schemas (UserResponse, AuthResponse, MessageResponse) in backend/src/schemas/auth.py
- [ ] T014 Create password hashing utilities with bcrypt in backend/src/security/password.py
- [ ] T015 Create session token generation utilities in backend/src/security/tokens.py
- [ ] T016 Create AuthService skeleton with dependency injection in backend/src/services/auth.py
- [ ] T017 Create UserService skeleton with dependency injection in backend/src/services/user.py
- [ ] T018 Create FastAPI auth router in backend/src/api/auth.py
- [ ] T019 Register auth API router in backend/src/main.py
- [ ] T020 [P] Create session cookie middleware in backend/src/middleware/session.py
- [ ] T021 [P] Create auth.js for form handling in frontend/static/js/auth.js

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Register a New Account (Priority: P1)

**Goal**: Visitors can create an account with email, password, and display name

**Independent Test**: Register with valid email/password, verify account created and can log in

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T022 [P] [US1] Contract test for POST /auth/register in backend/tests/contract/test_auth_api.py
- [ ] T023 [P] [US1] Unit test for password hashing in backend/tests/unit/test_password.py
- [ ] T024 [P] [US1] Unit test for AuthService.register_user() in backend/tests/unit/test_auth_service.py
- [ ] T025 [US1] Integration test for registration flow in backend/tests/integration/test_auth_flow.py

### Implementation for User Story 1

- [ ] T026 [US1] Implement password validation (8+ chars, uppercase, lowercase, number) in backend/src/security/password.py
- [ ] T027 [US1] Implement email normalization (lowercase) in backend/src/services/auth.py
- [ ] T028 [US1] Implement AuthService.register_user() with validation in backend/src/services/auth.py
- [ ] T029 [US1] Implement first-user-is-admin logic in backend/src/services/auth.py
- [ ] T030 [US1] Implement POST /auth/register endpoint in backend/src/api/auth.py
- [ ] T031 [US1] Create register.html template with form in frontend/templates/register.html
- [ ] T032 [US1] Implement GET /register HTML page endpoint in backend/src/api/auth.py
- [ ] T033 [US1] Add client-side form validation in frontend/static/js/auth.js

**Checkpoint**: User Story 1 complete - visitors can register accounts

---

## Phase 4: User Story 2 - Log In to Existing Account (Priority: P1)

**Goal**: Registered users can log in with email/password and receive a session

**Independent Test**: Log in with valid credentials, verify session created and authenticated pages accessible

### Tests for User Story 2

- [ ] T034 [P] [US2] Contract test for POST /auth/login in backend/tests/contract/test_auth_api.py
- [ ] T035 [P] [US2] Unit test for session creation in backend/tests/unit/test_auth_service.py
- [ ] T036 [P] [US2] Unit test for password verification in backend/tests/unit/test_password.py
- [ ] T037 [US2] Integration test for login flow in backend/tests/integration/test_auth_flow.py

### Implementation for User Story 2

- [ ] T038 [US2] Implement AuthService.authenticate_user() with password verification in backend/src/services/auth.py
- [ ] T039 [US2] Implement AuthService.create_session() with token generation in backend/src/services/auth.py
- [ ] T040 [US2] Implement POST /auth/login endpoint with session cookie in backend/src/api/auth.py
- [ ] T041 [US2] Implement generic error messages (no account existence leak) in backend/src/api/auth.py
- [ ] T042 [US2] Create login.html template with form in frontend/templates/login.html
- [ ] T043 [US2] Implement GET /login HTML page endpoint in backend/src/api/auth.py
- [ ] T044 [US2] Add redirect to dashboard for already-logged-in users in backend/src/api/auth.py
- [ ] T045 [US2] Implement get_current_user dependency for protected routes in backend/src/api/dependencies.py

**Checkpoint**: User Stories 1 AND 2 complete - users can register and log in (MVP)

---

## Phase 5: User Story 3 - Log Out (Priority: P2)

**Goal**: Logged-in users can log out, terminating their session

**Independent Test**: Log in, click logout, verify session invalidated and protected pages inaccessible

### Tests for User Story 3

- [ ] T046 [P] [US3] Contract test for POST /auth/logout in backend/tests/contract/test_auth_api.py
- [ ] T047 [P] [US3] Unit test for AuthService.invalidate_session() in backend/tests/unit/test_auth_service.py
- [ ] T048 [US3] Integration test for logout flow in backend/tests/integration/test_auth_flow.py

### Implementation for User Story 3

- [ ] T049 [US3] Implement AuthService.invalidate_session() in backend/src/services/auth.py
- [ ] T050 [US3] Implement POST /auth/logout endpoint with cookie clearing in backend/src/api/auth.py
- [ ] T051 [US3] Add logout button to base template/navigation in frontend/templates/base.html

**Checkpoint**: User Stories 1, 2, AND 3 complete - full login/logout cycle

---

## Phase 6: User Story 4 - Reset Forgotten Password (Priority: P2)

**Goal**: Users who forgot their password can reset it via email link

**Independent Test**: Request reset, use link, set new password, log in with new password

### Tests for User Story 4

- [ ] T052 [P] [US4] Contract test for POST /auth/forgot-password in backend/tests/contract/test_auth_api.py
- [ ] T053 [P] [US4] Contract test for POST /auth/reset-password in backend/tests/contract/test_auth_api.py
- [ ] T054 [P] [US4] Unit test for reset token generation/validation in backend/tests/unit/test_auth_service.py
- [ ] T055 [US4] Integration test for password reset flow in backend/tests/integration/test_auth_flow.py

### Implementation for User Story 4

- [ ] T056 [US4] Create EmailService interface and ConsoleEmailService in backend/src/services/email.py
- [ ] T057 [US4] Implement AuthService.request_password_reset() with token generation in backend/src/services/auth.py
- [ ] T058 [US4] Implement token hashing (SHA-256) before storage in backend/src/security/tokens.py
- [ ] T059 [US4] Implement AuthService.reset_password() with token validation in backend/src/services/auth.py
- [ ] T060 [US4] Implement invalidation of old tokens on new request in backend/src/services/auth.py
- [ ] T061 [US4] Implement POST /auth/forgot-password endpoint (always 200 response) in backend/src/api/auth.py
- [ ] T062 [US4] Implement POST /auth/reset-password endpoint in backend/src/api/auth.py
- [ ] T063 [US4] Create forgot_password.html template in frontend/templates/forgot_password.html
- [ ] T064 [US4] Create reset_password.html template in frontend/templates/reset_password.html
- [ ] T065 [US4] Implement GET /forgot-password HTML page endpoint in backend/src/api/auth.py
- [ ] T066 [US4] Implement GET /reset-password HTML page endpoint with token validation in backend/src/api/auth.py

**Checkpoint**: User Stories 1-4 complete - full authentication with password recovery

---

## Phase 7: User Story 5 - View and Edit Profile (Priority: P3)

**Goal**: Logged-in users can view their profile and update their display name

**Independent Test**: View profile page, change display name, verify change persists

### Tests for User Story 5

- [ ] T067 [P] [US5] Contract test for GET /auth/me in backend/tests/contract/test_auth_api.py
- [ ] T068 [P] [US5] Contract test for PUT /profile in backend/tests/contract/test_auth_api.py
- [ ] T069 [P] [US5] Unit test for UserService.update_profile() in backend/tests/unit/test_user_service.py
- [ ] T070 [US5] Integration test for profile update flow in backend/tests/integration/test_auth_flow.py

### Implementation for User Story 5

- [ ] T071 [US5] Implement UserService.get_user() in backend/src/services/user.py
- [ ] T072 [US5] Implement UserService.update_profile() with display name validation in backend/src/services/user.py
- [ ] T073 [US5] Implement GET /auth/me endpoint in backend/src/api/auth.py
- [ ] T074 [US5] Implement PUT /profile endpoint in backend/src/api/auth.py
- [ ] T075 [US5] Create profile.html template with edit form in frontend/templates/profile.html
- [ ] T076 [US5] Implement GET /profile HTML page endpoint in backend/src/api/auth.py

**Checkpoint**: All 5 user stories complete - full user management implemented

---

## Phase 8: Security & Cross-Cutting Concerns

**Purpose**: Account lockout, session security, and cross-story improvements

### Account Lockout (Supports US2)

- [ ] T077 [P] Unit test for lockout logic in backend/tests/unit/test_auth_service.py
- [ ] T078 Implement AuthService.check_lockout() with exponential backoff in backend/src/services/auth.py
- [ ] T079 Implement AuthService.record_failed_attempt() in backend/src/services/auth.py
- [ ] T080 Implement AuthService.clear_lockout() on successful login in backend/src/services/auth.py
- [ ] T081 Return 429 with retry_after for locked accounts in backend/src/api/auth.py

### Session Security

- [ ] T082 [P] Implement session expiration check in backend/src/middleware/session.py
- [ ] T083 [P] Add user_agent and ip_address capture to session creation in backend/src/services/auth.py
- [ ] T084 [P] Create session cleanup scheduled task in backend/src/tasks/cleanup.py

---

## Phase 9: Polish & Validation

**Purpose**: Error handling, logging, and final validation

- [ ] T085 [P] Add 401 Unauthorized handling for unauthenticated access in backend/src/api/auth.py
- [ ] T086 [P] Add 409 Conflict handling for duplicate email registration in backend/src/api/auth.py
- [ ] T087 [P] Add logging for auth operations in backend/src/services/auth.py
- [ ] T088 [P] Add CSRF protection for forms in frontend/static/js/auth.js
- [ ] T089 Run quickstart.md verification steps
- [ ] T090 Code cleanup and final review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Register) and US2 (Login) are both P1 - can proceed in parallel
  - US3 (Logout) depends on US2 (needs login to test logout)
  - US4 (Reset Password) depends on US1 (needs registered account)
  - US5 (Profile) depends on US2 (needs login to access profile)
- **Security (Phase 8)**: Can proceed after US2 is complete
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - registration gateway
- **US2 (P1)**: Foundation only - can develop in parallel with US1
- **US3 (P2)**: Requires US2 (login) to test logout
- **US4 (P2)**: Requires US1 (registration) to have accounts to reset
- **US5 (P3)**: Requires US2 (login) to access profile

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
T002 (requirements) || T003 (users migration) || T004 (sessions migration) || T005 (attempts migration) || T006 (resets migration)
```

**Phase 2 (Foundational)**:
```bash
# Models in sequence (dependencies), but these can be parallel:
T011 (models init) || T012 (request schemas) || T013 (response schemas) || T20 (middleware) || T021 (auth.js)
```

**Phase 3 (US1 Tests)**:
```bash
# All US1 tests can be written in parallel:
T022 || T023 || T024
```

**Phase 4 (US2 Tests)**:
```bash
# All US2 tests can be written in parallel:
T034 || T035 || T036
```

**After US2 Completion**:
```bash
# US3 and US4 can proceed in parallel:
Phase 5 (US3) || Phase 6 (US4)
```

---

## Parallel Example: User Stories 1 & 2

```bash
# Both P1 stories can be developed in parallel after Foundational:

# Developer A - User Story 1 (Registration)
Task: "Contract test for POST /auth/register" (T022)
Task: "Unit test for password hashing" (T023)
Task: "Implement register endpoint" (T030)

# Developer B - User Story 2 (Login)
Task: "Contract test for POST /auth/login" (T034)
Task: "Unit test for session creation" (T035)
Task: "Implement login endpoint" (T040)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup (migrations, dependencies)
2. Complete Phase 2: Foundational (models, schemas, security utilities)
3. Complete Phase 3: User Story 1 (register)
4. Complete Phase 4: User Story 2 (login)
5. **STOP and VALIDATE**: Users can register and log in
6. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 -> Test -> Deploy (registration works!)
3. Add US2 -> Test -> Deploy (login works - MVP complete!)
4. Add US3 -> Test -> Deploy (logout - security improvement)
5. Add US4 -> Test -> Deploy (password reset - account recovery)
6. Add US5 -> Test -> Deploy (profile - user personalization)
7. Each story adds value without breaking previous stories

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 6 | 5 |
| Foundational | 15 | 5 |
| US1 (P1) | 12 | 3 |
| US2 (P1) | 12 | 3 |
| US3 (P2) | 6 | 2 |
| US4 (P2) | 15 | 3 |
| US5 (P3) | 10 | 3 |
| Security | 8 | 3 |
| Polish | 6 | 4 |
| **Total** | **90** | **31** |

**MVP Scope**: Phases 1-4 (45 tasks) delivers User Stories 1 & 2 - users can register and log in
