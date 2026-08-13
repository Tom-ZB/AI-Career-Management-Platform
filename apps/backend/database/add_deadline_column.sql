-- ============================================================
-- Migration: Add missing 'deadline' column to job_opportunities table
-- ============================================================

USE ai_career_platform;

-- Add deadline column if it doesn't exist
ALTER TABLE job_opportunities
ADD COLUMN IF NOT EXISTS deadline DATE NULL COMMENT 'Application deadline date' AFTER status;
