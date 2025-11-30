-- Migration: 002_create_questions
-- Description: Create questions table

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    text TEXT NOT NULL CHECK (length(text) >= 1 AND length(text) <= 1000),
    display_order INTEGER NOT NULL CHECK (display_order >= 1),
    points INTEGER NOT NULL DEFAULT 1 CHECK (points >= 1 AND points <= 100)
);

CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id, display_order);
