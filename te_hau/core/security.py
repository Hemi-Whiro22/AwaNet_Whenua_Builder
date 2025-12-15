"""
Te Hau Security Module

Implements tapu (sacred/restricted) and mana (authority) based security.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime
import json
from pathlib import Path


class TapuLevel(Enum):
    """
    Tapu levels for resources and operations.
    
    NOA = unrestricted, everyday
    AHI = restricted, requires basic auth
    TAPU = sacred, requires elevated permissions
    WHAKAHAERE = administrative, system-level
    """
    NOA = 0          # Unrestricted
    AHI = 1          # Basic restriction (fire/energy)
    TAPU = 2         # Sacred/restricted
    WHAKAHAERE = 3   # Administrative/system


class ManaType(Enum):
    """
    Types of mana (authority/permission).
    
    WHENUA = land/realm authority
    TANGATA = person/user authority
    ATUA = system/divine authority
    """
    WHENUA = "whenua"   # Realm-based authority
    TANGATA = "tangata"  # User-based authority
    ATUA = "atua"        # System authority


@dataclass
class ManaGrant:
    """A grant of mana (authority) to an entity."""
    
    entity_id: str           # Who has the mana
    mana_type: ManaType      # Type of mana
    realm: Optional[str]     # Realm scope (None = global)
    permissions: Set[str]    # Specific permissions
    granted_at: datetime = field(default_factory=datetime.utcnow)
    granted_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if grant is still valid."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def has_permission(self, permission: str) -> bool:
        """Check if grant includes permission."""
        if '*' in self.permissions:
            return True
        return permission in self.permissions
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'mana_type': self.mana_type.value,
            'realm': self.realm,
            'permissions': list(self.permissions),
            'granted_at': self.granted_at.isoformat(),
            'granted_by': self.granted_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ManaGrant':
        """Create from dictionary."""
        return cls(
            entity_id=data['entity_id'],
            mana_type=ManaType(data['mana_type']),
            realm=data.get('realm'),
            permissions=set(data.get('permissions', [])),
            granted_at=datetime.fromisoformat(data['granted_at']),
            granted_by=data.get('granted_by'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )


@dataclass
class TapuDeclaration:
    """A tapu declaration on a resource or operation."""
    
    resource_path: str           # Path or identifier
    tapu_level: TapuLevel        # Required tapu level
    required_permissions: Set[str] = field(default_factory=set)
    reason: Optional[str] = None
    declared_by: Optional[str] = None
    declared_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'resource_path': self.resource_path,
            'tapu_level': self.tapu_level.value,
            'required_permissions': list(self.required_permissions),
            'reason': self.reason,
            'declared_by': self.declared_by,
            'declared_at': self.declared_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TapuDeclaration':
        """Create from dictionary."""
        return cls(
            resource_path=data['resource_path'],
            tapu_level=TapuLevel(data['tapu_level']),
            required_permissions=set(data.get('required_permissions', [])),
            reason=data.get('reason'),
            declared_by=data.get('declared_by'),
            declared_at=datetime.fromisoformat(data['declared_at'])
        )


class SecurityContext:
    """
    Security context for a session or request.
    
    Tracks the mana (authority) available to perform operations.
    """
    
    def __init__(self, entity_id: str, realm: Optional[str] = None):
        self.entity_id = entity_id
        self.realm = realm
        self.mana_grants: List[ManaGrant] = []
        self.elevated = False
    
    def add_mana(self, grant: ManaGrant):
        """Add a mana grant to the context."""
        self.mana_grants.append(grant)
    
    def has_mana(self, mana_type: ManaType, permission: str = None) -> bool:
        """Check if context has specific mana."""
        for grant in self.mana_grants:
            if not grant.is_valid():
                continue
            
            if grant.mana_type != mana_type:
                continue
            
            # Check realm scope
            if grant.realm and grant.realm != self.realm:
                continue
            
            # Check permission if specified
            if permission and not grant.has_permission(permission):
                continue
            
            return True
        
        return False
    
    def can_access(self, tapu: TapuDeclaration) -> bool:
        """Check if context can access a tapu resource."""
        # NOA is always accessible
        if tapu.tapu_level == TapuLevel.NOA:
            return True
        
        # Check required permissions
        for permission in tapu.required_permissions:
            has_permission = False
            for grant in self.mana_grants:
                if grant.is_valid() and grant.has_permission(permission):
                    has_permission = True
                    break
            if not has_permission:
                return False
        
        # Check tapu level against mana
        if tapu.tapu_level == TapuLevel.AHI:
            return self.has_mana(ManaType.TANGATA) or self.has_mana(ManaType.WHENUA)
        
        if tapu.tapu_level == TapuLevel.TAPU:
            return self.has_mana(ManaType.WHENUA) or self.has_mana(ManaType.ATUA)
        
        if tapu.tapu_level == TapuLevel.WHAKAHAERE:
            return self.has_mana(ManaType.ATUA)
        
        return False
    
    def elevate(self):
        """Elevate the security context (sudo equivalent)."""
        self.elevated = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'realm': self.realm,
            'mana_grants': [g.to_dict() for g in self.mana_grants],
            'elevated': self.elevated
        }


class SecurityManager:
    """
    Manages security for a realm.
    
    Handles mana grants and tapu declarations.
    """
    
    def __init__(self, realm_path: Optional[Path] = None):
        self.realm_path = realm_path
        self.mana_grants: Dict[str, List[ManaGrant]] = {}
        self.tapu_declarations: Dict[str, TapuDeclaration] = {}
        
        if realm_path:
            self._load()
    
    def _load(self):
        """Load security data from realm."""
        security_file = self.realm_path / "mauri" / "security.json"
        
        if security_file.exists():
            with open(security_file) as f:
                data = json.load(f)
            
            for entity_id, grants in data.get('mana_grants', {}).items():
                self.mana_grants[entity_id] = [
                    ManaGrant.from_dict(g) for g in grants
                ]
            
            for path, decl in data.get('tapu_declarations', {}).items():
                self.tapu_declarations[path] = TapuDeclaration.from_dict(decl)
    
    def save(self):
        """Save security data to realm."""
        if not self.realm_path:
            return
        
        security_file = self.realm_path / "mauri" / "security.json"
        security_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'mana_grants': {
                entity: [g.to_dict() for g in grants]
                for entity, grants in self.mana_grants.items()
            },
            'tapu_declarations': {
                path: decl.to_dict()
                for path, decl in self.tapu_declarations.items()
            }
        }
        
        with open(security_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def grant_mana(
        self,
        entity_id: str,
        mana_type: ManaType,
        permissions: Set[str],
        realm: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> ManaGrant:
        """Grant mana to an entity."""
        grant = ManaGrant(
            entity_id=entity_id,
            mana_type=mana_type,
            realm=realm,
            permissions=permissions,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        if entity_id not in self.mana_grants:
            self.mana_grants[entity_id] = []
        
        self.mana_grants[entity_id].append(grant)
        self.save()
        
        return grant
    
    def revoke_mana(self, entity_id: str, mana_type: Optional[ManaType] = None):
        """Revoke mana from an entity."""
        if entity_id not in self.mana_grants:
            return
        
        if mana_type:
            self.mana_grants[entity_id] = [
                g for g in self.mana_grants[entity_id]
                if g.mana_type != mana_type
            ]
        else:
            del self.mana_grants[entity_id]
        
        self.save()
    
    def declare_tapu(
        self,
        resource_path: str,
        tapu_level: TapuLevel,
        required_permissions: Optional[Set[str]] = None,
        reason: Optional[str] = None,
        declared_by: Optional[str] = None
    ) -> TapuDeclaration:
        """Declare tapu on a resource."""
        declaration = TapuDeclaration(
            resource_path=resource_path,
            tapu_level=tapu_level,
            required_permissions=required_permissions or set(),
            reason=reason,
            declared_by=declared_by
        )
        
        self.tapu_declarations[resource_path] = declaration
        self.save()
        
        return declaration
    
    def lift_tapu(self, resource_path: str):
        """Lift tapu from a resource."""
        if resource_path in self.tapu_declarations:
            del self.tapu_declarations[resource_path]
            self.save()
    
    def get_tapu(self, resource_path: str) -> Optional[TapuDeclaration]:
        """Get tapu declaration for a resource."""
        # Exact match
        if resource_path in self.tapu_declarations:
            return self.tapu_declarations[resource_path]
        
        # Check parent paths
        path = Path(resource_path)
        for parent in path.parents:
            parent_str = str(parent)
            if parent_str in self.tapu_declarations:
                return self.tapu_declarations[parent_str]
        
        return None
    
    def get_context(self, entity_id: str, realm: Optional[str] = None) -> SecurityContext:
        """Create a security context for an entity."""
        context = SecurityContext(entity_id, realm)
        
        if entity_id in self.mana_grants:
            for grant in self.mana_grants[entity_id]:
                context.add_mana(grant)
        
        return context
    
    def check_access(
        self,
        entity_id: str,
        resource_path: str,
        realm: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if an entity can access a resource.
        
        Returns:
            (allowed, reason)
        """
        tapu = self.get_tapu(resource_path)
        
        if not tapu:
            return True, None
        
        context = self.get_context(entity_id, realm)
        
        if context.can_access(tapu):
            return True, None
        else:
            return False, f"Insufficient mana for tapu level {tapu.tapu_level.name}"


