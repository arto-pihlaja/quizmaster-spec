# Data Model: User Management

**Feature**: 002-user-management
**Date**: 2025-11-29
**Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Entity Overview

```
┌──────────────────┐      ┌──────────────────┐
│      User        │      │     Session      │
├──────────────────┤      ├──────────────────┤
│ id (PK)          │◄────┐│ id (PK)          │
│ email (unique)   │     ││ user_id (FK)     │─┘
│ password_hash    │     │ token            │
│ display_name     │     │ created_at       │
│ is_admin         │     │ expires_at       │
│ created_at       │     │ user_agent       │
│ updated_at       │     │ ip_address       │
└──────────────────┘     └──────────────────┘
         │
         │
         ▼
┌──────────────────┐      ┌──────────────────┐
│  LoginAttempt    │      │  PasswordReset   │
├──────────────────┤      ├──────────────────┤
│ id (PK)          │      │ id (PK)          │
│ email            │      │ user_id (FK)     │─┐
│ attempt_count    │      │ token_hash       │ │
│ last_attempt_at  │      │ created_at       │ │
│ locked_until     │      │ expires_at       │ │
└──────────────────┘      │ used             │ │
                          │ used_at          │ │
                          └──────────────────┘ │
                                    ▲          │
                                    └──────────┘
```

## Entity Definitions

### User

Primary entity representing a registered user in the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash of password |
| display_name | VARCHAR(50) | NOT NULL | Display name for scoreboard |
| is_admin | BOOLEAN | NOT NULL, DEFAULT FALSE | Admin privileges flag |
| created_at | DATETIME | NOT NULL | Registration timestamp |
| updated_at | DATETIME | NOT NULL | Last profile update |

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

**Notes**:
- Email is case-insensitive (store lowercase)
- is_admin set to TRUE for first registered user (see 003-admin-roles)
- password_hash uses bcrypt with cost factor 12

### Session

Represents an active user session for authentication.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Session unique identifier |
| user_id | UUID | FK → User.id, NOT NULL | Owning user |
| token | VARCHAR(64) | UNIQUE, NOT NULL | Session token (stored in cookie) |
| created_at | DATETIME | NOT NULL | Session creation time |
| expires_at | DATETIME | NOT NULL | Session expiration time |
| user_agent | VARCHAR(500) | NULL | Browser user agent |
| ip_address | VARCHAR(45) | NULL | Client IP address |

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (token)
- INDEX (user_id)
- INDEX (expires_at) - for cleanup queries

**Notes**:
- Token is UUID v4, stored as-is (not hashed, unlike reset tokens)
- Default expiry: 7 days from creation
- Sliding expiration: extend on activity (optional)
- Delete row to invalidate session

### LoginAttempt

Tracks failed login attempts for account lockout.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email being attempted |
| attempt_count | INTEGER | NOT NULL, DEFAULT 0 | Consecutive failures |
| last_attempt_at | DATETIME | NOT NULL | Last failed attempt |
| locked_until | DATETIME | NULL | Lockout expiration |

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

**Notes**:
- Keyed by email, not user_id (tracks non-existent users too)
- Reset attempt_count on successful login
- Check locked_until before attempting password verification
- Cleanup old records periodically (> 24 hours old with zero attempts)

### PasswordReset

Stores password reset tokens for forgotten password flow.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| user_id | UUID | FK → User.id, NOT NULL | Target user |
| token_hash | VARCHAR(64) | UNIQUE, NOT NULL | SHA-256 hash of token |
| created_at | DATETIME | NOT NULL | Token creation time |
| expires_at | DATETIME | NOT NULL | Token expiration |
| used | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether token was used |
| used_at | DATETIME | NULL | When token was used |

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (token_hash)
- INDEX (user_id)
- INDEX (expires_at) - for cleanup queries

**Notes**:
- Token sent in email is NOT stored; only SHA-256 hash is stored
- Default expiry: 24 hours
- Mark as used (don't delete) for audit trail
- Invalidate old unused tokens when new one requested
- One active token per user at a time

## SQLite Schema

```sql
-- User table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_users_email ON users(email);

-- Session table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Login attempts table
CREATE TABLE login_attempts (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT NOT NULL,
    locked_until TEXT
);

CREATE INDEX idx_login_attempts_email ON login_attempts(email);

-- Password reset table
CREATE TABLE password_resets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER NOT NULL DEFAULT 0,
    used_at TEXT
);

CREATE INDEX idx_password_resets_user ON password_resets(user_id);
CREATE INDEX idx_password_resets_token ON password_resets(token_hash);
CREATE INDEX idx_password_resets_expires ON password_resets(expires_at);
```

## Pydantic Models

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

# Request models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)

# Response models
class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    is_admin: bool
    created_at: datetime

class SessionResponse(BaseModel):
    message: str
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
```

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| Session | User | Many-to-One | Multiple sessions per user |
| PasswordReset | User | Many-to-One | Multiple reset tokens per user (historical) |
| LoginAttempt | (email) | N/A | Not FK - tracks non-existent users |

## Cascade Behavior

- **User deleted** → All sessions deleted (CASCADE)
- **User deleted** → All password resets deleted (CASCADE)
- **User deleted** → Login attempts remain (keyed by email, not user_id)

## Data Lifecycle

### Session Cleanup
- Delete expired sessions: `WHERE expires_at < NOW()`
- Run via scheduled task or on each authentication check

### Password Reset Cleanup
- Delete expired unused tokens: `WHERE expires_at < NOW() AND used = 0`
- Keep used tokens for audit (optional: delete after 30 days)

### Login Attempt Cleanup
- Reset old attempts: `WHERE last_attempt_at < NOW() - 24h AND attempt_count > 0`
- Prevents permanent lockout from stale data
