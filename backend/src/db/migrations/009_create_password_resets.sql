-- Migration: Create password_resets table for password reset tokens
-- Feature: 002-user-management

CREATE TABLE IF NOT EXISTS password_resets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER NOT NULL DEFAULT 0,
    used_at TEXT
);

-- Index for token hash lookups (reset validation)
CREATE INDEX IF NOT EXISTS idx_password_resets_token ON password_resets(token_hash);

-- Index for user's reset tokens (invalidate old tokens)
CREATE INDEX IF NOT EXISTS idx_password_resets_user ON password_resets(user_id);

-- Index for cleanup queries (expired token removal)
CREATE INDEX IF NOT EXISTS idx_password_resets_expires ON password_resets(expires_at);
