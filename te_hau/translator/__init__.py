"""
Te Hau Translator Module

Cultural-grade te reo Māori translation with Ahiatoa kaitiaki.
"""

from te_hau.translator.core import (
    translate,
    translate_to_maori,
    translate_to_english,
    validate_macrons,
    fix_macrons,
)
from te_hau.translator.glossary import (
    Glossary,
    get_default_glossary,
    lookup_term,
)
from te_hau.translator.ahiatoa import (
    Ahiatoa,
    get_ahiatoa,
)

__all__ = [
    'translate',
    'translate_to_maori',
    'translate_to_english',
    'validate_macrons',
    'fix_macrons',
    'Glossary',
    'get_default_glossary',
    'lookup_term',
    'Ahiatoa',
    'get_ahiatoa',
]
