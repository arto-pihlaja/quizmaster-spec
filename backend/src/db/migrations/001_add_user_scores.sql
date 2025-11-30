-- Migration: Add user_scores table for scoreboard feature
-- Feature: 004-scoreboard
-- Date: 2025-11-30

-- UserScore table: Pre-aggregated score data for efficient scoreboard queries
CREATE TABLE IF NOT EXISTS user_scores (
    user_id TEXT PRIMARY KEY,
    total_score INTEGER NOT NULL DEFAULT 0,
    quizzes_completed INTEGER NOT NULL DEFAULT 0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    display_name TEXT NOT NULL DEFAULT 'Anonymous',

    -- Constraints
    CHECK (total_score >= 0),
    CHECK (quizzes_completed >= 0)
);

-- Index for efficient ranking queries (ORDER BY total_score DESC, display_name ASC)
CREATE INDEX IF NOT EXISTS idx_user_scores_ranking
ON user_scores (total_score DESC, display_name ASC);

-- Index for user lookup
CREATE INDEX IF NOT EXISTS idx_user_scores_user_id
ON user_scores (user_id);
