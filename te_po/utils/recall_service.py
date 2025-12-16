from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from te_po.db.supabase import get_client, insert_with_realm
from te_po.schema.realms import RealmConfig
from te_po.utils.openai_client import client as openai_client

EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_VECTOR_FLAG = "ENABLE_OPENAI_VECTOR_RECALL"

logger = logging.getLogger("te_po.recall_service")


class RecallService:
    """
    Realm-aware recall that combines embeddings + Supabase pgvector search.
    Optionally supports OpenAI vector stores via feature flag.
    """

    def __init__(self, realm_config: RealmConfig):
        self.realm = realm_config

    def recall(
        self,
        query: str,
        thread_id: Optional[str] = None,
        top_k: Optional[int] = None,
        vector_store: Optional[str] = None,
    ) -> Dict[str, Any]:
        query_text = (query or "").strip()
        if not query_text:
            raise ValueError("Query text is required for recall.")

        matches: List[Dict[str, Any]] = []
        backend_used = "supabase"
        top_k_value = top_k or self._default_top_k()

        start_time = time.perf_counter()
        embedding = self._embed_query(query_text)

        preference = (vector_store or "").strip().lower() or self.realm.vector_store_strategy

        if preference == "openai" and self._openai_search_enabled():
            matches = self._search_openai(query_text, embedding, top_k_value)
            backend_used = "openai"

        if not matches and self._should_use_supabase(preference):
            matches = self._search_supabase(embedding, top_k_value)
            backend_used = "supabase"

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        results_count = len(matches)
        self._log_query(query_text, results_count)

        return {
            "realm_id": self.realm.realm_id,
            "thread_id": thread_id,
            "query": query_text,
            "matches": matches,
            "backend": backend_used,
            "query_tokens": self._estimate_tokens(query_text),
            "recall_latency_ms": latency_ms,
            "top_k": top_k_value,
        }

    def _embed_query(self, query: str) -> List[float]:
        if openai_client is None:
            raise RuntimeError("OpenAI client not configured for recall embeddings.")
        response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query)
        return response.data[0].embedding  # type: ignore[attr-defined]

    def _search_supabase(self, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        client = get_client()
        if client is None:
            logger.warning("Supabase client unavailable; recall search skipped.")
            return []
        try:
            response = (
                client.rpc(
                    "match_research_embeddings",
                    {
                        "query_embedding": embedding,
                        "match_count": top_k,
                        "filter_realm_id": self.realm.realm_id,
                    },
                ).execute()
            )
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Supabase recall search failed for realm %s: %s", self.realm.realm_id, exc)
            return []

        rows = getattr(response, "data", None) or []
        matches: List[Dict[str, Any]] = []
        for row in rows:
            metadata = row.get("metadata") or {}
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    metadata = {"raw": metadata}
            matches.append(
                {
                    "id": row.get("chunk_id") or row.get("id"),
                    "source": row.get("source_id") or row.get("source"),
                    "score": row.get("similarity") or row.get("score"),
                    "snippet": row.get("content") or row.get("text") or "",
                    "metadata": metadata,
                }
            )
        return matches

    def _search_openai(self, query: str, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """OpenAI vector store recall is not enabled by default; return empty matches."""
        logger.info(
            "OpenAI vector store recall disabled; falling back to Supabase for realm %s.",
            self.realm.realm_id,
        )
        return []

    def _log_query(self, query: str, results_count: int) -> None:
        payload = {"query": query, "results_count": results_count}
        insert_with_realm("recall_logs", payload, self.realm.realm_id)

    def _default_top_k(self) -> int:
        cfg = self.realm.recall_config
        if cfg and cfg.top_k:
            return max(1, cfg.top_k)
        return 5

    def _should_use_supabase(self, preferred_store: str) -> bool:
        cfg = self.realm.recall_config
        if cfg is None:
            return True
        if preferred_store == "openai" and not self._openai_search_enabled():
            return True
        return cfg.use_supabase_pgvector

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return max(1, len(text.split()))

    @staticmethod
    def _openai_search_enabled() -> bool:
        flag = os.getenv(OPENAI_VECTOR_FLAG, "").strip().lower()
        return flag in {"1", "true", "yes", "on"}
