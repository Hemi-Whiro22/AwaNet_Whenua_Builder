"""
Te Hau Branching Module

Seeds and branches for realm evolution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import shutil
import hashlib

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.core.renderer import render_template_string


@dataclass
class SeedManifest:
    """Manifest for a seed (template state)."""
    
    seed_name: str
    version: str
    description: str
    files: List[str]
    placeholders: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    dependencies: Dict[str, str] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'seed_name': self.seed_name,
            'version': self.version,
            'description': self.description,
            'files': self.files,
            'placeholders': self.placeholders,
            'created_at': self.created_at.isoformat(),
            'dependencies': self.dependencies,
            'checksum': self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SeedManifest':
        return cls(
            seed_name=data['seed_name'],
            version=data['version'],
            description=data.get('description', ''),
            files=data.get('files', []),
            placeholders=data.get('placeholders', []),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            dependencies=data.get('dependencies', {}),
            checksum=data.get('checksum')
        )


@dataclass  
class BranchManifest:
    """Manifest for a branch (evolved realm)."""
    
    branch_name: str
    parent_seed: str
    realm_name: str
    glyph_at_creation: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    added_capabilities: List[str] = field(default_factory=list)
    env_overrides: Dict[str, str] = field(default_factory=dict)
    toolchain_map: Dict[str, str] = field(default_factory=dict)
    mutations: List[Dict] = field(default_factory=list)
    promoted_to: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'branch_name': self.branch_name,
            'parent_seed': self.parent_seed,
            'realm_name': self.realm_name,
            'glyph_at_creation': self.glyph_at_creation,
            'created_at': self.created_at.isoformat(),
            'added_capabilities': self.added_capabilities,
            'env_overrides': self.env_overrides,
            'toolchain_map': self.toolchain_map,
            'mutations': self.mutations,
            'promoted_to': self.promoted_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BranchManifest':
        return cls(
            branch_name=data['branch_name'],
            parent_seed=data['parent_seed'],
            realm_name=data['realm_name'],
            glyph_at_creation=data.get('glyph_at_creation', '#888888'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            added_capabilities=data.get('added_capabilities', []),
            env_overrides=data.get('env_overrides', {}),
            toolchain_map=data.get('toolchain_map', {}),
            mutations=data.get('mutations', []),
            promoted_to=data.get('promoted_to')
        )
    
    def record_mutation(self, mutation_type: str, description: str, data: Dict = None):
        """Record a mutation to the branch."""
        self.mutations.append({
            'type': mutation_type,
            'description': description,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data or {}
        })


class SeedRegistry:
    """Registry for managing seeds."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path.home() / ".awaos" / "seeds"
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.seeds: Dict[str, SeedManifest] = {}
        self._load()
    
    def _load(self):
        """Load all seeds from registry."""
        for seed_dir in self.registry_path.iterdir():
            if seed_dir.is_dir():
                manifest_path = seed_dir / "seed_manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        data = json.load(f)
                    self.seeds[data['seed_name']] = SeedManifest.from_dict(data)
    
    def register(self, seed: SeedManifest, seed_path: Path):
        """Register a new seed."""
        dest = self.registry_path / seed.seed_name
        
        if dest.exists():
            shutil.rmtree(dest)
        
        shutil.copytree(seed_path, dest)
        
        # Save manifest
        with open(dest / "seed_manifest.json", 'w') as f:
            json.dump(seed.to_dict(), f, indent=2)
        
        self.seeds[seed.seed_name] = seed
    
    def get(self, seed_name: str) -> Optional[SeedManifest]:
        """Get a seed by name."""
        return self.seeds.get(seed_name)
    
    def list_seeds(self) -> List[SeedManifest]:
        """List all registered seeds."""
        return list(self.seeds.values())
    
    def get_path(self, seed_name: str) -> Optional[Path]:
        """Get the path to a seed."""
        if seed_name in self.seeds:
            return self.registry_path / seed_name
        return None


