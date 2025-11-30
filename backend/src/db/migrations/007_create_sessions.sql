-- Migration: Create sessions table for user session management
-- Feature: 002-user-management

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT
);

-- Index for session lookup by token (auth middleware)
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);

-- Index for user's sessions (logout all, session management)
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- Index for cleanup queries (expired session removal)
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
