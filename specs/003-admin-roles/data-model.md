# Data Model: Admin Roles

**Feature**: 003-admin-roles
**Date**: 2025-11-29
**Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Entity Overview

```
┌──────────────────┐
│      User        │
├──────────────────┤
│ id (PK)          │
│ email            │
│ password_hash    │
│ display_name     │
│ is_admin ◄───────│─── MODIFIED: Boolean flag for admin status
│ created_at       │
│ updated_at       │
└──────────────────┘
         │
         │ 1
         │
         ▼ *
┌──────────────────┐
│  AdminActionLog  │  ◄─── NEW: Audit trail for admin actions
├──────────────────┤
│ id (PK)          │
│ admin_id (FK)    │─┐
│ action           │ │
│ target_type      │ │
│ target_id        │ │
│ before_value     │ │
│ after_value      │ │
│ created_at       │ │
└──────────────────┘ │
         ▲           │
         └───────────┘

┌──────────────────┐
│    Question      │
├──────────────────┤
│ id (PK)          │
│ quiz_id (FK)     │
│ text             │
│ order_index      │
│ points ◄─────────│─── MODIFIED: Variable point value (1-100)
│ created_at       │
│ updated_at       │
└──────────────────┘
```

## Entity Definitions

### User (Modified)

Extends user entity from 002-user-management with admin flag.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash of password |
| display_name | VARCHAR(50) | NOT NULL | Display name for scoreboard |
| **is_admin** | BOOLEAN | NOT NULL, DEFAULT FALSE | **NEW**: Admin privileges flag |
| created_at | DATETIME | NOT NULL | Registration timestamp |
| updated_at | DATETIME | NOT NULL | Last profile update |

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

**Notes**:
- `is_admin` defaults to FALSE for all users
- First registered user gets `is_admin = TRUE` (application logic)
- Binary role: no intermediate privilege levels

### Question (Modified)

Extends question entity from 001-quiz-creation with point value.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| quiz_id | UUID | FK -> Quiz.id, NOT NULL | Parent quiz |
| text | TEXT | NOT NULL | Question text |
| order_index | INTEGER | NOT NULL | Display order in quiz |
| **points** | INTEGER | NOT NULL, DEFAULT 1, CHECK 1-100 | **NEW**: Point value for correct answer |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last modification |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (quiz_id)
- INDEX (quiz_id, order_index)

**Notes**:
- `points` defaults to 1 (FR-009)
- Valid range: 1-100 (FR-008)
- Quiz total = sum of points for correctly answered questions

### AdminActionLog (New)

Audit trail for all administrative actions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Log entry identifier |
| admin_id | UUID | FK -> User.id, NOT NULL | Admin who performed action |
| action | VARCHAR(50) | NOT NULL | Action type (see enum below) |
| target_type | VARCHAR(50) | NOT NULL | Target entity type |
| target_id | UUID | NOT NULL | ID of target entity |
| before_value | TEXT | NULL | JSON: state before action |
| after_value | TEXT | NULL | JSON: state after action |
| created_at | DATETIME | NOT NULL | When action occurred |

**Action Types (enum)**:
- `grant_admin` - Promoted user to admin
- `revoke_admin` - Removed admin status
- `edit_question` - Modified question text
- `edit_answer` - Modified answer text or correct flag
- `set_points` - Changed question point value

**Target Types**:
- `user` - For grant_admin, revoke_admin
- `question` - For edit_question, set_points
- `answer` - For edit_answer

**Indexes**:
- PRIMARY KEY (id)
- INDEX (admin_id)
- INDEX (target_type, target_id)
- INDEX (created_at)

**Notes**:
- No CASCADE delete - logs preserved even if admin/target deleted
- `before_value` and `after_value` store JSON for flexible schema
- Append-only table (no updates or deletes)

## SQLite Schema

```sql
-- Modify users table (add is_admin column)
ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0;

-- Modify questions table (add points column)
ALTER TABLE questions ADD COLUMN points INTEGER NOT NULL DEFAULT 1 CHECK (points >= 1 AND points <= 100);

-- Admin action log table
CREATE TABLE admin_action_logs (
    id TEXT PRIMARY KEY,
    admin_id TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    before_value TEXT,
    after_value TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_admin_logs_admin ON admin_action_logs(admin_id);
CREATE INDEX idx_admin_logs_target ON admin_action_logs(target_type, target_id);
CREATE INDEX idx_admin_logs_created ON admin_action_logs(created_at);

-- Note: No foreign key on admin_id to preserve logs if admin deleted
```

