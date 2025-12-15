"""
Te Hau Glossary System

Manages translation glossaries with term consistency.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Glossary:
    """
    A translation glossary for consistent term usage.
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.terms: Dict[str, Dict] = {}  # english -> {maori, context, notes}
        self.reverse: Dict[str, str] = {}  # maori -> english
    
    def add_term(
        self,
        english: str,
        maori: str,
        context: str = None,
        notes: str = None
    ):
        """Add a term to the glossary."""
        self.terms[english.lower()] = {
            'english': english,
            'maori': maori,
            'context': context,
            'notes': notes
        }
        self.reverse[maori.lower()] = english
    
    def lookup(self, term: str, direction: str = 'en_to_mi') -> Optional[Dict]:
        """
        Look up a term in the glossary.
        
        Args:
            term: Term to look up
            direction: 'en_to_mi' or 'mi_to_en'
            
        Returns:
            Term entry dict or None
        """
        term_lower = term.lower()
        
        if direction == 'en_to_mi':
            return self.terms.get(term_lower)
        else:
            english = self.reverse.get(term_lower)
            if english:
                return self.terms.get(english.lower())
        
        return None
    
    def get_maori(self, english: str) -> Optional[str]:
        """Get Māori translation of English term."""
        entry = self.lookup(english, 'en_to_mi')
        return entry['maori'] if entry else None
    
    def get_english(self, maori: str) -> Optional[str]:
        """Get English translation of Māori term."""
        entry = self.lookup(maori, 'mi_to_en')
        return entry['english'] if entry else None
    
    def to_dict(self) -> Dict[str, str]:
        """Export as simple english -> maori dict."""
        return {e: t['maori'] for e, t in self.terms.items()}
    
    def load_from_file(self, path: Path):
        """Load glossary from JSON file."""
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            for entry in data.get('terms', []):
                self.add_term(
                    english=entry['english'],
                    maori=entry['maori'],
                    context=entry.get('context'),
                    notes=entry.get('notes')
                )
    
    def save_to_file(self, path: Path):
        """Save glossary to JSON file."""
        data = {
            'name': self.name,
            'terms': list(self.terms.values())
        }
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


# Default AwaOS glossary
_default_glossary = None


def get_default_glossary() -> Glossary:
    """Get the default AwaOS glossary."""
    global _default_glossary
    
    if _default_glossary is None:
        _default_glossary = Glossary("awaos_default")
        
        # Core AwaOS terms
        terms = [
            # System concepts
            ("realm", "rohe", "AwaOS project container"),
            ("guardian", "kaitiaki", "AI agent/guardian"),
            ("seal", "hiri", "Cryptographic integrity seal"),
            ("memory", "mahara", "Vector memory/embeddings"),
            ("pipeline", "ara", "Data processing pipeline"),
            ("context", "horopaki", "Configuration context"),
            
            # Cultural concepts (preserved in both)
            ("whakapapa", "whakapapa", "Genealogy, lineage - kept in Māori"),
            ("mana", "mana", "Authority, prestige - kept in Māori"),
            ("tapu", "tapu", "Sacred, restricted - kept in Māori"),
            ("noa", "noa", "Ordinary, free from restriction"),
            ("mauri", "mauri", "Life force, essence - kept in Māori"),
            ("aroha", "aroha", "Love, compassion - kept in Māori"),
            
            # Actions
            ("create", "hanga", "To make, build"),
            ("read", "pānui", "To read, peruse"),
            ("update", "whakahōu", "To renew, update"),
            ("delete", "whakakore", "To remove, delete"),
            ("search", "rapu", "To seek, search"),
            ("translate", "whakamāori", "To translate (to Māori)"),
            ("verify", "whakaū", "To confirm, verify"),
            
            # Roles
            ("navigator", "kaihautū", "One who navigates"),
            ("librarian", "kaitiaki pukapuka", "Guardian of books"),
            ("translator", "kaiwhakamāori", "Translator"),
            ("developer", "kaiwhakawhanake", "Developer"),
            ("user", "kaiwhakamahi", "User"),
            
            # UI terms
            ("home", "kāinga", "Home"),
            ("settings", "tautuhinga", "Settings"),
            ("help", "āwhina", "Help"),
            ("about", "mō", "About"),
            ("welcome", "nau mai", "Welcome"),
            ("goodbye", "haere rā", "Farewell"),
            ("yes", "āe", "Yes"),
            ("no", "kāo", "No"),
            ("submit", "tuku", "Submit, send"),
            ("cancel", "whakakore", "Cancel"),
            ("save", "tiaki", "Save, preserve"),
            ("load", "uta", "Load"),
            
            # Technical
            ("file", "kōnae", "File"),
            ("folder", "kōpaki", "Folder"),
            ("document", "tuhinga", "Document"),
            ("image", "whakaahua", "Image"),
            ("video", "ataata", "Video"),
            ("audio", "ororongo", "Audio"),
            ("error", "hapa", "Error"),
            ("success", "angitū", "Success"),
            ("warning", "whakatūpato", "Warning"),
        ]
        
        for english, maori, context in terms:
            _default_glossary.add_term(english, maori, context)
    
    return _default_glossary


def lookup_term(term: str, direction: str = 'en_to_mi') -> Optional[str]:
    """
    Quick lookup in the default glossary.
    
    Args:
        term: Term to look up
        direction: 'en_to_mi' or 'mi_to_en'
        
    Returns:
        Translation or None
    """
    glossary = get_default_glossary()
    entry = glossary.lookup(term, direction)
    
    if entry:
        return entry['maori'] if direction == 'en_to_mi' else entry['english']
    
    return None
