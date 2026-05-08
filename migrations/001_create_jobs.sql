-- Drop the old table so we can start fresh
DROP TABLE IF EXISTS jobs;

-- Create the V2 table
CREATE TABLE jobs (
    id            SERIAL PRIMARY KEY,
    type          VARCHAR(100) NOT NULL DEFAULT 'default',
    payload       JSONB NOT NULL DEFAULT '{}',
    status        VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority      INTEGER NOT NULL DEFAULT 0,
    attempts      INTEGER NOT NULL DEFAULT 0,
    max_retries   INTEGER NOT NULL DEFAULT 3,
    scheduled_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at    TIMESTAMPTZ,
    finished_at   TIMESTAMPTZ,
    error_message TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- THE MOST IMPORTANT PART OF THE PROJECT:
-- This index ensures the workers can find PENDING jobs instantly 
-- without scanning the entire table. It sorts by priority first, then scheduled time.
CREATE INDEX idx_jobs_polling ON jobs (status, priority DESC, scheduled_at ASC)
WHERE status = 'PENDING';