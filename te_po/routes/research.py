import json
import os
import requests
from fastapi import APIRouter, Body, HTTPException
from te_po.pipeline.research.search_engine import research_query
from te_po.services.vector_service import search_text
from te_po.services.chat_memory import record_turn
from te_po.utils.supabase_client import get_client

router = APIRouter()


@router.post("/research/query")
def research(body: dict):
    return research_query(body["query"], body.get("limit", 10))


@router.post("/research/web_search")
def research_web_search(payload: dict = Body(...)):
    """
    Web search via Brave API with optional site filters. Falls back to stacked search if missing key, empty, or failure.
    """
    query = (payload.get("query") or "").strip()
    limit = payload.get("limit", 5)
    filters = payload.get("filters") or {}
    fallback = payload.get("fallback", True)
    session_id = payload.get("session_id") or None
    thread_id = payload.get("thread_id") or None
    data_mode = payload.get("mode") or "research"
    sites = filters.get("site") or []

    # Apply site boosting
    site_clause = ""
    if sites:
        boosted = [f"site:{s}" for s in sites if s]
        if boosted:
            site_clause = " " + " ".join(boosted)
    brave_query = (query + site_clause).strip()
    supabase = get_client()

    def _persist(results_payload, web_results: list[dict] | None):
        # Best-effort log into tepo_logs
        if supabase:
            try:
                supabase.table("tepo_logs").insert(
                    {
                        "event": "web_search",
                        "detail": query or "web search",
                        "source": "research_web_search",
                        "data": {
                            "query": query,
                            "filters": filters,
                            "engine": results_payload.get("engine"),
                            "results": web_results if web_results is not None else results_payload,
                        },
                    }
                ).execute()
            except Exception:
                pass

        # Embed into chat memory so /kitenga/gpt-whisper recall can pick it up
        if session_id:
            try:
                snippet = ""
                if web_results:
                    lines = []
                    for idx, item in enumerate(web_results[:limit]):
                        title = item.get("title") or ""
                        url = item.get("url") or ""
                        summary = item.get("summary") or ""
                        lines.append(f"{idx+1}. {title} — {url} — {summary}")
                    snippet = "\n".join(lines)
                else:
                    # Fallback: serialize payload (trimmed)
                    snippet = (json.dumps(results_payload, ensure_ascii=False)[:4000]) if results_payload else ""

                if query:
                    record_turn(
                        session_id=session_id,
                        thread_id=thread_id,
                        role="user",
                        text=f"[web_search query] {query}",
                        mode=data_mode,
                        source="web_search",
                    )
                if snippet:
                    record_turn(
                        session_id=session_id,
                        thread_id=thread_id,
                        role="assistant",
                        text=f"[web_search results] {snippet}",
                        mode=data_mode,
                        source="web_search",
                    )
            except Exception:
                pass

    token = os.getenv("BRAVE_API_WEB_SEARCH")
    result_payload = None
    web_results: list[dict] | None = None
    if not token:
        result_payload = research_stacked({"query": query, "limit": limit}) if fallback else {"engine": "brave", "query": brave_query, "results": []}
        _persist(result_payload, web_results)
        return result_payload
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": token},
            params={"q": brave_query, "count": limit},
            timeout=8,
        )
        if not resp.ok:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json() or {}
        web_results = []
        for item in data.get("web", {}).get("results", []):
            web_results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "summary": item.get("description"),
                }
            )
        if not web_results and fallback:
            result_payload = research_stacked({"query": query, "limit": limit})
        else:
            result_payload = {"engine": "brave", "query": brave_query, "results": web_results}
    except Exception:
        result_payload = research_stacked({"query": query, "limit": limit}) if fallback else {"engine": "brave", "query": brave_query, "results": []}

    _persist(result_payload, web_results)
    return result_payload

@router.post("/research/stacked")
def research_stacked(
    payload: dict = Body(...),
):
    """
    Layered research: local vector search -> recent docs -> web/LLM fallback.
    """
    query = payload.get("query") or ""
    top_k = payload.get("limit", 5)
    results = {"vector_hits": [], "recent_docs": [], "web": None}

    # 1) Vector search (own data first)
    try:
        vec = search_text(query=query, top_k=top_k)
        results["vector_hits"] = vec.get("results", [])
    except Exception:
        results["vector_hits"] = []

    # 2) Recent docs (Supabase profiles)
    client = get_client()
    if client:
        try:
            resp = (
                client.table("kitenga.artifacts")
                .select("file_name,summary_short,summary_long,storage_path,storage_url,source,created_at")
                .order("created_at", desc=True)
                .limit(top_k)
                .execute()
            )
            results["recent_docs"] = getattr(resp, "data", None) or []
        except Exception:
            results["recent_docs"] = []

    # 3) Web/LLM fallback if vector hits are weak
    if not results["vector_hits"]:
        try:
            web = research_query(query, min(top_k, 5))
            results["web"] = web
        except Exception:
            results["web"] = None

    return results

# To add: search_trademe_cards(), search_archive_pdfs(), search_local_metadata()