# Default tapu declarations for AwaOS resources
DEFAULT_TAPU = {
    'mauri/seal.json': TapuLevel.TAPU,
    'mauri/den_manifest.json': TapuLevel.TAPU,
    '.env': TapuLevel.WHAKAHAERE,
    'secrets/': TapuLevel.WHAKAHAERE,
    'pipelines/': TapuLevel.AHI,
    'mini_te_po/': TapuLevel.AHI,
}


def apply_default_tapu(manager: SecurityManager):
    """Apply default tapu declarations to a realm."""
    for path, level in DEFAULT_TAPU.items():
        manager.declare_tapu(
            path,
            level,
            reason="Default AwaOS security policy"
        )


def require_mana(mana_type: ManaType, permission: str = None):
    """
    Decorator to require mana for a function.
    
    Usage:
        @require_mana(ManaType.WHENUA, 'deploy')
        def deploy_realm(context, realm):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Look for security context in args
            context = None
            for arg in args:
                if isinstance(arg, SecurityContext):
                    context = arg
                    break
            
            if not context:
                context = kwargs.get('security_context')
            
            if not context:
                raise PermissionError("No security context provided")
            
            if not context.has_mana(mana_type, permission):
                raise PermissionError(
                    f"Insufficient mana: requires {mana_type.value}"
                    f"{f' with {permission}' if permission else ''}"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_tapu(tapu_level: TapuLevel):
    """
    Decorator to require tapu level for a function.
    
    Usage:
        @require_tapu(TapuLevel.TAPU)
        def modify_seal(context, realm):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            context = None
            for arg in args:
                if isinstance(arg, SecurityContext):
                    context = arg
                    break
            
            if not context:
                context = kwargs.get('security_context')
            
            if not context:
                raise PermissionError("No security context provided")
            
            # Create a synthetic tapu declaration
            tapu = TapuDeclaration(
                resource_path=func.__name__,
                tapu_level=tapu_level
            )
            
            if not context.can_access(tapu):
                raise PermissionError(
                    f"Operation requires tapu level: {tapu_level.name}"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# Cross-Realm Access Prevention
# ============================================================================

class CrossRealmAccessError(Exception):
    """Raised when attempting unauthorized cross-realm access."""
    pass


class RealmBoundary:
    """
    Enforces realm boundaries to prevent unauthorized cross-realm access.
    
    Each realm is isolated by default. Cross-realm access requires explicit
    mana grants and can only occur through the awa (channel) system.
    """
    
    def __init__(self, realm_id: str, realm_path: Path):
        self.realm_id = realm_id
        self.realm_path = realm_path
        self.allowed_realms: Set[str] = set()  # Realms we can access
        self.linked_via_awa: Dict[str, str] = {}  # realm_id -> awa_id
    
    def allow_realm(self, target_realm_id: str, awa_id: str):
        """Allow access to another realm via a specific awa."""
        self.allowed_realms.add(target_realm_id)
        self.linked_via_awa[target_realm_id] = awa_id
    
    def revoke_realm(self, target_realm_id: str):
        """Revoke access to another realm."""
        self.allowed_realms.discard(target_realm_id)
        self.linked_via_awa.pop(target_realm_id, None)
    
    def check_access(
        self,
        target_realm_id: str,
        operation: str,
        context: SecurityContext
    ) -> tuple[bool, Optional[str]]:
        """
        Check if access to target realm is allowed.
        
        Returns:
            (allowed, reason)
        """
        # Same realm is always allowed
        if target_realm_id == self.realm_id:
            return True, None
        
        # Check if realm is in allowed list
        if target_realm_id not in self.allowed_realms:
            return False, f"Cross-realm access denied: {target_realm_id} not linked"
        
        # Check if context has cross-realm mana
        if not context.has_mana(ManaType.WHENUA, 'cross_realm'):
            return False, "Insufficient mana for cross-realm access"
        
        return True, None
    
    def enforce(
        self,
        target_realm_id: str,
        operation: str,
        context: SecurityContext
    ):
        """Enforce realm boundary. Raises on violation."""
        allowed, reason = self.check_access(target_realm_id, operation, context)
        if not allowed:
            AuditLog.log(
                event_type='cross_realm_violation',
                realm_id=self.realm_id,
                entity_id=context.entity_id,
                details={
                    'target_realm': target_realm_id,
                    'operation': operation,
                    'reason': reason
                }
            )
            raise CrossRealmAccessError(reason)


# ============================================================================
# Audit Logging
# ============================================================================

@dataclass
class AuditEntry:
    """A single audit log entry."""
    
    timestamp: datetime
    event_type: str
    realm_id: str
    entity_id: Optional[str]
    resource_path: Optional[str]
    action: Optional[str]
    success: bool
    details: Dict
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'realm_id': self.realm_id,
            'entity_id': self.entity_id,
            'resource_path': self.resource_path,
            'action': self.action,
            'success': self.success,
            'details': self.details
        }


