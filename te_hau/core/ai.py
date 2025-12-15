"""
AI Module - Routes ALL AI calls through Te Pō via Awa Protocol.

Architecture:
    Te Hau CLI → mini_te_po → Te Pō → OpenAI/Supabase
    
No API keys are stored here. All calls go through:
    - TEPO_URL/awa/vector/embed (embeddings)
    - TEPO_URL/awa/chat (completions)
    - TEPO_URL/awa/kaitiaki/invoke (kaitiaki operations)

Mock mode (AWAOS_MOCK_AI=true) for testing without Te Pō connection.
"""

import os
import hashlib
import logging
import httpx
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Te Pō connection
TEPO_URL = os.getenv("TEPO_URL", "http://localhost:8000")
TEPO_BEARER = os.getenv("TEPO_BEARER", "")

# Mock mode for testing
MOCK_AI = os.getenv("AWAOS_MOCK_AI", "").lower() in ("true", "1", "yes")


@dataclass
class EmbeddingResult:
    """Result from embedding with tapu status."""
    embedding: list[float]
    tapu: bool = False
    realm_id: Optional[str] = None
    
    def check_access(self, requestor_realm: Optional[str] = None) -> bool:
        """
        Check if access is allowed to this embedding.
        
        Args:
            requestor_realm: The realm requesting access
            
        Returns:
            True if access allowed, False if blocked by tapu
        """
        if not self.tapu:
            return True
        # Tapu content only accessible by same realm
        if self.realm_id and requestor_realm == self.realm_id:
            return True
        return False


class TapuAccessError(Exception):
    """Raised when tapu content is accessed without permission."""
    pass


def _get_headers() -> dict:
    """Get headers for Te Pō requests."""
    headers = {"Content-Type": "application/json"}
    if TEPO_BEARER:
        headers["Authorization"] = f"Bearer {TEPO_BEARER}"
    return headers


