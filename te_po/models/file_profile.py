from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FileProfile(BaseModel):
    source: str = Field(..., description="Pipeline source tag")
    filename: str
    storage_path: Optional[str] = None
    storage_bucket: Optional[str] = None
    storage_url: Optional[str] = None
    content_type: Optional[str] = None
    sha256: Optional[str] = None
    size: Optional[int] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    vector_batch_id: Optional[str] = None
    chunk_ids: List[str] = []
    extra: Dict[str, Any] = {}
