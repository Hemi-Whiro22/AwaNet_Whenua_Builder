-- SQL Migration: Pipeline Jobs Tracking Table
-- Created: 15 Tīhema 2025
-- Purpose: Durable job tracking in PostgreSQL for RQ jobs

-- Enable UUID extensions (try pgcrypto first, fallback to uuid-ossp)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main pipeline_jobs table
CREATE TABLE IF NOT EXISTS pipeline_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rq_job_id TEXT UNIQUE,
    realm TEXT,
    queue TEXT NOT NULL DEFAULT 'default',
    status TEXT NOT NULL DEFAULT 'queued',
    payload JSONB,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_rq_job_id ON pipeline_jobs(rq_job_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_status ON pipeline_jobs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_realm_status ON pipeline_jobs(realm, status);
CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_created_at ON pipeline_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_queue_status ON pipeline_jobs(queue, status);

-- Optional: Dead letter table for permanent failures
CREATE TABLE IF NOT EXISTS pipeline_jobs_dead_letter (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_job_id UUID REFERENCES pipeline_jobs(id) ON DELETE CASCADE,
    rq_job_id TEXT,
    final_error TEXT,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_dead_letter_job_id 
    ON pipeline_jobs_dead_letter(pipeline_job_id);

-- Optional: Job metrics table for dashboards
CREATE TABLE IF NOT EXISTS pipeline_job_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_job_id UUID REFERENCES pipeline_jobs(id) ON DELETE CASCADE,
    queue TEXT NOT NULL,
    realm TEXT,
    duration_sec FLOAT,
    status TEXT,
    recorded_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_job_metrics_queue_status 
    ON pipeline_job_metrics(queue, status);
CREATE INDEX IF NOT EXISTS idx_pipeline_job_metrics_recorded_at 
    ON pipeline_job_metrics(recorded_at DESC);
