-- Quiz attempts table - stores each attempt by a user to complete a quiz
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    quiz_id TEXT REFERENCES quizzes(id) ON DELETE SET NULL,
    quiz_title_snapshot TEXT NOT NULL,
    total_points_possible INTEGER NOT NULL,
    total_score INTEGER,
    started_at TEXT NOT NULL,
    submitted_at TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress',
    CHECK (status IN ('in_progress', 'submitted')),
    CHECK (total_points_possible > 0),
    CHECK (total_score IS NULL OR total_score >= 0)
);

CREATE INDEX IF NOT EXISTS idx_attempts_user_quiz ON quiz_attempts(user_id, quiz_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user_recent ON quiz_attempts(user_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_attempts_quiz ON quiz_attempts(quiz_id);
