"""
Ruru PDF Summarizer
Migrated from te_po/ruru/prompts/tools/pdf_summariser.py
"""
from datetime import datetime, timezone
import uuid
from pathlib import Path
from typing import Dict

import fitz


def summarise_pdf(
    file_path: str,
    max_length: int = 1000,
) -> Dict:
    """
    Extract and summarise PDF content with cultural lens.

    Args:
        file_path: Path to the PDF file.
        max_length: Maximum character length for summary.

    Returns:
        Dictionary containing summary and metadata.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    summary = text[:max_length] + "..." if len(text) > max_length else text

    entry = {
        "id": str(uuid.uuid4()),
        "file_name": Path(file_path).name,
        "summary": summary,
        "full_text": text,
        "full_text_length": len(text),
        "whakatauki": "He manu hou ahau, he pi ka rere — I am a new bird, a fledgling just learning to fly.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "kaupapa_tags": [],
        "tapu_level": 0,
    }

    print(f"🦉 Ruru summarised: {entry['file_name']}")
    return entry


