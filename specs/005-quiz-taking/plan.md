# Implementation Plan: Quiz Taking

**Branch**: `005-quiz-taking` | **Date**: 2025-11-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-quiz-taking/spec.md`

## Summary

Implement quiz-taking functionality allowing authenticated users to browse available quizzes,
take quizzes by answering questions, submit their answers, and view results. Key features include:
answer selection without revealing correct answers, answer changes before submission, score
calculation on submit, best-score tracking for scoreboard integration, and attempt history.
Built with Python/FastAPI backend serving plain HTML/JavaScript frontend, persisting to SQLite.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), Uvicorn (ASGI server), Jinja2 (HTML templating), SQLAlchemy (ORM)
**Storage**: SQLite (local persistence, container-portable)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Local development initially, Azure container hosting later
**Project Type**: Web application (separate frontend/backend)
**Performance Goals**: Quiz start <1 second, submission <2 seconds, results page <2 seconds
**Constraints**: Lightweight dependencies, plain HTML/JS, no client-side answer storage (server holds truth)
**Scale/Scope**: Up to 10,000 users, unlimited quiz attempts per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development

| Requirement | Status | Notes |
|-------------|--------|-------|
| Tests written before implementation | WILL COMPLY | pytest tests for quiz-taking flows |
| Tests fail before implementation (Red) | WILL COMPLY | Contract tests defined first |
| Minimal implementation to pass (Green) | WILL COMPLY | Start with P1 (start/complete quiz) |
| Refactor maintains passing tests | WILL COMPLY | CI enforces test pass |

### II. Build in Small Increments

| Requirement | Status | Notes |
|-------------|--------|-------|
| Increments deliver demonstrable value | WILL COMPLY | Each user story is independent |
| Increments independently deployable | WILL COMPLY | P1 works alone; P2/P3 enhance |
| Stories scoped to single session | WILL COMPLY | 5 stories, all focused scope |
| Large features decomposed | WILL COMPLY | Split into browse/take/submit/results/retake |

### III. Simplicity (YAGNI)

| Requirement | Status | Notes |
|-------------|--------|-------|
| No "future" functionality | WILL COMPLY | No timers, no partial credit, no pause/resume |
| Abstractions when duplication demands | WILL COMPLY | Direct DB access first |
| Minimize dependencies | WILL COMPLY | Reuse existing stack from 001/002 |
| Sensible defaults | WILL COMPLY | All questions required, best score for scoreboard |

### Technology Stack Compliance

| Layer | Required | Planned | Compliant |
|-------|----------|---------|-----------|
| Language | Python 3.11+ | Python 3.11+ | YES |
| Web Framework | FastAPI | FastAPI | YES |
| Testing | pytest | pytest | YES |
| Database | SQLite | SQLite | YES |
| API Format | REST + JSON | REST + JSON | YES |

**Gate Status**: PASS - All constitution requirements will be met.

## Project Structure

### Documentation (this feature)

```text
specs/005-quiz-taking/
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
│   │   ├── quiz.py      # Quiz model (from 001)
│   │   ├── question.py  # Question model (from 001)
│   │   ├── answer.py    # Answer model (from 001)
│   │   ├── attempt.py   # NEW: Quiz attempt model
│   │   └── attempt_answer.py  # NEW: User's answer per question
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── quiz.py      # Quiz service (from 001)
│   │   ├── attempt.py   # NEW: Attempt/submission service
│   │   └── scoreboard.py # Scoreboard service (from 004)
│   ├── api/             # FastAPI routes
│   │   ├── __init__.py
│   │   ├── quiz.py      # Quiz endpoints (from 001)
│   │   └── attempt.py   # NEW: Quiz-taking endpoints
│   ├── db.py            # Database connection/session
│   └── main.py          # FastAPI app entry point
└── tests/
    ├── contract/        # API contract tests
    │   └── test_attempt_api.py  # NEW
    ├── integration/     # End-to-end tests
    │   └── test_quiz_taking.py  # NEW
    └── unit/            # Service unit tests
        └── test_attempt_service.py  # NEW

frontend/
├── static/
│   ├── css/
│   │   └── styles.css   # Basic styling
│   └── js/
│       ├── quiz.js      # Quiz form JS (from 001)
│       └── attempt.js   # NEW: Quiz-taking JS
├── templates/
│   ├── quiz_browser.html  # NEW: Browse all quizzes
│   ├── quiz_take.html     # NEW: Take quiz page
│   ├── quiz_results.html  # NEW: Results after submission
│   └── attempt_history.html # NEW: User's attempt history
└── tests/               # Frontend tests (optional)
```

**Structure Decision**: Web application structure extending existing backend/frontend layout.
New models for attempts and answers, new service for submission logic, new templates for
quiz-taking UI. Integrates with existing quiz and scoreboard features.

## Complexity Tracking

> No violations to justify. Design follows constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
