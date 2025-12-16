-- Kitenga Realms Table
-- Stores realm configurations for cloud deployments

CREATE TABLE IF NOT EXISTS kitenga.kitenga_realms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_name TEXT NOT NULL,
    realm_slug TEXT UNIQUE NOT NULL,
    template TEXT DEFAULT 'basic',
    kaitiaki_name TEXT,
    kaitiaki_role TEXT,
    kaitiaki_instructions TEXT,
    description TEXT,
    selected_apis JSONB DEFAULT '["vector", "memory", "assistant"]',
    openai_assistant_id TEXT,
    openai_vector_store_id TEXT,
    urls JSONB,
    config JSONB,
    mauri_status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_kitenga_realms_slug ON kitenga.kitenga_realms(realm_slug);
CREATE INDEX IF NOT EXISTS idx_kitenga_realms_created ON kitenga.kitenga_realms(created_at DESC);

-- Add to public schema as well for easier access
CREATE TABLE IF NOT EXISTS kitenga_realms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_name TEXT NOT NULL,
    realm_slug TEXT UNIQUE NOT NULL,
    template TEXT DEFAULT 'basic',
    kaitiaki_name TEXT,
    kaitiaki_role TEXT,
    kaitiaki_instructions TEXT,
    description TEXT,
    selected_apis JSONB DEFAULT '["vector", "memory", "assistant"]',
    openai_assistant_id TEXT,
    openai_vector_store_id TEXT,
    urls JSONB,
    config JSONB,
    mauri_status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_realms_slug ON kitenga_realms(realm_slug);
CREATE INDEX IF NOT EXISTS idx_realms_created ON kitenga_realms(created_at DESC);

-- Enable RLS
ALTER TABLE kitenga_realms ENABLE ROW LEVEL SECURITY;

-- Policy for service role (full access)
CREATE POLICY "Service role has full access" ON kitenga_realms
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy for authenticated users (read only)
CREATE POLICY "Authenticated users can read realms" ON kitenga_realms
    FOR SELECT
    TO authenticated
    USING (true);
