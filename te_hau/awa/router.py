"""
Awa Router

Message routing between realms.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import asyncio
import json
import hashlib
import uuid


class MessageType(Enum):
    """Types of inter-realm messages."""
    
    # Memory protocol
    MEMORY_QUERY = "memory.query"
    MEMORY_RESULT = "memory.result"
    MEMORY_SHARE = "memory.share"
    MEMORY_ACK = "memory.ack"
    
    # Kaitiaki protocol
    KAITIAKI_REQUEST = "kaitiaki.request"
    KAITIAKI_RESPONSE = "kaitiaki.response"
    KAITIAKI_BROADCAST = "kaitiaki.broadcast"
    
    # Pipeline protocol
    PIPELINE_TRIGGER = "pipeline.trigger"
    PIPELINE_RESULT = "pipeline.result"
    PIPELINE_CHAIN = "pipeline.chain"
    
    # System
    HEARTBEAT = "system.heartbeat"
    REGISTER = "system.register"
    UNREGISTER = "system.unregister"
    ERROR = "system.error"


@dataclass
class MessageSource:
    """Source of a message."""
    realm: str
    kaitiaki: Optional[str] = None
    component: Optional[str] = None


@dataclass
class MessageTarget:
    """Target of a message."""
    realm: str
    kaitiaki: Optional[str] = None
    component: Optional[str] = None


@dataclass
class Message:
    """Inter-realm message."""
    
    id: str
    timestamp: datetime
    source: MessageSource
    target: MessageTarget
    type: MessageType
    payload: Dict[str, Any]
    auth: Optional[Dict[str, str]] = None
    reply_to: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        source_realm: str,
        target_realm: str,
        msg_type: MessageType,
        payload: Dict[str, Any],
        source_kaitiaki: str = None,
        target_kaitiaki: str = None,
        reply_to: str = None
    ) -> 'Message':
        """Create a new message."""
        return cls(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            source=MessageSource(source_realm, source_kaitiaki),
            target=MessageTarget(target_realm, target_kaitiaki),
            type=msg_type,
            payload=payload,
            reply_to=reply_to
        )
    
    def sign(self, bearer_key: str):
        """Sign the message with bearer key."""
        content = json.dumps({
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.realm,
            'target': self.target.realm,
            'type': self.type.value,
            'payload': self.payload
        }, sort_keys=True)
        
        signature = hashlib.sha256(
            (content + bearer_key).encode()
        ).hexdigest()
        
        self.auth = {
            'bearer_hash': hashlib.sha256(bearer_key.encode()).hexdigest()[:16],
            'signature': signature
        }
    
    def verify(self, bearer_key: str) -> bool:
        """Verify message signature."""
        if not self.auth:
            return False
        
        expected_hash = hashlib.sha256(bearer_key.encode()).hexdigest()[:16]
        if self.auth.get('bearer_hash') != expected_hash:
            return False
        
        content = json.dumps({
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.realm,
            'target': self.target.realm,
            'type': self.type.value,
            'payload': self.payload
        }, sort_keys=True)
        
        expected_sig = hashlib.sha256(
            (content + bearer_key).encode()
        ).hexdigest()
        
        return self.auth.get('signature') == expected_sig
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'source': {
                'realm': self.source.realm,
                'kaitiaki': self.source.kaitiaki,
                'component': self.source.component
            },
            'target': {
                'realm': self.target.realm,
                'kaitiaki': self.target.kaitiaki,
                'component': self.target.component
            },
            'type': self.type.value,
            'payload': self.payload,
            'auth': self.auth,
            'reply_to': self.reply_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=MessageSource(
                realm=data['source']['realm'],
                kaitiaki=data['source'].get('kaitiaki'),
                component=data['source'].get('component')
            ),
            target=MessageTarget(
                realm=data['target']['realm'],
                kaitiaki=data['target'].get('kaitiaki'),
                component=data['target'].get('component')
            ),
            type=MessageType(data['type']),
            payload=data.get('payload', {}),
            auth=data.get('auth'),
            reply_to=data.get('reply_to')
        )


MessageHandler = Callable[[Message], Any]


class Router:
    """
    Routes messages between realms.
    
    Handles message delivery, queuing, and handler dispatch.
    """
    
    def __init__(self, realm_name: str, bearer_key: str = None):
        self.realm_name = realm_name
        self.bearer_key = bearer_key
        self.handlers: Dict[MessageType, List[MessageHandler]] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.connected_realms: Dict[str, 'Router'] = {}  # For local routing
        self._running = False
    
    def on(self, msg_type: MessageType, handler: MessageHandler):
        """Register a handler for a message type."""
        if msg_type not in self.handlers:
            self.handlers[msg_type] = []
        self.handlers[msg_type].append(handler)
    
    def off(self, msg_type: MessageType, handler: MessageHandler = None):
        """Unregister a handler."""
        if msg_type in self.handlers:
            if handler:
                self.handlers[msg_type].remove(handler)
            else:
                del self.handlers[msg_type]
    
    async def send(self, message: Message, wait_response: bool = False) -> Optional[Message]:
        """
        Send a message to another realm.
        
        Args:
            message: The message to send
            wait_response: Whether to wait for a response
            
        Returns:
            Response message if wait_response is True
        """
        # Sign message if we have a bearer key
        if self.bearer_key:
            message.sign(self.bearer_key)
        
        # Check if target is locally connected
        target_router = self.connected_realms.get(message.target.realm)
        
        if target_router:
            # Local delivery
            if wait_response:
                future = asyncio.get_event_loop().create_future()
                self.pending_responses[message.id] = future
                
                await target_router.receive(message)
                
                try:
                    return await asyncio.wait_for(future, timeout=30.0)
                except asyncio.TimeoutError:
                    del self.pending_responses[message.id]
                    raise TimeoutError(f"No response to message {message.id}")
            else:
                await target_router.receive(message)
        else:
            # Remote delivery would go here (Redis, Kafka, etc.)
            raise NotImplementedError("Remote routing requires an adapter")
        
        return None
    
    async def receive(self, message: Message):
        """
        Receive and process a message.
        
        Args:
            message: The received message
        """
        # Check if this is a response to a pending request
        if message.reply_to and message.reply_to in self.pending_responses:
            future = self.pending_responses.pop(message.reply_to)
            future.set_result(message)
            return
        
        # Dispatch to handlers
        handlers = self.handlers.get(message.type, [])
        
        for handler in handlers:
            try:
                result = handler(message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                # Send error response
                error_msg = Message.create(
                    source_realm=self.realm_name,
                    target_realm=message.source.realm,
                    msg_type=MessageType.ERROR,
                    payload={'error': str(e), 'original_id': message.id},
                    reply_to=message.id
                )
                await self._route_back(error_msg)
    
    async def _route_back(self, message: Message):
        """Route a message back to its source."""
        target_router = self.connected_realms.get(message.target.realm)
        if target_router:
            await target_router.receive(message)
    
    def connect(self, other_router: 'Router'):
        """Connect to another router (local/in-memory connection)."""
        self.connected_realms[other_router.realm_name] = other_router
        other_router.connected_realms[self.realm_name] = self
    
    def disconnect(self, realm_name: str):
        """Disconnect from another router."""
        if realm_name in self.connected_realms:
            other_router = self.connected_realms.pop(realm_name)
            if self.realm_name in other_router.connected_realms:
                del other_router.connected_realms[self.realm_name]
    
    # Convenience methods for common message types
    
    async def query_memory(
        self,
        target_realm: str,
        query: str,
        top_k: int = 5
    ) -> Optional[List[Dict]]:
        """Query another realm's memory."""
        message = Message.create(
            source_realm=self.realm_name,
            target_realm=target_realm,
            msg_type=MessageType.MEMORY_QUERY,
            payload={'query': query, 'top_k': top_k}
        )
        
        response = await self.send(message, wait_response=True)
        if response:
            return response.payload.get('results', [])
        return None
    
    async def request_kaitiaki(
        self,
        target_realm: str,
        kaitiaki: str,
        task: str,
        payload: Dict[str, Any]
    ) -> Optional[Dict]:
        """Request assistance from another realm's kaitiaki."""
        message = Message.create(
            source_realm=self.realm_name,
            target_realm=target_realm,
            msg_type=MessageType.KAITIAKI_REQUEST,
            payload={'task': task, 'data': payload},
            target_kaitiaki=kaitiaki
        )
        
        response = await self.send(message, wait_response=True)
        if response:
            return response.payload
        return None
    
    async def trigger_pipeline(
        self,
        target_realm: str,
        pipeline: str,
        input_data: Any
    ) -> Optional[Any]:
        """Trigger a pipeline in another realm."""
        message = Message.create(
            source_realm=self.realm_name,
            target_realm=target_realm,
            msg_type=MessageType.PIPELINE_TRIGGER,
            payload={'pipeline': pipeline, 'input': input_data}
        )
        
        response = await self.send(message, wait_response=True)
        if response:
            return response.payload.get('output')
        return None
    
    async def broadcast(
        self,
        event: str,
        payload: Dict[str, Any]
    ):
        """Broadcast to all connected realms."""
        for realm_name in self.connected_realms:
            message = Message.create(
                source_realm=self.realm_name,
                target_realm=realm_name,
                msg_type=MessageType.KAITIAKI_BROADCAST,
                payload={'event': event, 'data': payload}
            )
            await self.send(message)


# Global router instance
_router: Optional[Router] = None


def get_router(realm_name: str = None, bearer_key: str = None) -> Router:
    """Get or create the global router."""
    global _router
    
    if _router is None:
        if not realm_name:
            raise ValueError("realm_name required for first router initialization")
        _router = Router(realm_name, bearer_key)
    
    return _router
