from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

_env_state: Dict[str, Any] = {}


class Settings(BaseSettings):
    """Application settings sourced from validated environment variables."""

    # Supabase keys
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: Optional[str] = Field(
        default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_anon_key: Optional[str] = None
    supabase_publishable_key: Optional[str] = None
    supabase_bucket_storage: str = Field(default="tepo_storage", alias="SUPABASE_BUCKET_STORAGE")
    supabase_table_files: str = Field(default="tepo_files", alias="SUPABASE_TABLE_FILES")
    supabase_bucket_mauri: str = Field(default="mauri_state", alias="SUPABASE_BUCKET_MAURI")
    supabase_table_mauri: str = Field(default="mauri_snapshots", alias="SUPABASE_TABLE_MAURI")
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_vector_store_id: Optional[str] = Field(default=None, alias="OPENAI_VECTOR_STORE_ID")
    openai_assistant_id_qa: Optional[str] = Field(default=None, alias="OPENAI_ASSISTANT_ID_QA")
    openai_assistant_id_ops: Optional[str] = Field(default=None, alias="OPENAI_ASSISTANT_ID_OPS")
    kitenga_assistant_id: Optional[str] = Field(default=None, alias="KITENGA_ASSISTANT_ID")

    # Locale
    lang: str = Field(default="en_NZ.UTF-8", alias="LANG")
    lc_all: str = Field(default="en_NZ.UTF-8", alias="LC_ALL")

    # Flags + Tools
    offline_mode: bool = False
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    memory_table: Optional[str] = None
    pipeline_token: Optional[str] = Field(default=None, alias="PIPELINE_TOKEN")
    te_po_base_url: Optional[str] = Field(default=None, alias="TE_PO_BASE_URL")

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
    tesseract_path: Optional[str] = Field(default=None, alias="TESSERACT_PATH")

    # Supabase tables
    supabase_table_ocr_logs: str = "ocr_logs"
    supabase_table_translations: str = "translations"
    supabase_table_embeddings: str = "embeddings"
    supabase_table_memory: str = "ti_memory"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"        # <-- Important
        populate_by_name = True

    def summary(self) -> Dict[str, Any]:
        """Return a masked snapshot of environment status."""
        return {
            "context": _env_state.get("context", "local"),
            "loaded_keys": _env_state.get("loaded_keys", []),
            "masked_secrets": _env_state.get("masked_preview", {}),
            "utf8_status": _env_state.get("utf8_status", {}),
            "source": _env_state.get("source", "system"),
        }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# global shared instance
settings = get_settings()
