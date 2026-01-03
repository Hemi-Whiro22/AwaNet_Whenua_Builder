"""
Scope definition for Whiro tooling.

Allowed:
- HTTP calls to Te Pō runtime endpoints (TE_PO_BASE_URL)
- Local file inspection under te_po/*

Forbidden:
- Direct imports from `te_po.core.main` or FastAPI app objects
- Writes outside Te Pō repo or env-configured storage buckets
- Any Te Hau / other realm interactions
"""

NO_TOUCH = {
    "te_ao",
    "te_hau",
}

ALLOWED_IMPORT_PREFIXES = {
    "te_po.kaitiaki.whiro",
    "te_po.kitenga",
    "te_po.utils",
}
