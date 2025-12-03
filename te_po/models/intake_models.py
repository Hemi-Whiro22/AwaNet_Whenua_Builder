from pydantic import BaseModel
from typing import Optional


class OCRResult(BaseModel):
    id: str
    text: str
    saved: bool


class SummarizeRequest(BaseModel):
    text: str
    mode: str  # "research" | "taonga"


class SummarizeResult(BaseModel):
    id: str
    summary: str
    mode: str
    saved: bool
