<!--
SYNC IMPACT REPORT
==================
Version change: N/A → 1.0.0 (initial ratification)

Modified principles: None (initial creation)

Added sections:
- Core Principles (3 principles: Test-First Development, Build in Small Increments, Simplicity)
- Technology Stack
- Release Process
- Governance

Removed sections: None

Templates requiring updates:
- .specify/templates/plan-template.md: ✅ No updates required (Constitution Check section already generic)
- .specify/templates/spec-template.md: ✅ No updates required (compatible with principles)
- .specify/templates/tasks-template.md: ✅ No updates required (supports incremental delivery)

Follow-up TODOs: None
-->

# QuizMaster Constitution

## Core Principles

### I. Test-First Development

All feature development MUST follow Test-Driven Development (TDD):

- Tests MUST be written before implementation code
- Tests MUST fail before implementation begins (Red phase)
- Implementation MUST be minimal to pass tests (Green phase)
- Refactoring MUST maintain passing tests (Refactor phase)

**Rationale**: Test-first ensures requirements are clear, code is testable by design, and
regressions are caught immediately. Skipping tests leads to technical debt and fragile systems.

### II. Build in Small Increments

Development MUST proceed in small, independently testable increments:

- Each increment MUST deliver demonstrable value
- Each increment MUST be independently deployable
- User stories MUST be scoped to complete within a single work session
- Large features MUST be decomposed into vertical slices

**Rationale**: Small increments reduce risk, enable frequent feedback, and ensure continuous
progress. Large batches hide problems and delay value delivery.

### III. Simplicity (YAGNI)

All solutions MUST be the simplest that could possibly work:

- Implementations MUST NOT include functionality "for the future"
- Abstractions MUST NOT be created until duplication demands them
- Dependencies MUST be minimized—prefer standard library over external packages
- Configuration MUST have sensible defaults—avoid premature configurability

**Rationale**: Complexity is the enemy of reliability. Every unused feature, premature
abstraction, or unnecessary dependency increases maintenance burden and bug surface.

## Technology Stack

QuizMaster uses the following technology stack:

| Layer | Technology | Version Constraint |
|-------|------------|-------------------|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | Latest stable |
| Testing | pytest | Latest stable |
| Database | To be determined | N/A |
| API Format | REST + JSON | OpenAPI 3.0+ |

**Stack Constraints**:

- All new dependencies MUST be justified in PR descriptions
- Security-sensitive dependencies MUST be pinned to specific versions
- Development dependencies MUST be separated from production dependencies

## Release Process

### Versioning

QuizMaster follows Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes to public APIs or data schemas
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, documentation updates, internal refactors

### Release Workflow

1. All changes MUST pass automated tests before merge
2. Release branches MUST be created from main
3. Release notes MUST document all user-facing changes
4. Deployments MUST be reversible (rollback capability required)

### Hotfix Process

1. Hotfixes MUST branch from the release tag
2. Hotfixes MUST be cherry-picked to main after release
3. Hotfix version MUST increment PATCH number only

## Governance

### Constitution Authority

This constitution supersedes all other project practices. When conflicts arise between this
document and other guidelines, this constitution takes precedence.

### Amendment Process

1. Proposed amendments MUST be documented in a PR
2. Amendments MUST include rationale and migration plan
3. Breaking governance changes require MAJOR version increment
4. All team members MUST be notified of amendments

### Compliance Verification

- All PRs MUST verify compliance with Core Principles
- Code reviewers MUST check for principle violations
- Complexity additions MUST be justified against Simplicity principle

**Version**: 1.0.0 | **Ratified**: 2025-11-29 | **Last Amended**: 2025-11-29
