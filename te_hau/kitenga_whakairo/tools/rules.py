RULES = [
    "Never delete or drop tables unless explicit confirmation.",
    "Always write migrations and show to user first.",
    "Prefer add/alter over destructive changes.",
    "Store new migrations in /supabase/migrations/ directory.",
    "Ensure UTF-8 mi-NZ encoding for all text.",
    "Use pgvector where embeddings are required.",
    "All tables include created_at, updated_at, and mauri metadata.",
]


def rules_writer(ctx):
    """Return carve safety rules for downstream automation."""
    return {"rules": RULES}