## Pydantic Models

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

# Enums
class AdminAction(str, Enum):
    GRANT_ADMIN = "grant_admin"
    REVOKE_ADMIN = "revoke_admin"
    EDIT_QUESTION = "edit_question"
    EDIT_ANSWER = "edit_answer"
    SET_POINTS = "set_points"

class TargetType(str, Enum):
    USER = "user"
    QUESTION = "question"
    ANSWER = "answer"

# Request models
class PromoteUserRequest(BaseModel):
    user_id: UUID

class RevokeAdminRequest(BaseModel):
    user_id: UUID

class EditQuestionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)

class EditAnswerRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    is_correct: bool

class SetPointsRequest(BaseModel):
    points: int = Field(ge=1, le=100)

# Response models
class UserAdminResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    is_admin: bool
    created_at: datetime

class AdminActionLogResponse(BaseModel):
    id: UUID
    admin_id: UUID
    admin_display_name: str
    action: AdminAction
    target_type: TargetType
    target_id: UUID
    before_value: dict | None
    after_value: dict | None
    created_at: datetime

class AdminStatsResponse(BaseModel):
    total_admins: int
    total_users: int
    recent_actions: list[AdminActionLogResponse]
```

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| AdminActionLog | User (admin) | Many-to-One | Many logs per admin |
| AdminActionLog | (target) | Logical | target_id references various entities |

## Cascade Behavior

- **User deleted** -> AdminActionLog preserved (admin_id becomes orphaned but logs remain for audit)
- **Question deleted** -> AdminActionLog preserved (historical record)
- **Answer deleted** -> AdminActionLog preserved (historical record)

## State Transitions

### User Admin Status

```
[New User Registers]
       │
       ▼
┌──────────────────┐
│ is_admin = FALSE │ (default for all)
└──────────────────┘
       │
       │ (if first user in system)
       ▼
┌──────────────────┐
│ is_admin = TRUE  │ (auto-promoted)
└──────────────────┘
       │
       │ (admin grants)     (admin revokes)
       ▼                    ▼
┌──────────────────┐ ◄──► ┌──────────────────┐
│ is_admin = TRUE  │      │ is_admin = FALSE │
└──────────────────┘      └──────────────────┘
       │
       │ (blocked if last admin)
       X Cannot revoke
```

### Question Points

```
[New Question Created]
       │
       ▼
┌──────────────────┐
│ points = 1       │ (default)
└──────────────────┘
       │
       │ (admin sets points)
       ▼
┌──────────────────┐
│ points = N       │ (where 1 ≤ N ≤ 100)
└──────────────────┘
```

## Query Patterns

### Check if User is Admin

```sql
SELECT is_admin FROM users WHERE id = :user_id;
```

### Count Total Admins (for last-admin check)

```sql
SELECT COUNT(*) FROM users WHERE is_admin = 1;
```

### List All Users (for admin management)

```sql
SELECT id, email, display_name, is_admin, created_at
FROM users
ORDER BY created_at DESC;
```

### Get Recent Admin Actions

```sql
SELECT l.*, u.display_name as admin_name
FROM admin_action_logs l
JOIN users u ON l.admin_id = u.id
ORDER BY l.created_at DESC
LIMIT 50;
```

### Calculate Quiz Score with Variable Points

```sql
SELECT SUM(q.points)
FROM questions q
JOIN answers a ON a.question_id = q.id
JOIN attempt_answers aa ON aa.answer_id = a.id
WHERE aa.attempt_id = :attempt_id
  AND a.is_correct = 1;
```

## Validation Rules

| Entity | Field | Rule | Error Message |
|--------|-------|------|---------------|
| Question | points | 1 ≤ value ≤ 100 | "Points must be between 1 and 100" |
| User | is_admin (revoke) | admin_count > 1 | "Cannot revoke last admin" |
| AdminActionLog | action | Valid enum value | "Invalid action type" |
| AdminActionLog | target_type | Valid enum value | "Invalid target type" |
