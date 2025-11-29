# Implementation Plan: Scoreboard

**Branch**: `004-scoreboard` | **Date**: 2025-11-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-scoreboard/spec.md`

## Summary

Implement a public scoreboard page that displays all users ranked by their total quiz scores.
The scoreboard supports pagination (50 per page), highlights the logged-in user's position,
provides a "jump to my rank" feature, and allows manual refresh without page reload.
Built with Python/FastAPI backend serving a plain HTML/JavaScript frontend, persisting to SQLite.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), Uvicorn (ASGI server), Jinja2 (HTML templating)
**Storage**: SQLite (local persistence, container-portable)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Local development initially, Azure container hosting later
**Project Type**: Web application (separate frontend/backend)
**Performance Goals**: Page load <2 seconds, support 10,000+ users
**Constraints**: Lightweight dependencies, plain HTML/JS (no heavy frameworks), separation of duties
**Scale/Scope**: 10,000+ users, single scoreboard page with pagination

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development

| Requirement | Status | Notes |
|-------------|--------|-------|
| Tests written before implementation | WILL COMPLY | pytest tests for each endpoint/service |
| Tests fail before implementation (Red) | WILL COMPLY | Contract tests defined first |
| Minimal implementation to pass (Green) | WILL COMPLY | Start with P1 story only |
| Refactor maintains passing tests | WILL COMPLY | CI enforces test pass |

### II. Build in Small Increments

| Requirement | Status | Notes |
|-------------|--------|-------|
| Increments deliver demonstrable value | WILL COMPLY | Each user story is independent |
| Increments independently deployable | WILL COMPLY | P1 works alone; P2/P3 add to it |
| Stories scoped to single session | WILL COMPLY | 4 stories, all small scope |
| Large features decomposed | WILL COMPLY | Already split into US1-4 |

### III. Simplicity (YAGNI)

| Requirement | Status | Notes |
|-------------|--------|-------|
| No "future" functionality | WILL COMPLY | Only spec'd features |
| Abstractions when duplication demands | WILL COMPLY | Direct queries first |
| Minimize dependencies | WILL COMPLY | FastAPI + SQLite + Jinja2 only |
| Sensible defaults | WILL COMPLY | 50 items/page default |

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
specs/004-scoreboard/
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
│   │   ├── user.py      # User model (from 002)
│   │   ├── quiz.py      # Quiz/Question models (from 001, 003)
│   │   └── score.py     # Score aggregation model
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   └── scoreboard.py # Scoreboard service
│   ├── api/             # FastAPI routes
│   │   ├── __init__.py
│   │   └── scoreboard.py # Scoreboard endpoints
│   ├── db.py            # Database connection/session
│   └── main.py          # FastAPI app entry point
└── tests/
    ├── contract/        # API contract tests
    ├── integration/     # End-to-end tests
    └── unit/            # Service unit tests

frontend/
├── static/
│   ├── css/
│   │   └── styles.css   # Basic styling
│   └── js/
│       └── scoreboard.js # Vanilla JS for refresh/navigation
├── templates/
│   └── scoreboard.html  # Jinja2 template
└── tests/               # Frontend tests (optional, minimal)
```

**Structure Decision**: Web application structure with separate backend (FastAPI/Python)
and frontend (static HTML/JS served by FastAPI). This supports the user requirement for
separation of duties while keeping deployment simple (single container).

## Complexity Tracking

> No violations to justify. Design follows constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
