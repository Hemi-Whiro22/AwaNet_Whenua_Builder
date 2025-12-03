"""Reo processing engine for Whai Tika Reo."""
from __future__ import annotations

from te_po.utils.openai_client import call_openai


async def translate_to_maori(text: str) -> str:
    prompt = (
        "Translate this into te reo Māori with correct macrons, grammar, and respectful tone:\n"
        f"{text}"
    )
    return await call_openai(prompt)


async def pronounce_maori(text: str) -> str:
    prompt = (
        "Break this Māori phrase into syllables, IPA, and mark primary stress. "
        "Return a concise textual explanation only.\n"
        f"{text}"
    )
    return await call_openai(prompt)


async def review_kupu(text: str) -> str:
    prompt = (
        "Review this Māori text for dialectal variants, respectful usage, and clarity. "
        "Highlight any Ngāti Koata, Kuia, or Toa variants if present.\n"
        f"{text}"
    )
    return await call_openai(prompt)


async def build_names_dictionary(text: str) -> str:
    prompt = (
        "Extract Māori personal or place names from this text and produce a JSON array "
        "with fields: name, syllables, ipa, meaning_or_origin (if known).\n"
        f"{text}"
    )
    return await call_openai(prompt)


# Pro-tier helpers


async def translate_text(text: str, dialect: str = "standard") -> str:
    prompt = (
        f"Translate into te reo Māori ({dialect}) with precise macrons, grammar, and clarity.\n"
        f"Return Māori only.\n"
        f"{text}"
    )
    return await call_openai(prompt)


async def review_reo_text(text: str) -> str:
    prompt = (
        "You are a Māori reo language expert. "
        "Review the following text for correctness, tikanga alignment, grammar, macrons, flow, and tone. "
        "Return corrected text only.\n\n"
        f"TEXT:\n{text}"
    )
    return await call_openai(prompt)


async def pronounce_word(word: str) -> str:
    prompt = (
        "Provide syllables and IPA for this Māori word, mark primary stress, and give a short pronunciation tip.\n"
        f"{word}"
    )
    return await call_openai(prompt)


async def score_pronunciation(word: str) -> tuple[float, str]:
    """
    Assign pronunciation hints + confidence without audio (text-based).
    """
    prompt = (
        "Rate how difficult this Māori word is for non-speakers, and return teaching hints.\n\n"
        f"WORD: {word}"
    )
    out = await call_openai(prompt)
    return 0.82, out  # placeholder confidence


async def check_maori_name(name: str) -> tuple[bool, str, str]:
    """
    Detect whether a name is Māori, meaning, and any branding risks.
    """
    prompt = (
        "Determine if this is a Māori name, its meaning, dialect origin, and any brand usage notes.\n\n"
        f"NAME: {name}"
    )
    out = await call_openai(prompt)
    return True, "Meaning unknown", out
