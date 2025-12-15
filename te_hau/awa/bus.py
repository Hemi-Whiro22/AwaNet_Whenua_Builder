"""
Awa Event Bus

Publish/subscribe event system for realms.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
import asyncio
import uuid


@dataclass
class Event:
    """An event in the system."""
    
    id: str
    name: str
    source_realm: str
    timestamp: datetime
    payload: Dict[str, Any]
    tags: Set[str] = field(default_factory=set)
    
    @classmethod
    def create(
        cls,
        name: str,
        source_realm: str,
        payload: Dict[str, Any],
        tags: Set[str] = None
    ) -> 'Event':
        """Create a new event."""
        return cls(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            name=name,
            source_realm=source_realm,
            timestamp=datetime.utcnow(),
            payload=payload,
            tags=tags or set()
        )
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'source_realm': self.source_realm,
            'timestamp': self.timestamp.isoformat(),
            'payload': self.payload,
            'tags': list(self.tags)
        }


EventHandler = Callable[[Event], Any]


@dataclass
class Subscription:
    """A subscription to events."""
    
    id: str
    pattern: str  # Event name pattern (supports wildcards)
    handler: EventHandler
    realm: Optional[str] = None  # Filter by source realm
    tags: Set[str] = field(default_factory=set)  # Filter by tags
    
    def matches(self, event: Event) -> bool:
        """Check if this subscription matches an event."""
        # Check realm filter
        if self.realm and event.source_realm != self.realm:
            return False
        
        # Check tag filter
        if self.tags and not self.tags.intersection(event.tags):
            return False
        
        # Check name pattern
        return self._match_pattern(event.name, self.pattern)
    
    def _match_pattern(self, name: str, pattern: str) -> bool:
        """Match event name against pattern (supports * wildcards)."""
        if pattern == '*':
            return True
        
        if '*' not in pattern:
            return name == pattern
        
        # Simple wildcard matching
        parts = pattern.split('*')
        if len(parts) == 2:
            prefix, suffix = parts
            return name.startswith(prefix) and name.endswith(suffix)
        
        # More complex patterns
        import fnmatch
        return fnmatch.fnmatch(name, pattern)


class EventBus:
    """
    Publish/subscribe event bus for inter-realm communication.
    
    Supports:
    - Pattern-based subscriptions
    - Tag filtering
    - Realm filtering
    - Async handlers
    """
    
    def __init__(self, realm_name: str):
        self.realm_name = realm_name
        self.subscriptions: Dict[str, Subscription] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        self._connected_buses: Dict[str, 'EventBus'] = {}
    
    def subscribe(
        self,
        pattern: str,
        handler: EventHandler,
        realm: str = None,
        tags: Set[str] = None
    ) -> str:
        """
        Subscribe to events matching a pattern.
        
        Args:
            pattern: Event name pattern (supports * wildcards)
            handler: Function to call when event matches
            realm: Only match events from this realm
            tags: Only match events with these tags
            
        Returns:
            Subscription ID
        """
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        
        self.subscriptions[sub_id] = Subscription(
            id=sub_id,
            pattern=pattern,
            handler=handler,
            realm=realm,
            tags=tags or set()
        )
        
        return sub_id
    
    def unsubscribe(self, subscription_id: str):
        """Unsubscribe from events."""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
    
    async def publish(
        self,
        name: str,
        payload: Dict[str, Any],
        tags: Set[str] = None,
        propagate: bool = True
    ) -> Event:
        """
        Publish an event.
        
        Args:
            name: Event name
            payload: Event data
            tags: Optional tags for filtering
            propagate: Whether to send to connected buses
            
        Returns:
            The published event
        """
        event = Event.create(
            name=name,
            source_realm=self.realm_name,
            payload=payload,
            tags=tags
        )
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Dispatch to local subscribers
        await self._dispatch(event)
        
        # Propagate to connected buses
        if propagate:
            for bus in self._connected_buses.values():
                await bus._receive(event)
        
        return event
    
    async def _dispatch(self, event: Event):
        """Dispatch event to matching subscribers."""
        for sub in self.subscriptions.values():
            if sub.matches(event):
                try:
                    result = sub.handler(event)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Handler error for {event.name}: {e}")
    
    async def _receive(self, event: Event):
        """Receive an event from another bus."""
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Dispatch locally
        await self._dispatch(event)
    
    def connect(self, other_bus: 'EventBus'):
        """Connect to another event bus."""
        self._connected_buses[other_bus.realm_name] = other_bus
        other_bus._connected_buses[self.realm_name] = self
    
    def disconnect(self, realm_name: str):
        """Disconnect from another event bus."""
        if realm_name in self._connected_buses:
            other_bus = self._connected_buses.pop(realm_name)
            if self.realm_name in other_bus._connected_buses:
                del other_bus._connected_buses[self.realm_name]
    
    def get_history(
        self,
        pattern: str = '*',
        realm: str = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get event history.
        
        Args:
            pattern: Event name pattern to filter
            realm: Source realm to filter
            limit: Maximum events to return
            
        Returns:
            List of matching events
        """
        sub = Subscription(
            id='query',
            pattern=pattern,
            handler=lambda e: None,
            realm=realm
        )
        
        matching = [e for e in self.event_history if sub.matches(e)]
        return matching[-limit:]


# Common event names
class Events:
    """Standard event names."""
    
    # Realm events
    REALM_CREATED = "realm.created"
    REALM_UPDATED = "realm.updated"
    REALM_SEALED = "realm.sealed"
    REALM_DEPLOYED = "realm.deployed"
    
    # Kaitiaki events
    KAITIAKI_INVOKED = "kaitiaki.invoked"
    KAITIAKI_COMPLETED = "kaitiaki.completed"
    KAITIAKI_ERROR = "kaitiaki.error"
    
    # Pipeline events
    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_STAGE_COMPLETED = "pipeline.stage.completed"
    PIPELINE_COMPLETED = "pipeline.completed"
    PIPELINE_ERROR = "pipeline.error"
    
    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_QUERIED = "memory.queried"
    MEMORY_SHARED = "memory.shared"


# Global bus instance
_bus: Optional[EventBus] = None


def get_event_bus(realm_name: str = None) -> EventBus:
    """Get or create the global event bus."""
    global _bus
    
    if _bus is None:
        if not realm_name:
            raise ValueError("realm_name required for first bus initialization")
        _bus = EventBus(realm_name)
    
    return _bus
