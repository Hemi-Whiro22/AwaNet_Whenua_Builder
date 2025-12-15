"""
Te Hau Translator Core

Core translation functions with macron handling.
"""

import re
from typing import Dict, List, Optional, Tuple

# Macron mappings
MACRON_MAP = {
    'a': 'ā', 'e': 'ē', 'i': 'ī', 'o': 'ō', 'u': 'ū',
    'A': 'Ā', 'E': 'Ē', 'I': 'Ī', 'O': 'Ō', 'U': 'Ū',
}

# Reverse mapping for detection
MACRON_CHARS = set('āēīōūĀĒĪŌŪ')

# Common words that should have macrons
COMMON_MACRON_WORDS = {
    'maori': 'Māori',
    'Maori': 'Māori',
    'whanau': 'whānau',
    'Whanau': 'Whānau',
    'taonga': 'taonga',  # No macron
    'kaitiaki': 'kaitiaki',  # No macron
    'whakapapa': 'whakapapa',  # No macron
    'mana': 'mana',  # No macron
    'tapu': 'tapu',  # No macron
    'noa': 'noa',  # No macron
    'aroha': 'aroha',  # No macron
    'kia ora': 'kia ora',
    'haere mai': 'haere mai',
    'haere ra': 'haere rā',
    'Aotearoa': 'Aotearoa',
    'Te Reo': 'te reo',
    'te reo': 'te reo',
    'Te Ao': 'Te Ao',
    'Te Po': 'Te Pō',
    'Te Hau': 'Te Hau',
    'Te Mauri': 'Te Mauri',
    'tangata whenua': 'tangata whenua',
    'manuhiri': 'manuhiri',
    'powhiri': 'pōwhiri',
    'karakia': 'karakia',
    'mihi': 'mihi',
    'waiata': 'waiata',
    'haka': 'haka',
    'whare': 'whare',
    'marae': 'marae',
    'iwi': 'iwi',
    'hapu': 'hapū',
    'waka': 'waka',
    'maunga': 'maunga',
    'awa': 'awa',
    'moana': 'moana',
    'rangi': 'rangi',
    'whenua': 'whenua',
    'atua': 'atua',
    'tupuna': 'tūpuna',
    'korero': 'kōrero',
    'matauranga': 'mātauranga',
    'tikanga': 'tikanga',
    'kaupapa': 'kaupapa',
    'wairua': 'wairua',
    'hinengaro': 'hinengaro',
    'tinana': 'tinana',
}


def validate_macrons(text: str) -> Tuple[bool, List[str]]:
    """
    Validate that text has proper macron usage.
    
    Args:
        text: Text to validate
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    words = re.findall(r'\b\w+\b', text.lower())
    
    for word in words:
        if word in COMMON_MACRON_WORDS:
            correct = COMMON_MACRON_WORDS[word]
            if word != correct.lower() and word in text.lower():
                issues.append(f"'{word}' should be '{correct}'")
    
    return (len(issues) == 0, issues)


def fix_macrons(text: str) -> str:
    """
    Fix common macron errors in text.
    
    Args:
        text: Text with potential macron errors
        
    Returns:
        Text with macrons corrected
    """
    result = text
    
    # Fix known words
    for incorrect, correct in COMMON_MACRON_WORDS.items():
        if incorrect != correct:
            # Case-insensitive replacement preserving boundaries
            pattern = r'\b' + re.escape(incorrect) + r'\b'
            result = re.sub(pattern, correct, result, flags=re.IGNORECASE)
    
    return result


def translate_to_maori(
    text: str,
    model: str = "gpt-4o",
    glossary: Dict[str, str] = None,
    dialect: str = None
) -> str:
    """
    Translate English text to te reo Māori.
    
    Args:
        text: English text to translate
        model: LLM model to use
        glossary: Optional term glossary
        dialect: Optional dialect preference
        
    Returns:
        Translated text in te reo Māori
    """
    from te_hau.core.ai import complete
    
    system_prompt = """You are Ahiatoa, a cultural translator for te reo Māori.