class AuditLog:
    """
    Security audit logging system.
    
    Logs all security-relevant events for compliance and debugging.
    """
    
    _instance = None
    _log_path: Optional[Path] = None
    _entries: List[AuditEntry] = []
    _max_memory_entries = 1000
    
    @classmethod
    def configure(cls, log_path: Path):
        """Configure the audit log path."""
        cls._log_path = log_path
        cls._log_path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def log(
        cls,
        event_type: str,
        realm_id: str,
        entity_id: Optional[str] = None,
        resource_path: Optional[str] = None,
        action: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict] = None
    ):
        """Log a security event."""
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            realm_id=realm_id,
            entity_id=entity_id,
            resource_path=resource_path,
            action=action,
            success=success,
            details=details or {}
        )
        
        # Store in memory
        cls._entries.append(entry)
        
        # Trim memory if needed
        if len(cls._entries) > cls._max_memory_entries:
            cls._entries = cls._entries[-cls._max_memory_entries:]
        
        # Write to file if configured
        if cls._log_path:
            cls._write_entry(entry)
    
    @classmethod
    def _write_entry(cls, entry: AuditEntry):
        """Write entry to log file."""
        try:
            with open(cls._log_path, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')
        except Exception:
            pass  # Fail silently for audit logs
    
    @classmethod
    def get_entries(
        cls,
        realm_id: Optional[str] = None,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """Query audit log entries."""
        results = []
        
        for entry in reversed(cls._entries):
            if realm_id and entry.realm_id != realm_id:
                continue
            if event_type and entry.event_type != event_type:
                continue
            if entity_id and entry.entity_id != entity_id:
                continue
            if since and entry.timestamp < since:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    @classmethod
    def log_access(
        cls,
        realm_id: str,
        entity_id: str,
        resource_path: str,
        action: str,
        allowed: bool,
        tapu_level: Optional[TapuLevel] = None
    ):
        """Convenience method to log access attempts."""
        cls.log(
            event_type='access_attempt',
            realm_id=realm_id,
            entity_id=entity_id,
            resource_path=resource_path,
            action=action,
            success=allowed,
            details={
                'tapu_level': tapu_level.name if tapu_level else None
            }
        )
    
    @classmethod
    def log_mana_change(
        cls,
        realm_id: str,
        entity_id: str,
        action: str,  # 'grant' or 'revoke'
        mana_type: ManaType,
        changed_by: Optional[str] = None
    ):
        """Log mana grants and revocations."""
        cls.log(
            event_type='mana_change',
            realm_id=realm_id,
            entity_id=entity_id,
            action=action,
            success=True,
            details={
                'mana_type': mana_type.value,
                'changed_by': changed_by
            }
        )
    
    @classmethod
    def log_tapu_change(
        cls,
        realm_id: str,
        resource_path: str,
        action: str,  # 'declare' or 'lift'
        tapu_level: TapuLevel,
        changed_by: Optional[str] = None
    ):
        """Log tapu declarations and lifts."""
        cls.log(
            event_type='tapu_change',
            realm_id=realm_id,
            resource_path=resource_path,
            action=action,
            success=True,
            details={
                'tapu_level': tapu_level.name,
                'changed_by': changed_by
            }
        )
