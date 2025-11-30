-- Migration: Create login_attempts table for account lockout tracking
-- Feature: 002-user-management

CREATE TABLE IF NOT EXISTS login_attempts (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT NOT NULL,
    locked_until TEXT
);

-- Index for email lookups (lockout checks)
CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON login_attempts(email);
