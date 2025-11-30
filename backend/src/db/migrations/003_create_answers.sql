-- Migration: 003_create_answers
-- Description: Create answers table

CREATE TABLE IF NOT EXISTS answers (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    text TEXT NOT NULL CHECK (length(text) >= 1 AND length(text) <= 500),
    is_correct INTEGER NOT NULL DEFAULT 0,
    display_order INTEGER NOT NULL CHECK (display_order >= 1)
);

CREATE INDEX IF NOT EXISTS idx_answers_question ON answers(question_id, display_order);
