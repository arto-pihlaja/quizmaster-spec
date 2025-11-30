-- Attempt answers table - stores user's answer for each question in an attempt
CREATE TABLE IF NOT EXISTS attempt_answers (
    id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id TEXT REFERENCES questions(id) ON DELETE SET NULL,
    question_order INTEGER NOT NULL,
    question_text_snapshot TEXT NOT NULL,
    question_points INTEGER NOT NULL,
    selected_answer_id TEXT,
    selected_answer_text TEXT,
    correct_answer_text TEXT NOT NULL,
    is_correct INTEGER,
    points_earned INTEGER,
    CHECK (question_order >= 1),
    CHECK (question_points >= 1),
    CHECK (points_earned IS NULL OR points_earned >= 0)
);

CREATE INDEX IF NOT EXISTS idx_attempt_answers_attempt ON attempt_answers(attempt_id, question_order);
CREATE UNIQUE INDEX IF NOT EXISTS idx_attempt_answers_unique ON attempt_answers(attempt_id, question_id);
