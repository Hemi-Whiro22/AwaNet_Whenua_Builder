"""
Awa Whakapapa Graph

Manages realm lineage and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import json


@dataclass
class RealmNode:
    """A realm in the whakapapa graph."""
    
    realm_id: str
    realm_name: str
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    glyph_color: str = "#888888"
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'realm_id': self.realm_id,
            'realm_name': self.realm_name,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'glyph_color': self.glyph_color,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RealmNode':
        return cls(
            realm_id=data['realm_id'],
            realm_name=data['realm_name'],
            parent_id=data.get('parent_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            glyph_color=data.get('glyph_color', '#888888'),
            metadata=data.get('metadata', {})
        )


@dataclass
class RealmLink:
    """A link between realms (beyond parent-child)."""
    
    source_id: str
    target_id: str
    link_type: str  # 'fork', 'merge', 'reference', 'trust'
    created_at: datetime = field(default_factory=datetime.utcnow)
    permissions: Set[str] = field(default_factory=set)
    bidirectional: bool = False
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'link_type': self.link_type,
            'created_at': self.created_at.isoformat(),
            'permissions': list(self.permissions),
            'bidirectional': self.bidirectional,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RealmLink':
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            link_type=data['link_type'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            permissions=set(data.get('permissions', [])),
            bidirectional=data.get('bidirectional', False),
            metadata=data.get('metadata', {})
        )


class WhakapapaGraph:
    """
    Manages realm lineage and relationships.
    
    Implements:
    - Parent-child relationships (inheritance)
    - Sibling relationships (same parent)
    - Arbitrary links (forks, merges, references)
    - Access control based on lineage
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".awaos" / "whakapapa.json"
        self.nodes: Dict[str, RealmNode] = {}
        self.links: List[RealmLink] = []
        self._load()
    
    def _load(self):
        """Load graph from storage."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                data = json.load(f)
            
            for node_data in data.get('nodes', []):
                node = RealmNode.from_dict(node_data)
                self.nodes[node.realm_id] = node
            
            for link_data in data.get('links', []):
                self.links.append(RealmLink.from_dict(link_data))
    
    def save(self):
        """Save graph to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'nodes': [n.to_dict() for n in self.nodes.values()],
            'links': [l.to_dict() for l in self.links]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_realm(
        self,
        realm_id: str,
        realm_name: str,
        parent_id: str = None,
        glyph_color: str = "#888888",
        metadata: Dict = None
    ) -> RealmNode:
        """
        Register a realm in the graph.
        
        Args:
            realm_id: Unique identifier
            realm_name: Human-readable name
            parent_id: Parent realm (if any)
            glyph_color: Glyph color
            metadata: Additional data
            
        Returns:
            The created node
        """
        if realm_id in self.nodes:
            raise ValueError(f"Realm {realm_id} already exists")
        
        if parent_id and parent_id not in self.nodes:
            raise ValueError(f"Parent realm {parent_id} not found")
        
        node = RealmNode(
            realm_id=realm_id,
            realm_name=realm_name,
            parent_id=parent_id,
            glyph_color=glyph_color,
            metadata=metadata or {}
        )
        
        self.nodes[realm_id] = node
        self.save()
        
        return node
    
    def remove_realm(self, realm_id: str):
        """Remove a realm from the graph."""
        if realm_id not in self.nodes:
            return
        
        # Check for children
        children = self.get_children(realm_id)
        if children:
            raise ValueError(f"Cannot remove realm with children: {children}")
        
        del self.nodes[realm_id]
        
        # Remove associated links
        self.links = [l for l in self.links 
                     if l.source_id != realm_id and l.target_id != realm_id]
        
        self.save()
    
    def add_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        permissions: Set[str] = None,
        bidirectional: bool = False,
        metadata: Dict = None
    ) -> RealmLink:
        """
        Add a link between realms.
        
        Args:
            source_id: Source realm
            target_id: Target realm
            link_type: Type of link (fork, merge, reference, trust)
            permissions: Permissions granted by link
            bidirectional: Whether link works both ways
            metadata: Additional data
            
        Returns:
            The created link
        """
        if source_id not in self.nodes:
            raise ValueError(f"Source realm {source_id} not found")
        if target_id not in self.nodes:
            raise ValueError(f"Target realm {target_id} not found")
        
        link = RealmLink(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            permissions=permissions or set(),
            bidirectional=bidirectional,
            metadata=metadata or {}
        )
        
        self.links.append(link)
        self.save()
        
        return link
    
    def remove_link(self, source_id: str, target_id: str, link_type: str = None):
        """Remove a link between realms."""
        self.links = [
            l for l in self.links
            if not (l.source_id == source_id and 
                   l.target_id == target_id and
                   (link_type is None or l.link_type == link_type))
        ]
        self.save()
    
    def get_parent(self, realm_id: str) -> Optional[RealmNode]:
        """Get parent realm."""
        if realm_id not in self.nodes:
            return None
        
        node = self.nodes[realm_id]
        if node.parent_id and node.parent_id in self.nodes:
            return self.nodes[node.parent_id]
        
        return None
    
    def get_children(self, realm_id: str) -> List[RealmNode]:
        """Get direct children of a realm."""
        return [n for n in self.nodes.values() if n.parent_id == realm_id]
    
    def get_ancestors(self, realm_id: str) -> List[RealmNode]:
        """Get all ancestors (parent chain) of a realm."""
        ancestors = []
        current_id = realm_id
        
        while current_id and current_id in self.nodes:
            parent_id = self.nodes[current_id].parent_id
            if parent_id and parent_id in self.nodes:
                ancestors.append(self.nodes[parent_id])
                current_id = parent_id
            else:
                break
        
        return ancestors
    
    def get_descendants(self, realm_id: str) -> List[RealmNode]:
        """Get all descendants of a realm."""
        descendants = []
        queue = [realm_id]
        
        while queue:
            current_id = queue.pop(0)
            children = self.get_children(current_id)
            descendants.extend(children)
            queue.extend([c.realm_id for c in children])
        
        return descendants
    
    def get_siblings(self, realm_id: str) -> List[RealmNode]:
        """Get siblings (same parent) of a realm."""
        if realm_id not in self.nodes:
            return []
        
        parent_id = self.nodes[realm_id].parent_id
        if not parent_id:
            return []
        
        return [n for n in self.nodes.values() 
                if n.parent_id == parent_id and n.realm_id != realm_id]
    
    def get_linked(self, realm_id: str, link_type: str = None) -> List[RealmNode]:
        """Get realms linked to this one."""
        linked = []
        
        for link in self.links:
            if link.source_id == realm_id:
                if link_type is None or link.link_type == link_type:
                    if link.target_id in self.nodes:
                        linked.append(self.nodes[link.target_id])
            elif link.bidirectional and link.target_id == realm_id:
                if link_type is None or link.link_type == link_type:
                    if link.source_id in self.nodes:
                        linked.append(self.nodes[link.source_id])
        
        return linked
    
    def can_access(
        self,
        source_id: str,
        target_id: str,
        required_permission: str = None
    ) -> bool:
        """
        Check if source can access target based on lineage.
        
        Access rules:
        1. A realm can always access itself
        2. A parent can access children
        3. Linked realms can access based on link permissions
        4. Ancestors can access descendants
        """
        if source_id == target_id:
            return True
        
        if source_id not in self.nodes or target_id not in self.nodes:
            return False
        
        # Check if target is descendant
        descendants = self.get_descendants(source_id)
        if any(d.realm_id == target_id for d in descendants):
            return True
        
        # Check links
        for link in self.links:
            # Direct link
            if link.source_id == source_id and link.target_id == target_id:
                if required_permission:
                    return required_permission in link.permissions or '*' in link.permissions
                return True
            
            # Bidirectional link
            if link.bidirectional and link.target_id == source_id and link.source_id == target_id:
                if required_permission:
                    return required_permission in link.permissions or '*' in link.permissions
                return True
        
        return False
    
    def get_tree(self, root_id: str = None) -> Dict:
        """
        Get the graph as a tree structure.
        
        Args:
            root_id: Start from this node (None for all roots)
            
        Returns:
            Tree structure
        """
        def build_tree(node_id: str) -> Dict:
            node = self.nodes[node_id]
            children = self.get_children(node_id)
            
            return {
                'id': node.realm_id,
                'name': node.realm_name,
                'glyph': node.glyph_color,
                'created_at': node.created_at.isoformat(),
                'children': [build_tree(c.realm_id) for c in children]
            }
        
        if root_id:
            return build_tree(root_id)
        
        # Find all roots (nodes without parents)
        roots = [n for n in self.nodes.values() if not n.parent_id]
        
        return {
            'roots': [build_tree(r.realm_id) for r in roots]
        }
    
    def visualize(self) -> str:
        """Generate ASCII visualization of the graph."""
        lines = []
        
        def draw_node(node_id: str, prefix: str = "", is_last: bool = True):
            node = self.nodes[node_id]
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node.realm_name} ({node.glyph_color})")
            
            children = self.get_children(node_id)
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            for i, child in enumerate(children):
                draw_node(child.realm_id, child_prefix, i == len(children) - 1)
        
        # Find roots
        roots = [n for n in self.nodes.values() if not n.parent_id]
        
        for i, root in enumerate(roots):
            lines.append(f"🌱 {root.realm_name} ({root.glyph_color})")
            children = self.get_children(root.realm_id)
            for j, child in enumerate(children):
                draw_node(child.realm_id, "", j == len(children) - 1)
            
            if i < len(roots) - 1:
                lines.append("")
        
        return "\n".join(lines)


# Global instance
_graph: Optional[WhakapapaGraph] = None


def get_whakapapa_graph() -> WhakapapaGraph:
    """Get the global whakapapa graph."""
    global _graph
    
    if _graph is None:
        _graph = WhakapapaGraph()
    
    return _graph
