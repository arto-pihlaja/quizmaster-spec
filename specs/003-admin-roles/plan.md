# Implementation Plan: Admin Roles

**Branch**: `003-admin-roles` | **Date**: 2025-11-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-admin-roles/spec.md`

## Summary

Implement admin role management for QuizMaster. The first registered user automatically
becomes an admin. Admins can appoint/revoke other admins, edit any quiz questions and
answers, and assign variable point values per question. All admin actions are logged
for audit purposes. Built with Python/FastAPI backend serving plain HTML/JavaScript
frontend, persisting to SQLite.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), Uvicorn (ASGI server), Jinja2 (HTML templating)
**Storage**: SQLite (local persistence, container-portable)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Local development initially, Azure container hosting later
**Project Type**: Web application (separate frontend/backend)
**Performance Goals**: Admin actions complete <1 second
**Constraints**: Lightweight dependencies, plain HTML/JS, audit trail for all admin actions
**Scale/Scope**: Up to 10,000 users, multiple admins, binary role model (admin/user)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development

| Requirement | Status | Notes |
|-------------|--------|-------|
| Tests written before implementation | WILL COMPLY | pytest tests for admin flows |
| Tests fail before implementation (Red) | WILL COMPLY | Contract tests defined first |
| Minimal implementation to pass (Green) | WILL COMPLY | Start with P1 (auto-admin, promote) |
| Refactor maintains passing tests | WILL COMPLY | CI enforces test pass |

### II. Build in Small Increments

| Requirement | Status | Notes |
|-------------|--------|-------|
| Increments deliver demonstrable value | WILL COMPLY | Each user story is independent |
| Increments independently deployable | WILL COMPLY | P1 works alone; P2/P3 add capabilities |
| Stories scoped to single session | WILL COMPLY | 6 stories, all small scope |
| Large features decomposed | WILL COMPLY | Admin split into role mgmt + content edit + points |

### III. Simplicity (YAGNI)

| Requirement | Status | Notes |
|-------------|--------|-------|
| No "future" functionality | WILL COMPLY | Binary role only (no hierarchy) |
| Abstractions when duplication demands | WILL COMPLY | Direct admin checks first |
| Minimize dependencies | WILL COMPLY | No new dependencies needed |
| Sensible defaults | WILL COMPLY | Default 1 point per question |

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
specs/003-admin-roles/
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
│   │   ├── user.py      # User model (from 002) - add is_admin field
│   │   ├── quiz.py      # Quiz model (from 001)
│   │   ├── question.py  # Question model (from 001) - add points field
│   │   └── admin_log.py # NEW: Admin action audit log
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── admin.py     # NEW: Admin service (role mgmt, audit)
│   │   └── quiz.py      # Quiz service (extends for admin edits)
│   ├── api/             # FastAPI routes
│   │   ├── __init__.py
│   │   ├── admin.py     # NEW: Admin endpoints
│   │   └── quiz.py      # Quiz endpoints (extend for admin edits)
│   ├── middleware/      # Auth middleware
│   │   └── admin.py     # NEW: Admin-only middleware
│   ├── db.py            # Database connection/session
│   └── main.py          # FastAPI app entry point
└── tests/
    ├── contract/        # API contract tests
    │   └── test_admin_api.py
    ├── integration/     # End-to-end tests
    │   └── test_admin_flow.py
    └── unit/            # Service unit tests
        └── test_admin_service.py

frontend/
├── static/
│   ├── css/
│   │   └── styles.css   # Basic styling (admin indicators)
│   └── js/
│       └── admin.js     # NEW: Admin functionality JS
├── templates/
│   ├── admin/
│   │   ├── users.html   # User management page
│   │   └── audit.html   # Audit log page (optional)
│   └── quiz/
│       └── edit.html    # Quiz edit (extends for admin)
└── tests/               # Frontend tests (optional, minimal)
```

**Structure Decision**: Web application structure with separate backend (FastAPI/Python)
and frontend (static HTML/JS served by FastAPI). Admin-specific modules isolated for clarity.
Extends existing user and quiz models with admin fields.

## Complexity Tracking

> No violations to justify. Design follows constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
