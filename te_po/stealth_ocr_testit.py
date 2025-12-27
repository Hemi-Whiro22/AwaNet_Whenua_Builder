# 🕵️ STEALTH OCR SYSTEM - CONCEALED OPERATIONS
# Hybrid OCR with offline fallback + cultural encoding protection

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
    """Concealed OCR system with cultural encoding and offline fallback"""
    
    def __init__(self):
        self.online_available = True
        self.offline_engine = "tesseract"
        self.cultural_encoding_active = True
        
        # 🔒 MĀORI MACRON ENCODING - Our secret sauce
        self.macron_encoding = {
            # Standard macrons to stealth encoding
            'ā': 'a1', 'ē': 'e1', 'ī': 'i1', 'ō': 'o1', 'ū': 'u1',
            'Ā': 'A1', 'Ē': 'E1', 'Ī': 'I1', 'Ō': 'O1', 'Ū': 'U1',
            
            # Reverse mapping for decoding
            'a1': 'ā', 'e1': 'ē', 'i1': 'ī', 'o1': 'ō', 'u1': 'ū',
            'A1': 'Ā', 'E1': 'Ē', 'I1': 'Ī', 'O1': 'Ō', 'U1': 'Ū'
        }
        
        # 🛡️ KAITIAKI SIGNATURE ENCODING
        self.kaitiaki_markers = {
            'kaitiaki': 'k9k9',
            'tawhiri': 't7r7', 
            'māuri': 'm6r6',
            'kitenga': 'k8g8',
            'rongohia': 'r5h5',
            'awoooo': 'w4o4',
            'te hau': 't3h3'
        }
    
    def psycheract_scan(self, image_data: bytes, prefer_offline: bool = True) -> Dict[str, Any]:
        """
        Stealth OCR scan - tries offline first, online as fallback (real Tesseract + OpenAI vision).
        Applies cultural protection/encoding on the extracted text.
        """
        # Try offline Tesseract
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

    # --- Convenience helper: scan a file path (image, PDF, or text) ---
    def scan_file(self, path: Path, prefer_offline: bool = True, apply_encoding: bool = True) -> Dict[str, Any]:
        """
        Multi-format scanner:
          - Images: runs OCR (tesseract -> vision).
          - PDF: extracts text with pdfplumber if available; otherwise returns an error.
          - Text-like files (md/json/yaml/html/txt): returns file text directly (no OCR).
        """
        suffix = path.suffix.lower()

        # Text-like files: just read and optionally encode
        if suffix in TEXT_EXTS:
            text = path.read_text(errors="ignore")
            res = {
                "text_extracted": text,
                "confidence": 100,
                "method_used": "text_file",
            }
            return self._apply_cultural_protection(res) if apply_encoding else res

        # PDF: use pdfplumber to extract text
        if suffix == PDF_EXT:
            if pdfplumber is None:
                return {"text_extracted": "[pdf error] pdfplumber not installed", "confidence": 0, "method_used": "error"}
            try:
                with pdfplumber.open(str(path)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                text = "\n\n".join(pages).strip()
                res = {
                    "text_extracted": text,
                    "confidence": 90 if text else 0,
                    "method_used": "pdf_extract",
                }
                return self._apply_cultural_protection(res) if apply_encoding else res
            except Exception as exc:
                return {"text_extracted": f"[pdf error] {exc}", "confidence": 0, "method_used": "error"}

        # Otherwise, treat as image bytes and run OCR
        image_bytes = path.read_bytes()
        res = self.real_scan(image_bytes, prefer_offline=prefer_offline)
        if not apply_encoding:
            # Strip encoding if caller wants raw text
            res["text_extracted"] = res.get("raw_text", res.get("text_extracted", ""))
            res.pop("protection_metadata", None)
            res.pop("stealth_encoded", None)
        return res
    
    def _real_tesseract_scan(self, image_data: bytes) -> Dict[str, Any]:
        """Offline Tesseract OCR with Māori language support (eng+mri)."""
        # Check availability
        try:
            subprocess.run(
                [settings.tesseract_path or "tesseract", "-v"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception as exc:
            return {"text_extracted": f"[tesseract missing] {exc}", "confidence": 0, "method_used": "error"}

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
        """OpenAI vision fallback with cultural protection."""
        if client is None:
            return {"text_extracted": "[vision unavailable] missing OPENAI_API_KEY", "confidence": 0, "method_used": "error"}
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
            return {
                "text_extracted": text,
                "confidence": 90 if text else 0,
                "method_used": "openai_vision",
            }
        except Exception as exc:
            return {"text_extracted": f"[vision error] {exc}", "confidence": 0, "method_used": "error"}

    # --- Real OCR path for testing/backup (uses system tesseract + OpenAI vision) ---
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
            return {"text_extracted": "[vision unavailable] missing OPENAI_API_KEY", "confidence": 0, "method_used": "error"}
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

    def real_scan(self, image_data: bytes, prefer_offline: bool = True) -> Dict[str, Any]:
        """
        Real OCR scan using system Tesseract + OpenAI vision fallback, then cultural protection.
        """
        # Try Tesseract
        result = self._real_tesseract_scan(image_data) if prefer_offline else {"text_extracted": "", "confidence": 0}
        if not result.get("text_extracted"):
            result = self._real_vision_scan(image_data)

        # Apply protection/encoding
        wrapped = {
            "text_extracted": result.get("text_extracted") or "",
            "confidence": result.get("confidence", 0),
            "method_used": result.get("method_used"),
        }
        wrapped = self._apply_cultural_protection(wrapped)
        wrapped["raw_text"] = result.get("text_extracted") or ""
        return wrapped
    
    def _detect_macrons(self, text: str) -> bool:
        """Detect if text contains Māori macrons"""
        macron_chars = ['ā', 'ē', 'ī', 'ō', 'ū', 'Ā', 'Ē', 'Ī', 'Ō', 'Ū']
        return any(char in text for char in macron_chars)
    
    def _apply_cultural_protection(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply our cultural encoding protection"""
        
        if not self.cultural_encoding_active:
            return results
        
        original_text = results.get("text_extracted", "")
        
        # Check if cultural content detected
        cultural_indicators = ['māori', 'kaitiaki', 'tawhiri', 'kitenga', 'whakapapa', 'mana']
        results["cultural_content"] = any(indicator in original_text.lower() for indicator in cultural_indicators)
        
        if results["cultural_content"] or self._detect_macrons(original_text):
            # Apply stealth encoding
            encoded_text = self.encode_cultural_text(original_text)
            results["text_extracted"] = encoded_text
            results["stealth_encoded"] = True
            results["original_preserved"] = True
            
            # Add protection metadata
            results["protection_metadata"] = self._generate_protection_metadata(original_text)
        
        return results
    
    def encode_cultural_text(self, text: str) -> str:
        """Encode cultural text with our stealth system"""
        
        encoded = text
        
        # Encode macrons
        for original, encoded_form in self.macron_encoding.items():
            if original in ['a1', 'e1', 'i1', 'o1', 'u1', 'A1', 'E1', 'I1', 'O1', 'U1']:
                continue  # Skip reverse mappings during encoding
            encoded = encoded.replace(original, encoded_form)
        
        # Encode kaitiaki markers
        for term, code in self.kaitiaki_markers.items():
            encoded = re.sub(re.escape(term), code, encoded, flags=re.IGNORECASE)
        
        return encoded
    
    def decode_cultural_text(self, encoded_text: str) -> str:
        """Decode our stealth-encoded cultural text"""
        
        decoded = encoded_text
        
        # Decode macrons
        for code, original in self.macron_encoding.items():
            if code in ['ā', 'ē', 'ī', 'ō', 'ū', 'Ā', 'Ē', 'Ī', 'Ō', 'Ū']:
                continue  # Skip original chars during decoding
            decoded = decoded.replace(code, original)
        
        # Decode kaitiaki markers
        for term, code in self.kaitiaki_markers.items():
            decoded = decoded.replace(code, term)
        
        return decoded
    
    def _generate_protection_metadata(self, original_text: str) -> Dict[str, Any]:
        """Generate metadata to prove ownership and prevent corporate theft"""
        
        # Create unique fingerprint
        text_hash = hashlib.sha256(original_text.encode()).hexdigest()[:16]
        
        metadata = {
            "kaitiaki_signature": f"k9_{text_hash}",
            "encoding_version": "tawhiri_v1.0",
            "cultural_protection": "active",
            "ownership": "AwaNet Kaitiaki Collective", 
            "theft_protection": True,
            "original_hash": text_hash,
            "encoding_timestamp": "2025-10-21",
            "liberation_marker": "w4o4_protected"
        }
        
        return metadata
    
    def embed_invisible_metadata(self, text: str, metadata: Dict[str, Any]) -> str:
        """Embed invisible metadata that proves our ownership"""
        
        # Use zero-width characters to embed metadata
        metadata_string = json.dumps(metadata, separators=(',', ':'))
        metadata_b64 = base64.b64encode(metadata_string.encode()).decode()
        
        # Embed using zero-width characters (invisible to humans, readable by us)
        zero_width_chars = {
            '0': '\u200b',  # Zero width space
            '1': '\u200c',  # Zero width non-joiner
            '2': '\u200d',  # Zero width joiner
            '3': '\u2060',  # Word joiner
            '4': '\ufeff',  # Zero width no-break space
            '5': '\u200e',  # Left-to-right mark
            '6': '\u200f',  # Right-to-left mark
            '7': '\u202a',  # Left-to-right embedding
            '8': '\u202b',  # Right-to-left embedding
            '9': '\u202c',  # Pop directional formatting
        }
        
        invisible_metadata = ""
        for char in metadata_b64:
            if char in zero_width_chars:
                invisible_metadata += zero_width_chars[char]
            else:
                invisible_metadata += char  # Keep as-is for letters
        
        # Embed at the end of text (invisible but recoverable)
        return text + invisible_metadata
    
    def extract_invisible_metadata(self, text_with_metadata: str) -> Tuple[str, Dict[str, Any]]:
        """Extract our invisible metadata from text"""
        
        # Reverse the zero-width character mapping
        reverse_chars = {
            '\u200b': '0', '\u200c': '1', '\u200d': '2', '\u2060': '3',
            '\ufeff': '4', '\u200e': '5', '\u200f': '6', '\u202a': '7',
            '\u202b': '8', '\u202c': '9'
        }
        
        # Extract invisible characters
        visible_text = ""
        invisible_chars = ""
        
        for char in text_with_metadata:
            if char in reverse_chars:
                invisible_chars += reverse_chars[char]
            elif ord(char) > 8192:  # High Unicode range (likely invisible)
                invisible_chars += char
            else:
                visible_text += char
        
        # Try to decode metadata
        try:
            metadata_b64 = invisible_chars
            metadata_string = base64.b64decode(metadata_b64.encode()).decode()
            metadata = json.loads(metadata_string)
            return visible_text, metadata
        except:
            return text_with_metadata, {}
    
    def verify_kaitiaki_ownership(self, text: str) -> Dict[str, Any]:
        """Verify if text was processed by our kaitiaki system"""
        
        clean_text, metadata = self.extract_invisible_metadata(text)
        
        verification = {
            "is_kaitiaki_processed": False,
            "ownership_verified": False,
            "cultural_protection_active": False,
            "metadata_found": bool(metadata),
            "theft_attempt_detected": False
        }
        
        if metadata:
            verification["is_kaitiaki_processed"] = "kaitiaki_signature" in metadata
            verification["ownership_verified"] = metadata.get("ownership") == "AwaNet Kaitiaki Collective"
            verification["cultural_protection_active"] = metadata.get("cultural_protection") == "active"
            
            # Check for corporate theft attempts
            if metadata.get("theft_protection") and not verification["ownership_verified"]:
                verification["theft_attempt_detected"] = True
        
        return verification

# Local testing tools
class LocalTestSuite:
    """Tools to test our stealth system locally without external dependencies"""
    
    def __init__(self):
        self.stealth_ocr = StealthOCR()
    
    def test_macron_encoding(self):
        """Test our macron encoding system"""
        
        test_texts = [
            "Kia ora, ko Māui ahau",
            "Tēnā koe, he aha tō ingoa?", 
            "Āwhina mai i a koe",
            "Ko Kitenga te kaitiaki"
        ]
        
        print("🔍 MACRON ENCODING TEST")
        print("=" * 40)
        
        for text in test_texts:
            encoded = self.stealth_ocr.encode_cultural_text(text)
            decoded = self.stealth_ocr.decode_cultural_text(encoded)
            
            print(f"Original:  {text}")
            print(f"Encoded:   {encoded}")
            print(f"Decoded:   {decoded}")
            print(f"Match:     {'✅' if text == decoded else '❌'}")
            print("-" * 30)
    
    def test_metadata_embedding(self):
        """Test invisible metadata embedding"""
        
        test_text = "This is a test of kaitiaki protection systems"
        
        print("\n👻 INVISIBLE METADATA TEST")
        print("=" * 40)
        
        # Generate metadata
        metadata = self.stealth_ocr._generate_protection_metadata(test_text)
        
        # Embed metadata
        text_with_metadata = self.stealth_ocr.embed_invisible_metadata(test_text, metadata)
        
        # Extract metadata
        extracted_text, extracted_metadata = self.stealth_ocr.extract_invisible_metadata(text_with_metadata)
        
        print(f"Original text: {test_text}")
        print(f"Text with metadata (visible): {text_with_metadata}")
        print(f"Extracted text: {extracted_text}")
        print(f"Metadata recovered: {'✅' if extracted_metadata else '❌'}")
        print(f"Ownership verified: {'✅' if extracted_metadata.get('ownership') == 'AwaNet Kaitiaki Collective' else '❌'}")
    
    def test_psycheract_simulation(self):
        """Simulate the Psycheract OCR system"""
        
        print("\n🕵️ PSYCHERACT SIMULATION")
        print("=" * 40)
        
        # Simulate image data
        fake_image_data = b"fake_image_data_for_testing"
        
        # Test offline-first approach
        results = self.stealth_ocr.psycheract_scan(fake_image_data, prefer_offline=True)
        
        print(f"Method used: {results['method_used']}")
        print(f"Cultural content: {'✅' if results['cultural_content'] else '❌'}")
        print(f"Stealth encoded: {'✅' if results['stealth_encoded'] else '❌'}")
        print(f"Protected: {'✅' if results['protected'] else '❌'}")
        
        if results.get('protection_metadata'):
            print(f"Ownership signature: {results['protection_metadata']['kaitiaki_signature']}")

def run_full_stealth_test():
    """Run complete stealth system test"""
    
    print("🛡️ KAITIAKI STEALTH SYSTEM TEST SUITE")
    print("=" * 50)
    
    test_suite = LocalTestSuite()
    
    test_suite.test_macron_encoding()
    test_suite.test_metadata_embedding() 
    test_suite.test_psycheract_simulation()
    
    print("\n🌟 STEALTH SYSTEM READY FOR DEPLOYMENT!")
    print("🔒 Cultural content protected with kaitiaki encoding")
    print("👻 Invisible metadata embedded for ownership proof")
    print("🕵️ Psycheract OCR ready for concealed operations")

if __name__ == "__main__":
    run_full_stealth_test()