class BranchManager:
    """Manages branches for a realm."""
    
    def __init__(self, realm_path: Path):
        self.realm_path = realm_path
        self.branch_path = realm_path / "mauri" / "branch.json"
        self.branch: Optional[BranchManifest] = None
        self._load()
    
    def _load(self):
        """Load branch manifest."""
        if self.branch_path.exists():
            with open(self.branch_path) as f:
                data = json.load(f)
            self.branch = BranchManifest.from_dict(data)
    
    def save(self):
        """Save branch manifest."""
        if self.branch:
            self.branch_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.branch_path, 'w') as f:
                json.dump(self.branch.to_dict(), f, indent=2)
    
    def create_branch(
        self,
        branch_name: str,
        parent_seed: str,
        realm_name: str,
        glyph_color: str
    ) -> BranchManifest:
        """Create a new branch."""
        self.branch = BranchManifest(
            branch_name=branch_name,
            parent_seed=parent_seed,
            realm_name=realm_name,
            glyph_at_creation=glyph_color
        )
        self.save()
        return self.branch
    
    def add_capability(self, capability: str):
        """Add a capability to the branch."""
        if self.branch and capability not in self.branch.added_capabilities:
            self.branch.added_capabilities.append(capability)
            self.branch.record_mutation(
                'capability_added',
                f"Added capability: {capability}"
            )
            self.save()
    
    def set_env_override(self, key: str, value: str):
        """Set an environment override."""
        if self.branch:
            self.branch.env_overrides[key] = value
            self.branch.record_mutation(
                'env_override',
                f"Set {key}={value}"
            )
            self.save()
    
    def set_toolchain(self, tool: str, implementation: str):
        """Set a toolchain mapping."""
        if self.branch:
            self.branch.toolchain_map[tool] = implementation
            self.branch.record_mutation(
                'toolchain_change',
                f"Set {tool} to {implementation}"
            )
            self.save()


def clone_seed(
    seed_name: str,
    target_path: Path,
    variables: Dict[str, str],
    registry: Optional[SeedRegistry] = None
) -> BranchManifest:
    """
    Clone a seed to create a new realm.
    
    Args:
        seed_name: Name of the seed to clone
        target_path: Where to create the realm
        variables: Template variables to substitute
        registry: Seed registry (uses default if None)
        
    Returns:
        BranchManifest for the new realm
    """
    reg = registry or SeedRegistry()
    seed = reg.get(seed_name)
    
    if not seed:
        raise ValueError(f"Seed '{seed_name}' not found")
    
    seed_path = reg.get_path(seed_name)
    
    # Copy seed to target
    if target_path.exists():
        raise ValueError(f"Target path already exists: {target_path}")
    
    shutil.copytree(seed_path, target_path, ignore=shutil.ignore_patterns('seed_manifest.json'))
    
    # Process templates
    for file_path in target_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.json', '.md', '.py', '.ts', '.yaml', '.yml', '.toml']:
            try:
                content = file_path.read_text()
                for key, value in variables.items():
                    placeholder = f"{{{{{key}}}}}"
                    content = content.replace(placeholder, value)
                file_path.write_text(content)
            except:
                pass
    
    # Create branch manifest
    branch_manager = BranchManager(target_path)
    branch = branch_manager.create_branch(
        branch_name=f"branch_{variables.get('REALM_NAME', 'unnamed')}",
        parent_seed=seed_name,
        realm_name=variables.get('REALM_NAME', 'unnamed'),
        glyph_color=variables.get('GLYPH_COLOR', '#888888')
    )
    
    return branch


def promote_to_seed(
    realm_path: Path,
    new_seed_name: str,
    version: str = "1.0.0",
    description: str = "",
    registry: Optional[SeedRegistry] = None
) -> SeedManifest:
    """
    Promote a branch to a new seed.
    
    Args:
        realm_path: Path to the realm to promote
        new_seed_name: Name for the new seed
        version: Seed version
        description: Seed description
        registry: Seed registry
        
    Returns:
        The new SeedManifest
    """
    from te_hau.mauri.seal import is_sealed, verify_seal
    
    # Validate realm is sealed
    if not is_sealed(realm_path):
        raise ValueError("Realm must be sealed before promotion")
    
    if not verify_seal(realm_path):
        raise ValueError("Realm seal verification failed")
    
    # Load branch manifest
    branch_manager = BranchManager(realm_path)
    if not branch_manager.branch:
        raise ValueError("No branch manifest found")
    
    # Collect files
    files = []
    for item in realm_path.iterdir():
        if item.name not in ['.git', '__pycache__', 'node_modules', '.env']:
            files.append(item.name)
    
    # Detect placeholders from files
    placeholders = detect_placeholders(realm_path)
    
    # Calculate checksum
    checksum = calculate_realm_checksum(realm_path)
    
    # Create seed manifest
    seed = SeedManifest(
        seed_name=new_seed_name,
        version=version,
        description=description or f"Promoted from {branch_manager.branch.branch_name}",
        files=files,
        placeholders=placeholders,
        checksum=checksum
    )
    
    # Register seed
    reg = registry or SeedRegistry()
    reg.register(seed, realm_path)
    
    # Mark branch as promoted
    branch_manager.branch.promoted_to = new_seed_name
    branch_manager.save()
    
    return seed


