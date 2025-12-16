-- Recall query logging per realm

CREATE TABLE IF NOT EXISTS recall_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    query TEXT NOT NULL,
    results_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_recall_logs_realm ON recall_logs(realm_id);
