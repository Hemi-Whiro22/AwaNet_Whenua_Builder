"""
Ahiatoa - The Translator Kaitiaki

Specialized kaitiaki for cultural-grade translation.
"""

from typing import Dict, List, Optional
from te_hau.core.kaitiaki import Kaitiaki, CORE_KAITIAKI
from te_hau.translator.glossary import get_default_glossary, Glossary


class Ahiatoa(Kaitiaki):
    """
    Ahiatoa - the Translator kaitiaki.
    
    Specialized for te reo Māori translation with:
    - Glossary enforcement
    - Macron validation
    - Dialect awareness
    - Cultural context preservation
    """
    
    def __init__(self, realm_name: str = None, glossary: Glossary = None):
        super().__init__('ahiatoa', realm_name)
        self.glossary = glossary or get_default_glossary()
        self.dialect = None
        self.strict_glossary = True
    
    def set_dialect(self, dialect: str):
        """Set preferred dialect."""
        self.dialect = dialect
    
    def set_glossary(self, glossary: Glossary):
        """Set custom glossary."""
        self.glossary = glossary
    
    def translate_to_maori(
        self,
        text: str,
        context: str = None,
        preserve_formatting: bool = True
    ) -> str:
        """
        Translate English to te reo Māori.
        
        Args:
            text: English text
            context: Additional context for translation
            preserve_formatting: Keep original formatting
            
        Returns:
            Te reo Māori translation
        """
        from te_hau.translator.core import translate_to_maori, fix_macrons
        
        # Pre-process with glossary
        glossary_dict = self.glossary.to_dict()
        
        # Build context
        full_context = {}
        if context:
            full_context['instruction'] = context
        if self.dialect:
            full_context['dialect'] = self.dialect
        
        # Translate
        result = translate_to_maori(
            text,
            model=self.config.get('model', 'gpt-4o'),
            glossary=glossary_dict if self.strict_glossary else None,
            dialect=self.dialect
        )
        
        # Post-process
        result = fix_macrons(result)
        
        return result
    
    def translate_to_english(
        self,
        text: str,
        preserve_cultural_terms: bool = True
    ) -> str:
        """
        Translate te reo Māori to English.
        
        Args:
            text: Te reo Māori text
            preserve_cultural_terms: Keep important Māori terms
            
        Returns:
            English translation
        """
        from te_hau.translator.core import translate_to_english
        
        # Terms to preserve
        preserve = None
        if preserve_cultural_terms:
            preserve = [
                'whakapapa', 'mana', 'tapu', 'noa', 'mauri', 'aroha',
                'kaitiaki', 'tangata whenua', 'iwi', 'hapū', 'whānau'
            ]
        
        return translate_to_english(
            text,
            model=self.config.get('model', 'gpt-4o'),
            preserve_terms=preserve
        )
    
    def validate_translation(self, original: str, translation: str) -> Dict:
        """
        Validate a translation for quality.
        
        Args:
            original: Original text
            translation: Translated text
            
        Returns:
            Validation report
        """
        from te_hau.translator.core import validate_macrons, detect_language
        
        report = {
            'valid': True,
            'issues': [],
            'suggestions': []
        }
        
        # Check macrons
        macron_valid, macron_issues = validate_macrons(translation)
        if not macron_valid:
            report['valid'] = False
            report['issues'].extend(macron_issues)
        
        # Check glossary compliance
        glossary_terms = self.glossary.to_dict()
        for eng, mao in glossary_terms.items():
            if eng.lower() in original.lower():
                if mao.lower() not in translation.lower():
                    report['suggestions'].append(
                        f"Consider using '{mao}' for '{eng}'"
                    )
        
        return report
    
    def get_term(self, term: str, direction: str = 'en_to_mi') -> Optional[str]:
        """
        Look up a term in the glossary.
        
        Args:
            term: Term to look up
            direction: 'en_to_mi' or 'mi_to_en'
            
        Returns:
            Translation or None
        """
        entry = self.glossary.lookup(term, direction)
        if entry:
            return entry['maori'] if direction == 'en_to_mi' else entry['english']
        return None


# Global Ahiatoa instance
_ahiatoa: Optional[Ahiatoa] = None


def get_ahiatoa(realm_name: str = None) -> Ahiatoa:
    """
    Get the Ahiatoa translator instance.
    
    Args:
        realm_name: Optional realm context
        
    Returns:
        Ahiatoa instance
    """
    global _ahiatoa
    
    if _ahiatoa is None or _ahiatoa.realm_name != realm_name:
        _ahiatoa = Ahiatoa(realm_name)
    
    return _ahiatoa