def detect_placeholders(realm_path: Path) -> List[str]:
    """Detect placeholder patterns in a realm."""
    placeholders = set()
    
    import re
    placeholder_pattern = re.compile(r'\{\{([A-Z_]+)\}\}')
    
    for file_path in realm_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.json', '.md', '.py', '.ts', '.yaml', '.yml']:
            try:
                content = file_path.read_text()
                matches = placeholder_pattern.findall(content)
                placeholders.update(matches)
            except:
                pass
    
    return list(placeholders)


def calculate_realm_checksum(realm_path: Path) -> str:
    """Calculate a checksum for a realm."""
    hasher = hashlib.sha256()
    
    for file_path in sorted(realm_path.rglob('*')):
        if file_path.is_file() and file_path.name not in ['.git', '__pycache__', 'node_modules']:
            try:
                hasher.update(file_path.read_bytes())
            except:
                pass
    
    return hasher.hexdigest()


def merge_branches(
    branch_a_path: Path,
    branch_b_path: Path,
    new_seed_name: str,
    registry: Optional[SeedRegistry] = None
) -> SeedManifest:
    """
    Merge two branches into a new seed.
    
    Args:
        branch_a_path: Path to first branch
        branch_b_path: Path to second branch
        new_seed_name: Name for merged seed
        registry: Seed registry
        
    Returns:
        The merged SeedManifest
    """
    from te_hau.mauri.seal import verify_seal
    
    # Load branch manifests
    branch_a = BranchManager(branch_a_path).branch
    branch_b = BranchManager(branch_b_path).branch
    
    if not branch_a or not branch_b:
        raise ValueError("Both branches must have manifests")
    
    # Check mauri compatibility
    if not verify_seal(branch_a_path) or not verify_seal(branch_b_path):
        raise ValueError("Both branches must have valid seals")
    
    # Create merge directory
    merge_path = Path.home() / ".awaos" / "merges" / new_seed_name
    merge_path.mkdir(parents=True, exist_ok=True)
    
    # Copy branch A as base
    shutil.copytree(branch_a_path, merge_path, dirs_exist_ok=True)
    
    # Merge capabilities
    merged_capabilities = list(set(
        branch_a.added_capabilities + branch_b.added_capabilities
    ))
    
    # Merge env overrides (B takes precedence)
    merged_env = {**branch_a.env_overrides, **branch_b.env_overrides}
    
    # Merge toolchain (B takes precedence)
    merged_toolchain = {**branch_a.toolchain_map, **branch_b.toolchain_map}
    
    # Create merged branch manifest
    merged_branch = BranchManifest(
        branch_name=f"merged_{branch_a.branch_name}_{branch_b.branch_name}",
        parent_seed=f"{branch_a.parent_seed}+{branch_b.parent_seed}",
        realm_name=new_seed_name,
        glyph_at_creation=merge_glyphs(
            branch_a.glyph_at_creation,
            branch_b.glyph_at_creation
        ),
        added_capabilities=merged_capabilities,
        env_overrides=merged_env,
        toolchain_map=merged_toolchain
    )
    
    # Save merged branch
    merge_manager = BranchManager(merge_path)
    merge_manager.branch = merged_branch
    merge_manager.save()
    
    # Promote merged branch to seed
    return promote_to_seed(
        merge_path,
        new_seed_name,
        description=f"Merged from {branch_a.branch_name} and {branch_b.branch_name}",
        registry=registry
    )


def merge_glyphs(color_a: str, color_b: str) -> str:
    """Merge two glyph colors."""
    try:
        # Parse hex colors
        r_a = int(color_a[1:3], 16)
        g_a = int(color_a[3:5], 16)
        b_a = int(color_a[5:7], 16)
        
        r_b = int(color_b[1:3], 16)
        g_b = int(color_b[3:5], 16)
        b_b = int(color_b[5:7], 16)
        
        # Average
        r = (r_a + r_b) // 2
        g = (g_a + g_b) // 2
        b = (b_a + b_b) // 2
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return color_a


def get_lineage(realm_path: Path) -> List[Dict]:
    """Get the lineage (ancestry) of a realm."""
    lineage = []
    
    branch_manager = BranchManager(realm_path)
    if branch_manager.branch:
        lineage.append({
            'type': 'branch',
            'name': branch_manager.branch.branch_name,
            'created_at': branch_manager.branch.created_at.isoformat(),
            'glyph': branch_manager.branch.glyph_at_creation
        })
        
        # Try to find parent seed
        reg = SeedRegistry()
        parent_seed = reg.get(branch_manager.branch.parent_seed)
        if parent_seed:
            lineage.append({
                'type': 'seed',
                'name': parent_seed.seed_name,
                'version': parent_seed.version,
                'created_at': parent_seed.created_at.isoformat()
            })
    
    return lineage
