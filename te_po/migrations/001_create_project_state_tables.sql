-- Migration: Create project_state_public and project_state_private tables

CREATE TABLE project_state_public (
    id TEXT PRIMARY KEY,
    state_yaml TEXT NOT NULL,
    repo TEXT NOT NULL,
    branch TEXT NOT NULL,
    commit TEXT NOT NULL,
    version INT NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE TABLE project_state_private (
    id TEXT PRIMARY KEY,
    state_yaml TEXT NOT NULL,
    repo TEXT NOT NULL,
    branch TEXT NOT NULL,
    commit TEXT NOT NULL,
    version INT NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- RLS Policies for project_state_public
ALTER TABLE project_state_public ENABLE ROW LEVEL SECURITY;
CREATE POLICY select_public ON project_state_public
    FOR SELECT
    USING (true);
CREATE POLICY insert_public ON project_state_public
    FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- RLS Policies for project_state_private
ALTER TABLE project_state_private ENABLE ROW LEVEL SECURITY;
CREATE POLICY select_private ON project_state_private
    FOR SELECT
    USING (auth.role() = 'service_role');
CREATE POLICY insert_private ON project_state_private
    FOR INSERT
    WITH CHECK (auth.role() = 'service_role');