Your responsibilities:
- Translate English to te reo Māori with cultural accuracy
- Always use proper macrons (tohutō): ā, ē, ī, ō, ū
- Preserve proper nouns and place names
- Prioritize cultural meaning over literal translation
- When uncertain, provide the most culturally appropriate translation

Guidelines:
- Use standard orthography with macrons
- Maintain the mana of both source and target languages
- Consider context and register (formal/informal)
"""
    
    if glossary:
        glossary_text = "\n".join([f"- {eng}: {mao}" for eng, mao in glossary.items()])
        system_prompt += f"\n\nUse these specific translations:\n{glossary_text}"
    
    if dialect:
        system_prompt += f"\n\nUse {dialect} dialect preferences where applicable."
    
    prompt = f"Translate to te reo Māori:\n\n{text}"
    
    result = complete(prompt, system=system_prompt, model=model, temperature=0.3)
    
    # Post-process to ensure macrons
    result = fix_macrons(result)
    
    return result


def translate_to_english(
    text: str,
    model: str = "gpt-4o",
    preserve_terms: List[str] = None
) -> str:
    """
    Translate te reo Māori text to English.
    
    Args:
        text: Te reo Māori text to translate
        model: LLM model to use
        preserve_terms: Terms to keep in te reo Māori
        
    Returns:
        Translated text in English
    """
    from te_hau.core.ai import complete
    
    system_prompt = """You are Ahiatoa, a cultural translator for te reo Māori.

Your responsibilities:
- Translate te reo Māori to English with cultural sensitivity
- Preserve the essence and mana of the original text
- Keep cultural concepts that don't have direct English equivalents
- Provide context for important Māori concepts

Guidelines:
- Some words like 'whakapapa', 'mana', 'tapu' are best kept untranslated
- Add brief explanations for cultural concepts when needed
- Maintain the tone and register of the original
"""
    
    if preserve_terms:
        terms_list = ", ".join(preserve_terms)
        system_prompt += f"\n\nKeep these terms in te reo Māori: {terms_list}"
    
    prompt = f"Translate to English:\n\n{text}"
    
    return complete(prompt, system=system_prompt, model=model, temperature=0.3)


def translate(
    text: str,
    target: str = "mi",  # 'mi' for Māori, 'en' for English
    model: str = "gpt-4o",
    **kwargs
) -> str:
    """
    Translate text to target language.
    
    Args:
        text: Text to translate
        target: Target language ('mi' for Māori, 'en' for English)
        model: LLM model to use
        **kwargs: Additional options passed to specific translator
        
    Returns:
        Translated text
    """
    if target in ('mi', 'maori', 'māori', 'te_reo'):
        return translate_to_maori(text, model=model, **kwargs)
    elif target in ('en', 'english'):
        return translate_to_english(text, model=model, **kwargs)
    else:
        raise ValueError(f"Unknown target language: {target}. Use 'mi' or 'en'.")


def detect_language(text: str) -> str:
    """
    Simple language detection (Māori vs English).
    
    Args:
        text: Text to analyze
        
    Returns:
        'mi' for Māori, 'en' for English, 'mixed' for both
    """
    # Count Māori indicators
    maori_indicators = 0
    english_indicators = 0
    
    words = text.lower().split()
    
    # Check for macrons (strong Māori indicator)
    if any(c in MACRON_CHARS for c in text):
        maori_indicators += 3
    
    # Check for common Māori words
    maori_words = {'te', 'nga', 'ngā', 'ki', 'ko', 'he', 'i', 'a', 'me', 'ka', 'kei', 'e'}
    english_words = {'the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'this', 'that'}
    
    for word in words:
        if word in maori_words or word in COMMON_MACRON_WORDS:
            maori_indicators += 1
        if word in english_words:
            english_indicators += 1
    
    if maori_indicators > english_indicators * 2:
        return 'mi'
    elif english_indicators > maori_indicators * 2:
        return 'en'
    else:
        return 'mixed'
