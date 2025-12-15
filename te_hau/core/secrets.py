"""
Te Hau Secrets Module

Secure key generation and management for AwaOS realms.
"""

import secrets
import hashlib
import uuid
import json
import time
from typing import Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta


# Token expiry (default 30 days)
DEFAULT_TOKEN_EXPIRY_DAYS = 30


def generate_bearer_token(expiry_days: int = DEFAULT_TOKEN_EXPIRY_DAYS) -> Tuple[str, str, float]:
    """
    Generate a secure bearer token with expiry.
    
    Returns:
        Tuple of (plaintext_token, sha256_hash, expiry_timestamp)
    """
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expiry = time.time() + (expiry_days * 24 * 60 * 60)
    return token, token_hash, expiry


def generate_bearer_token_simple() -> Tuple[str, str]:
    """
    Generate a secure bearer token and its hash (no expiry).
    
    Returns:
        Tuple of (plaintext_token, sha256_hash)
    """
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def generate_realm_id() -> str:
    """
    Generate a unique realm identifier.
    
    Returns:
        Realm ID in format 'realm-{uuid_prefix}'
    """
    return f"realm-{uuid.uuid4().hex[:12]}"


def generate_pipeline_token() -> str:
    """
    Generate a token for pipeline authentication.
    
    Returns:
        16-byte hex token
    """
    return secrets.token_hex(16)


def generate_seal_hash(content: str) -> str:
    """
    Generate a SHA-256 seal hash from content.
    
    Args:
        content: String content to hash
        
    Returns:
        Hash in format 'sha256:{hash}'
    """
    hash_value = hashlib.sha256(content.encode()).hexdigest()
    return f"sha256:{hash_value}"


def verify_seal(content: str, seal: str) -> bool:
    """
    Verify a seal hash matches content.
    
    Args:
        content: Original content
        seal: Expected seal hash
        
    Returns:
        True if seal matches
    """
    expected = generate_seal_hash(content)
    return secrets.compare_digest(expected, seal)


def hash_token(token: str) -> str:
    """
    Hash a token for storage comparison.
    
    Args:
        token: Plaintext token
        
    Returns:
        SHA-256 hash
    """
    return hashlib.sha256(token.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════
# TOKEN REFRESH SYSTEM
# ═══════════════════════════════════════════════════════════════

class TokenStore:
    """
    Manage bearer tokens with refresh capability.
    
    Tokens are stored in mauri/tokens.json with expiry times.
    """
    
    def __init__(self, realm_path: Path):
        self.realm_path = Path(realm_path)
        self.tokens_file = self.realm_path / "mauri" / "tokens.json"
        self._tokens: Dict = {}
        self._load()
    
    def _load(self):
        """Load tokens from file."""
        if self.tokens_file.exists():
            with open(self.tokens_file) as f:
                self._tokens = json.load(f)
        else:
            self._tokens = {
                "active_hash": None,
                "expiry": None,
                "refresh_hash": None,
                "refresh_expiry": None,
                "history": []
            }
    
    def _save(self):
        """Save tokens to file."""
        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tokens_file, 'w') as f:
            json.dump(self._tokens, f, indent=2)
    
    def generate_tokens(self) -> Tuple[str, str]:
        """
        Generate new access and refresh tokens.
        
        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Generate access token (short-lived)
        access_token, access_hash, access_expiry = generate_bearer_token(expiry_days=1)
        
        # Generate refresh token (long-lived)
        refresh_token, refresh_hash, refresh_expiry = generate_bearer_token(expiry_days=30)
        
        # Archive old token
        if self._tokens.get("active_hash"):
            self._tokens["history"].append({
                "hash": self._tokens["active_hash"],
                "expired_at": datetime.utcnow().isoformat(),
                "reason": "refresh"
            })
            # Keep only last 10 in history
            self._tokens["history"] = self._tokens["history"][-10:]
        
        # Store new tokens
        self._tokens["active_hash"] = access_hash
        self._tokens["expiry"] = access_expiry
        self._tokens["refresh_hash"] = refresh_hash
        self._tokens["refresh_expiry"] = refresh_expiry
        self._tokens["generated_at"] = datetime.utcnow().isoformat()
        
        self._save()
        return access_token, refresh_token
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a bearer token.
        
        Args:
            token: Plaintext token to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        token_hash = hash_token(token)
        
        # Check if it's the active token
        if secrets.compare_digest(token_hash, self._tokens.get("active_hash", "")):
            # Check expiry
            expiry = self._tokens.get("expiry", 0)
            if time.time() > expiry:
                return False, "token_expired"
            return True, None
        
        # Check if it's in history (revoked)
        for hist in self._tokens.get("history", []):
            if secrets.compare_digest(token_hash, hist.get("hash", "")):
                return False, "token_revoked"
        
        return False, "invalid_token"
    
    def refresh(self, refresh_token: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Use refresh token to get new access token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token) or (None, error)
        """
        token_hash = hash_token(refresh_token)
        
        # Validate refresh token
        if not secrets.compare_digest(token_hash, self._tokens.get("refresh_hash", "")):
            return None, "invalid_refresh_token"
        
        # Check refresh token expiry
        if time.time() > self._tokens.get("refresh_expiry", 0):
            return None, "refresh_token_expired"
        
        # Generate new tokens
        access_token, new_refresh_token = self.generate_tokens()
        return access_token, new_refresh_token
    
    def revoke(self, reason: str = "manual"):
        """Revoke current tokens."""
        if self._tokens.get("active_hash"):
            self._tokens["history"].append({
                "hash": self._tokens["active_hash"],
                "expired_at": datetime.utcnow().isoformat(),
                "reason": reason
            })
        
        self._tokens["active_hash"] = None
        self._tokens["expiry"] = None
        self._tokens["refresh_hash"] = None
        self._tokens["refresh_expiry"] = None
        
        self._save()
    
    def get_status(self) -> Dict:
        """Get token status info."""
        expiry = self._tokens.get("expiry", 0)
        refresh_expiry = self._tokens.get("refresh_expiry", 0)
        now = time.time()
        
        return {
            "has_active_token": bool(self._tokens.get("active_hash")),
            "access_expired": now > expiry if expiry else True,
            "access_expires_in": max(0, int(expiry - now)) if expiry else 0,
            "refresh_expired": now > refresh_expiry if refresh_expiry else True,
            "refresh_expires_in": max(0, int(refresh_expiry - now)) if refresh_expiry else 0,
            "generated_at": self._tokens.get("generated_at"),
            "revocation_history": len(self._tokens.get("history", []))
        }


def create_token_store(realm_path: str | Path) -> TokenStore:
    """Create a TokenStore for a realm."""
    return TokenStore(Path(realm_path))