def _generate_mock_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """
    Generate deterministic mock embedding for testing.
    Same text always produces same embedding.
    """
    # Hash the text to get deterministic seed
    hash_bytes = hashlib.sha256(text.encode()).digest()
    
    # Convert to floats in [-1, 1] range
    embedding = []
    for i in range(dimensions):
        # Use cycling through hash bytes
        byte_val = hash_bytes[i % len(hash_bytes)]
        # Add position influence for variation
        val = ((byte_val + i) % 256) / 128.0 - 1.0
        embedding.append(val)
    
    # Normalize to unit length
    magnitude = sum(x * x for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding


def _generate_mock_completion(prompt: str) -> str:
    """Generate mock completion for testing."""
    return f"[Mock Response] Received prompt of {len(prompt)} characters. Te Pō connection not configured."


async def embed_text(
    text: str, 
    model: str = "text-embedding-3-small",
    tapu: bool = False,
    realm_id: Optional[str] = None
) -> EmbeddingResult:
    """
    Get embedding for text via Te Pō.
    
    Args:
        text: Text to embed
        model: Model to use (passed to Te Pō)
        tapu: Mark embedding as tapu (restricted access)
        realm_id: Realm this embedding belongs to
        
    Returns:
        EmbeddingResult with embedding vector and tapu status
    """
    if MOCK_AI:
        logger.info("Mock mode: generating deterministic embedding")
        return EmbeddingResult(
            embedding=_generate_mock_embedding(text),
            tapu=tapu,
            realm_id=realm_id
        )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{TEPO_URL}/awa/vector/embed",
                headers=_get_headers(),
                json={
                    "text": text, 
                    "model": model,
                    "tapu": tapu,
                    "realm_id": realm_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return EmbeddingResult(
                embedding=data.get("embedding", []),
                tapu=data.get("tapu", tapu),
                realm_id=data.get("realm_id", realm_id)
            )
    except httpx.HTTPError as e:
        logger.error(f"Te Pō embed request failed: {e}")
        if MOCK_AI:
            return EmbeddingResult(
                embedding=_generate_mock_embedding(text),
                tapu=tapu,
                realm_id=realm_id
            )
        raise RuntimeError(f"Failed to get embedding from Te Pō: {e}")


def embed_text_sync(
    text: str, 
    model: str = "text-embedding-3-small",
    tapu: bool = False,
    realm_id: Optional[str] = None
) -> EmbeddingResult:
    """
    Synchronous version of embed_text.
    
    Args:
        text: Text to embed
        model: Model to use (passed to Te Pō)
        tapu: Mark embedding as tapu (restricted access)
        realm_id: Realm this embedding belongs to
        
    Returns:
        EmbeddingResult with embedding vector and tapu status
    """
    if MOCK_AI:
        logger.info("Mock mode: generating deterministic embedding")
        return EmbeddingResult(
            embedding=_generate_mock_embedding(text),
            tapu=tapu,
            realm_id=realm_id
        )
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{TEPO_URL}/awa/vector/embed",
                headers=_get_headers(),
                json={
                    "text": text, 
                    "model": model,
                    "tapu": tapu,
                    "realm_id": realm_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return EmbeddingResult(
                embedding=data.get("embedding", []),
                tapu=data.get("tapu", tapu),
                realm_id=data.get("realm_id", realm_id)
            )
    except httpx.HTTPError as e:
        logger.error(f"Te Pō embed request failed: {e}")
        if MOCK_AI:
            return EmbeddingResult(
                embedding=_generate_mock_embedding(text),
                tapu=tapu,
                realm_id=realm_id
            )
        raise RuntimeError(f"Failed to get embedding from Te Pō: {e}")


async def complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    Get completion from Te Pō.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        model: Model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        
    Returns:
        Completion text
    """
    if MOCK_AI:
        logger.info("Mock mode: generating mock completion")
        return _generate_mock_completion(prompt)
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TEPO_URL}/awa/chat",
                headers=_get_headers(),
                json={
                    "messages": messages,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", data.get("message", ""))
    except httpx.HTTPError as e:
        logger.error(f"Te Pō chat request failed: {e}")
        if MOCK_AI:
            return _generate_mock_completion(prompt)
        raise RuntimeError(f"Failed to get completion from Te Pō: {e}")


async def chat_completion(
    messages: list[dict],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    Get chat completion from Te Pō with full message history.
    
    Args:
        messages: List of message dicts with role/content
        model: Model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        
    Returns:
        Assistant response text
    """
    if MOCK_AI:
        logger.info("Mock mode: generating mock completion")
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return _generate_mock_completion(last_user)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TEPO_URL}/awa/chat",
                headers=_get_headers(),
                json={
                    "messages": messages,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", data.get("message", ""))
    except httpx.HTTPError as e:
        logger.error(f"Te Pō chat request failed: {e}")
        if MOCK_AI:
            last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            return _generate_mock_completion(last_user)
        raise RuntimeError(f"Failed to get chat completion from Te Pō: {e}")


async def invoke_kaitiaki(
    kaitiaki_id: str,
    action: str,
    payload: dict,
    context: Optional[dict] = None
) -> dict:
    """
    Invoke a kaitiaki action via Te Pō.
    
    Args:
        kaitiaki_id: ID of the kaitiaki
        action: Action to perform
        payload: Action payload
        context: Optional context dict
        
    Returns:
        Kaitiaki response
    """
    if MOCK_AI:
        logger.info(f"Mock mode: simulating kaitiaki {kaitiaki_id} action {action}")
        return {
            "status": "mock",
            "kaitiaki_id": kaitiaki_id,
            "action": action,
            "message": "Mock kaitiaki response"
        }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TEPO_URL}/awa/kaitiaki/invoke",
                headers=_get_headers(),
                json={
                    "kaitiaki_id": kaitiaki_id,
                    "action": action,
                    "payload": payload,
                    "context": context or {}
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Te Pō kaitiaki invoke failed: {e}")
        raise RuntimeError(f"Failed to invoke kaitiaki via Te Pō: {e}")


async def vector_search(
    query: str,
    collection: str = "default",
    limit: int = 5,
    threshold: float = 0.7,
    requestor_realm: Optional[str] = None,
    include_tapu: bool = False
) -> list[dict]:
    """
    Search vectors via Te Pō.
    
    Args:
        query: Search query text
        collection: Vector collection name
        limit: Max results
        threshold: Similarity threshold
        requestor_realm: Realm making the request (for tapu access check)
        include_tapu: Include tapu results (requires same realm access)
        
    Returns:
        List of matching documents (tapu filtered unless include_tapu=True)
        
    Raises:
        TapuAccessError: If accessing tapu content without permission
    """
    if MOCK_AI:
        logger.info("Mock mode: returning empty search results")
        return []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{TEPO_URL}/awa/vector/search",
                headers=_get_headers(),
                json={
                    "query": query,
                    "collection": collection,
                    "limit": limit,
                    "threshold": threshold,
                    "requestor_realm": requestor_realm,
                    "include_tapu": include_tapu
                }
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            
            # Filter tapu results on client side if Te Pō didn't
            if not include_tapu:
                results = [r for r in results if not r.get("tapu", False)]
            elif include_tapu:
                # Verify access to tapu results
                for r in results:
                    if r.get("tapu", False):
                        result_realm = r.get("realm_id")
                        if result_realm and result_realm != requestor_realm:
                            raise TapuAccessError(
                                f"Cannot access tapu content from realm {result_realm}"
                            )
            
            return results
    except httpx.HTTPError as e:
        logger.error(f"Te Pō vector search failed: {e}")
        return []
    except httpx.HTTPError as e:
        logger.error(f"Te Pō vector search failed: {e}")
        return []


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    preserve_paragraphs: bool = True
) -> list[str]:
    """
    Split text into chunks for embedding.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks
        preserve_paragraphs: Try to break at paragraph boundaries
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    
    if preserve_paragraphs:
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Handle paragraphs larger than chunk_size
                if len(para) > chunk_size:
                    # Split long paragraph
                    words = para.split()
                    current_chunk = ""
                    for word in words:
                        if len(current_chunk) + len(word) + 1 <= chunk_size:
                            current_chunk = current_chunk + " " + word if current_chunk else word
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = word
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
    else:
        # Simple character-based chunking with overlap
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap if end < len(text) else end
    
    return chunks


# Convenience aliases
get_embedding = embed_text_sync
generate = complete


# Backward compatibility: get raw embedding list
def get_embedding_vector(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Get raw embedding vector (backward compatible).
    Use embed_text_sync for full EmbeddingResult with tapu support.
    """
    result = embed_text_sync(text, model)
    return result.embedding


# Export types
__all__ = [
    # Core functions
    "embed_text",
    "embed_text_sync",
    "complete",
    "chat_completion",
    "invoke_kaitiaki",
    "vector_search",
    "chunk_text",
    # Types
    "EmbeddingResult",
    "TapuAccessError",
    # Aliases
    "get_embedding",
    "get_embedding_vector",
    "generate",
]
