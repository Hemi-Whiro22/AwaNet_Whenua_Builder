"""
Te Po Configuration - Simple settings without encryption.
UTF-8 enforced project-wide via mi_NZ.UTF-8 locale.
"""
from typing import Optional, Dict, Any, List
from functools import lru_cache
import os
from dotenv import load_dotenv
from pathlib import Path
import locale

from te_po.core.pydantic_shim import ensure_pydantic_internal_signature, ensure_pydantic_public_shims

ensure_pydantic_internal_signature()
ensure_pydantic_public_shims()
from pydantic_settings import BaseSettings
from pydantic import Field

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

_env_state: Dict[str, Any] = {}


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    # Supabase
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_anon_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_publishable_key: Optional[str] = None
    supabase_bucket_storage: str = Field(default="tepo_storage", alias="SUPABASE_BUCKET_STORAGE")
    supabase_table_files: str = Field(default="tepo_files", alias="SUPABASE_TABLE_FILES")
    supabase_bucket_mauri: str = Field(default="mauri_state", alias="SUPABASE_BUCKET_MAURI")
    supabase_table_mauri: str = Field(default="mauri_snapshots", alias="SUPABASE_TABLE_MAURI")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_vector_store_id: Optional[str] = Field(default=None, alias="OPENAI_VECTOR_STORE_ID")
    openai_assistant_id_qa: Optional[str] = Field(default=None, alias="OPENAI_ASSISTANT_ID_QA")
    kitenga_assistant_id: Optional[str] = Field(default=None, alias="KITENGA_ASSISTANT_ID")

    # Locale - UTF-8 enforced
    lang: str = Field(default="mi_NZ.UTF-8", alias="LANG")
    lc_all: str = Field(default="mi_NZ.UTF-8", alias="LC_ALL")

    # Flags + Tools
    offline_mode: bool = False
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    memory_table: Optional[str] = None
    pipeline_token: Optional[str] = Field(default=None, alias="PIPELINE_TOKEN")
    te_po_base_url: str = Field(default="http://localhost:8000", alias="TE_PO_BASE_URL")

    # Models
    backend_model: str = Field(default="gpt-4o", alias="OPENAI_BACKEND_MODEL")
    translation_model: str = Field(default="gpt-4o-mini", alias="OPENAI_TRANSLATION_MODEL")
    ui_model: str = Field(default="gpt-4o", alias="OPENAI_UI_MODEL")
    vision_model: str = Field(default="gpt-4o", alias="OPENAI_VISION_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBED_MODEL")

    # Ollama / local models
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3:latest", alias="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=60, alias="OLLAMA_TIMEOUT")

    # OCR
    tesseract_path: str = Field(default="/usr/bin/tesseract", alias="TESSERACT_PATH")

    # Supabase tables
    supabase_table_ocr_logs: str = "ocr_logs"
    supabase_table_translations: str = "translations"
    supabase_table_embeddings: str = "embeddings"
    supabase_table_memory: str = "ti_memory"

    # Project-specific tables
    table_project_state_public: str = "project_state_public"
    table_mauri_snapshots: str = "mauri_snapshots"
    table_other_example: str = "other_example_table"

    # Required keys (for validation)
    required_keys: List[str] = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]

    # Queue mode
    queue_mode: str = Field(default="inline", alias="QUEUE_MODE")

    # Sensitive keys to mask in logs
    sensitive_keys: List[str] = [
        "supabase_service_role_key",
        "openai_api_key",
        "pipeline_token",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True

    def summary(self) -> Dict[str, Any]:
        """Return a masked snapshot of environment status."""
        return {
            "context": _env_state.get("context", "local"),
            "loaded_keys": _env_state.get("loaded_keys", []),
            "masked_secrets": self.mask_sensitive_keys(),
            "locale": self.lang,
            "source": _env_state.get("source", "system"),
        }

    def validate_required_keys(self) -> List[str]:
        """Check for missing required keys."""
        missing = []
        for key in self.required_keys:
            env_val = os.getenv(key)
            if not env_val:
                missing.append(key)
        return missing

    def enforce_utf8_locale(self) -> str:
        """Set UTF-8 locale using LANG/LC_ALL."""
        for loc in [self.lang, "en_NZ.UTF-8", "en_US.UTF-8", "C.UTF-8"]:
            try:
                locale.setlocale(locale.LC_ALL, loc)
                return loc
            except locale.Error:
                continue
        return "C.UTF-8"

    def mask_sensitive_keys(self) -> Dict[str, Any]:
        """Return settings with sensitive keys masked."""
        masked = {}
        for key in self.model_fields.keys():
            value = getattr(self, key, None)
            if key in self.sensitive_keys and value:
                masked[key] = "***MASKED***"
            else:
                masked[key] = value
        return masked


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global shared instance
settings = get_settings()

# Print masked settings on load (for debugging)
print(f"Loaded settings: {settings.mask_sensitive_keys()}")

# Convenience exports
SUPABASE_URL = settings.supabase_url or ""
SUPABASE_KEY = settings.supabase_service_role_key or ""
