"""
Māori Language Support
======================
Automatic macron correction for proper te reo Māori spelling.

This module handles:
- Common misspellings without macrons (maori → māori)
- Applies macrons to Māori words in text, dicts, and lists
- Preserves all other content unchanged
"""

from typing import Any, Dict, Iterable

MACRON_MAP = {
    "maori": "māori",
    "mana": "māna",
    "kaitiaki": "kaitiaki",
    "whenua": "whenua",
    "wai": "wai",
    "aha": "aha",
    "te ao": "te ao",
    "marama": "mārama",
    "aroha": "aroha",
    "kapu": "kāpu",
    "karakia": "karakia",
    "taonga": "taonga",
    "whare": "whare",
    "whakaaro": "whakaaro",
    "whānau": "whānau",
    "pākehā": "pākehā",
    "tikanga": "tikanga",
}


def _replace_macrons(text: str) -> str:
    """Replace common misspellings with correct macron versions."""
    lowered = text.lower()
    for key, value in MACRON_MAP.items():
        if key in lowered:
            # Case-insensitive replace while preserving case
            text = text.replace(key, value)
            # Also handle capitalized versions
            text = text.replace(key.title(), value.title())
    return text


def macronize_text(text: str) -> str:
    """Apply macrons to Māori words in a text string."""
    if not text or not isinstance(text, str):
        return text
    return _replace_macrons(text)


def macronize_value(value: Any) -> Any:
    """Apply macrons to a value (str, dict, list, or other)."""
    if isinstance(value, str):
        return macronize_text(value)
    if isinstance(value, dict):
        return macronize_dict(value)
    if isinstance(value, list):
        return [macronize_value(elem) for elem in value]
    return value


def macronize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply macrons to all string values in a dictionary."""
    return {k: macronize_value(v) for k, v in data.items()}


def macronize_iterable(items: Iterable[Any]) -> list:
    """Apply macrons to all items in an iterable."""
    return [macronize_value(item) for item in items]
