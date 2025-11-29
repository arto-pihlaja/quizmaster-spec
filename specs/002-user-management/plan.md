# Implementation Plan: User Management

**Branch**: `002-user-management` | **Date**: 2025-11-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-user-management/spec.md`

## Summary

Implement user registration, authentication, and profile management for QuizMaster.
Users can register with email/password, log in, log out, reset forgotten passwords,
and manage their profile (display name). Security features include password hashing,
session management, account lockout, and secure password reset via email.
Built with Python/FastAPI backend serving plain HTML/JavaScript frontend, persisting to SQLite.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), Uvicorn (ASGI server), Jinja2 (HTML templating), passlib (password hashing), python-jose (JWT/tokens)
**Storage**: SQLite (local persistence, container-portable)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Local development initially, Azure container hosting later
**Project Type**: Web application (separate frontend/backend)
**Performance Goals**: Login <1 second, registration <2 seconds
**Constraints**: Lightweight dependencies, plain HTML/JS, secure password storage, email delivery for resets
**Scale/Scope**: Up to 10,000 users, session-based authentication

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development

| Requirement | Status | Notes |
|-------------|--------|-------|
| Tests written before implementation | WILL COMPLY | pytest tests for auth flows |
| Tests fail before implementation (Red) | WILL COMPLY | Contract tests defined first |
| Minimal implementation to pass (Green) | WILL COMPLY | Start with P1 (register/login) |
| Refactor maintains passing tests | WILL COMPLY | CI enforces test pass |

### II. Build in Small Increments

| Requirement | Status | Notes |
|-------------|--------|-------|
| Increments deliver demonstrable value | WILL COMPLY | Each user story is independent |
| Increments independently deployable | WILL COMPLY | P1 works alone; P2/P3 enhance |
| Stories scoped to single session | WILL COMPLY | 5 stories, all small scope |
| Large features decomposed | WILL COMPLY | Auth split into register/login/logout/reset/profile |

### III. Simplicity (YAGNI)

| Requirement | Status | Notes |
|-------------|--------|-------|
| No "future" functionality | WILL COMPLY | No OAuth, SSO, MFA initially |
| Abstractions when duplication demands | WILL COMPLY | Direct auth first |
| Minimize dependencies | WILL COMPLY | passlib + python-jose only for security |
| Sensible defaults | WILL COMPLY | 7-day sessions, 24h reset tokens |

### Technology Stack Compliance

| Layer | Required | Planned | Compliant |
|-------|----------|---------|-----------|
| Language | Python 3.11+ | Python 3.11+ | YES |
| Web Framework | FastAPI | FastAPI | YES |
| Testing | pytest | pytest | YES |
| Database | TBD | SQLite | YES (per user input) |
| API Format | REST + JSON | REST + JSON | YES |

**Gate Status**: PASS - All constitution requirements will be met.

## Project Structure

### Documentation (this feature)

```text
specs/002-user-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLAlchemy/Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py      # User model
│   │   └── session.py   # Session model
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py      # Authentication service
│   │   └── user.py      # User service
│   ├── api/             # FastAPI routes
│   │   ├── __init__.py
│   │   └── auth.py      # Auth endpoints
│   ├── security/        # Security utilities
│   │   ├── __init__.py
│   │   ├── password.py  # Password hashing
│   │   └── tokens.py    # Session/reset tokens
│   ├── db.py            # Database connection/session
│   └── main.py          # FastAPI app entry point
└── tests/
    ├── contract/        # API contract tests
    │   └── test_auth_api.py
    ├── integration/     # End-to-end tests
    │   └── test_auth_flow.py
    └── unit/            # Service unit tests
        ├── test_auth_service.py
        └── test_password.py

frontend/
├── static/
│   ├── css/
│   │   └── styles.css   # Basic styling
│   └── js/
│       └── auth.js      # Vanilla JS for forms
├── templates/
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── forgot_password.html  # Request reset
│   ├── reset_password.html   # Set new password
│   └── profile.html     # Profile page
└── tests/               # Frontend tests (optional, minimal)
```

**Structure Decision**: Web application structure with separate backend (FastAPI/Python)
and frontend (static HTML/JS served by FastAPI). Security modules isolated for clarity.

## Complexity Tracking

> No violations to justify. Design follows constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
