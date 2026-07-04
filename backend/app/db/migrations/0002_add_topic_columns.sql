-- Migration 0002: Add topic columns to gamification tables
-- Run this once in the Neon SQL Editor after PR is merged.
-- Adds topic tracking for per-topic mastery analytics.

-- Add topic column to quiz_attempts (if not already present)
ALTER TABLE IF EXISTS quiz_attempts
ADD COLUMN IF NOT EXISTS topic VARCHAR(80) NOT NULL DEFAULT 'Umum';

-- Add topic column to persistent_quizzes (if not already present)
ALTER TABLE IF EXISTS persistent_quizzes
ADD COLUMN IF NOT EXISTS topic VARCHAR(80) NOT NULL DEFAULT 'Umum';

-- Create index on quiz_attempts(user_id, topic) for mastery queries
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user_topic
ON quiz_attempts(user_id, topic);
