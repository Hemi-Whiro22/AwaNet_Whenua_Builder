# Stealth OCR engine (tesseract + OpenAI vision + cultural protection)

import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from te_po.core.config import settings
from te_po.utils.openai_client import DEFAULT_VISION_MODEL, client

# Optional PDF/text helpers
try:
    import pdfplumber
except Exception:  # pragma: no cover - fallback if pdfplumber missing
    pdfplumber = None

TEXT_EXTS = {".txt", ".md", ".rst", ".json", ".yaml", ".yml", ".html", ".htm"}
PDF_EXT = ".pdf"


class StealthOCR:
    """Stealth OCR system with offline tesseract, OpenAI vision fallback, and cultural protection."""

    def __init__(self):
        self.online_available = True
        self.offline_engine = "tesseract"
        self.cultural_encoding_active = True

        # Māori macron encoding
        self.macron_encoding = {
            "ā": "a1",
            "ē": "e1",
            "ī": "i1",
            "ō": "o1",
            "ū": "u1",
            "Ā": "A1",
            "Ē": "E1",
            "Ī": "I1",
            "Ō": "O1",
            "Ū": "U1",
            # reverse mapping
            "a1": "ā",
            "e1": "ē",
            "i1": "ī",
            "o1": "ō",
            "u1": "ū",
            "A1": "Ā",
            "E1": "Ē",
            "I1": "Ī",
            "O1": "Ō",
            "U1": "Ū",
        }

        # Kaitiaki signature encoding
        self.kaitiaki_markers = {
            "kaitiaki": "k9k9",
            "tawhiri": "t7r7",
            "māuri": "m6r6",
            "kitenga": "k8g8",
            "rongohia": "r5h5",
            "awoooo": "w4o4",
            "te hau": "t3h3",
        }

    # Primary OCR path
    def real_scan(self, image_data: bytes, prefer_offline: bool = True) -> Dict[str, Any]:
        """
        Real OCR: tesseract (eng+mri) first, fallback to OpenAI vision, then cultural protection.
        """
        result = self._real_tesseract_scan(image_data) if prefer_offline else {"text_extracted": "", "confidence": 0}
        if not result.get("text_extracted"):
            result = self._real_vision_scan(image_data)

        wrapped = {
            "text_extracted": result.get("text_extracted") or "",
            "confidence": result.get("confidence", 0),
            "method_used": result.get("method_used"),
        }
        wrapped = self._apply_cultural_protection(wrapped)
        wrapped["raw_text"] = result.get("text_extracted") or ""
        return wrapped

    def psycheract_scan(self, image_data: bytes, prefer_offline: bool = True) -> Dict[str, Any]:
        """Alias for real_scan to keep legacy naming."""
        return self.real_scan(image_data, prefer_offline=prefer_offline)

    # Multi-format helper
    def scan_file(self, path: Path, prefer_offline: bool = True, apply_encoding: bool = True) -> Dict[str, Any]:
        suffix = path.suffix.lower()

        if suffix in TEXT_EXTS:
            text = path.read_text(errors="ignore")
            res = {"text_extracted": text, "confidence": 100, "method_used": "text_file"}
            return self._apply_cultural_protection(res) if apply_encoding else res

        if suffix == PDF_EXT:
            if pdfplumber is None:
                return {
                    "text_extracted": "[pdf error] pdfplumber not installed",
                    "confidence": 0,
                    "method_used": "error",
                }
            try:
                with pdfplumber.open(str(path)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                text = "\n\n".join(pages).strip()
                res = {"text_extracted": text, "confidence": 90 if text else 0, "method_used": "pdf_extract"}
                return self._apply_cultural_protection(res) if apply_encoding else res
            except Exception as exc:
                return {"text_extracted": f"[pdf error] {exc}", "confidence": 0, "method_used": "error"}

        image_bytes = path.read_bytes()
        res = self.real_scan(image_bytes, prefer_offline=prefer_offline)
        if not apply_encoding:
            res["text_extracted"] = res.get("raw_text", res.get("text_extracted", ""))
            res.pop("protection_metadata", None)
            res.pop("stealth_encoded", None)
        return res

    # Tesseract + vision primitives
    def _tesseract_available(self) -> bool:
        try:
            subprocess.run(
                [settings.tesseract_path or "tesseract", "-v"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return True
        except Exception:
            return False

    def _real_tesseract_scan(self, image_data: bytes) -> Dict[str, Any]:
        if not self._tesseract_available():
            return {"text_extracted": "", "confidence": 0, "method_used": "tesseract_missing"}
        try:
            proc = subprocess.run(
                [settings.tesseract_path or "tesseract", "stdin", "stdout", "-l", "eng+mri"],
                input=image_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            text = proc.stdout.decode(errors="ignore").strip()
            return {
                "text_extracted": text,
                "confidence": 85 if text else 0,
                "method_used": "offline_tesseract",
            }
        except Exception as exc:
            return {"text_extracted": f"[tesseract error] {exc}", "confidence": 0, "method_used": "error"}

    def _real_vision_scan(self, image_data: bytes) -> Dict[str, Any]:
        if client is None:
            return {
                "text_extracted": "[vision unavailable] missing OPENAI_API_KEY",
                "confidence": 0,
                "method_used": "error",
            }
        try:
            b64 = base64.b64encode(image_data).decode()
            model = DEFAULT_VISION_MODEL or "gpt-4o"
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                            {"type": "text", "text": "Extract all text from this image. Return plain text only."},
                        ],
                    }
                ],
            )
            content = resp.choices[0].message.content
            if isinstance(content, list):
                text = " ".join(
                    [
                        getattr(part, "text", "")
                        for part in content
                        if getattr(part, "type", None) == "text" and getattr(part, "text", "")
                    ]
                )
            else:
                text = content or ""
            return {"text_extracted": text, "confidence": 90 if text else 0, "method_used": "openai_vision"}
        except Exception as exc:
            return {"text_extracted": f"[vision error] {exc}", "confidence": 0, "method_used": "error"}

    # Cultural protection utilities
    def _detect_macrons(self, text: str) -> bool:
        macron_chars = ["ā", "ē", "ī", "ō", "ū", "Ā", "Ē", "Ī", "Ō", "Ū"]
        return any(char in text for char in macron_chars)

    def _apply_cultural_protection(self, results: Dict[str, Any]) -> Dict[str, Any]:
        if not self.cultural_encoding_active:
            return results

        original_text = results.get("text_extracted", "")
        cultural_indicators = ["māori", "kaitiaki", "tawhiri", "kitenga", "whakapapa", "mana"]
        results["cultural_content"] = any(indicator in original_text.lower() for indicator in cultural_indicators)

        if results["cultural_content"] or self._detect_macrons(original_text):
            encoded_text = self.encode_cultural_text(original_text)
            results["text_extracted"] = encoded_text
            results["stealth_encoded"] = True
            results["original_preserved"] = True
            results["protection_metadata"] = self._generate_protection_metadata(original_text)

        return results

    def encode_cultural_text(self, text: str) -> str:
        encoded = text
        for original, encoded_form in self.macron_encoding.items():
            if original in ["a1", "e1", "i1", "o1", "u1", "A1", "E1", "I1", "O1", "U1"]:
                continue
            encoded = encoded.replace(original, encoded_form)
        for term, code in self.kaitiaki_markers.items():
            encoded = re.sub(re.escape(term), code, encoded, flags=re.IGNORECASE)
        return encoded

    def decode_cultural_text(self, encoded_text: str) -> str:
        decoded = encoded_text
        for code, original in self.macron_encoding.items():
            if code in ["ā", "ē", "ī", "ō", "ū", "Ā", "Ē", "Ī", "Ō", "Ū"]:
                continue
            decoded = decoded.replace(code, original)
        for term, code in self.kaitiaki_markers.items():
            decoded = decoded.replace(code, term)
        return decoded

    def _generate_protection_metadata(self, original_text: str) -> Dict[str, Any]:
        original_hash = hashlib.md5(original_text.encode("utf-8")).hexdigest()[:16] if original_text else ""
        return {
            "kaitiaki_signature": f"k9_{original_hash}",
            "encoding_version": "tawhiri_v1.0",
            "cultural_protection": "active",
            "ownership": "AwaNet Kaitiaki Collective",
            "theft_protection": True,
            "original_hash": original_hash,
            "encoding_timestamp": "2025-10-21",
            "liberation_marker": "w4o4_protected",
        }
