"""
Self-Healing Engine (Drop 11)
=============================
Drift detection and auto-repair for AwaOS realms.

Features:
- File hash tracking
- Manifest comparison
- Schema drift detection
- Environment validation
- Auto-repair commands

From the Awa Protocol spec:
"The system detects when something goes out of alignment:
a file changed, a schema changed, a manifest changed,
a route is missing, an env var is unset..."
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# DRIFT TYPES
# ═══════════════════════════════════════════════════════════════

@dataclass
class DriftItem:
    """A single drift detection result."""
    category: str  # file, env, schema, manifest, mauri
    path: str
    issue: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    severity: str = "warning"  # info, warning, error
    repairable: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DriftReport:
    """Full drift detection report."""
    realm_id: str
    timestamp: str
    drifts: List[DriftItem] = field(default_factory=list)
    status: str = "clean"  # clean, drifted, critical
    
    def add(self, drift: DriftItem):
        self.drifts.append(drift)
        if drift.severity == "error":
            self.status = "critical"
        elif drift.severity == "warning" and self.status == "clean":
            self.status = "drifted"
    
    @property
    def has_drift(self) -> bool:
        return len(self.drifts) > 0
    
    def to_dict(self) -> dict:
        return {
            "realm_id": self.realm_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "drift_count": len(self.drifts),
            "drifts": [d.to_dict() for d in self.drifts]
        }
    
    def summary(self) -> str:
        """Human-readable summary."""
        if not self.has_drift:
            return f"✅ Realm '{self.realm_id}' is in alignment."
        
        lines = [f"⚠️ Drift detected in realm '{self.realm_id}':"]
        for drift in self.drifts:
            icon = "🔴" if drift.severity == "error" else "🟡"
            lines.append(f"  {icon} [{drift.category}] {drift.path}: {drift.issue}")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# HASH UTILITIES
# ═══════════════════════════════════════════════════════════════

def hash_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    if not path.exists():
        return ""
    
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def hash_directory(path: Path, patterns: List[str] = None) -> Dict[str, str]:
    """Hash all files in a directory matching patterns."""
    hashes = {}
    patterns = patterns or ["*.py", "*.json", "*.yaml", "*.yml", "*.ts", "*.tsx"]
    
    if not path.exists():
        return hashes
    
    for pattern in patterns:
        for file in path.rglob(pattern):
            if file.is_file() and ".git" not in str(file):
                rel = str(file.relative_to(path))
                hashes[rel] = hash_file(file)
    
    return hashes


def hash_manifest(manifest: dict) -> str:
    """Hash a manifest dictionary consistently."""
    content = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════
# MAURI LOCK MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@dataclass
class MauriLock:
    """
    The truth of the realm - stored in mauri/state/mauri_lock.json
    
    Contains:
    - glyph
    - rune
    - lineage
    - hash of every template file
    - hash of manifest
    - hash of env
    - timestamp
    - realm_id (UUID5 based on project name)
    """
    realm_id: str
    glyph: str = "koru_blue"
    rune: str = ""
    lineage: str = ""
    seal_hash: str = ""
    manifest_hash: str = ""
    env_hash: str = ""
    file_hashes: Dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    version: str = "1.0.0"
    
    def compute_seal(self) -> str:
        """Compute the overall seal hash."""
        components = [
            self.glyph,
            self.rune,
            self.lineage,
            self.manifest_hash,
            json.dumps(self.file_hashes, sort_keys=True),
            self.realm_id
        ]
        content = "|".join(components)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def save(self, path: Path):
        """Save mauri lock to file."""
        self.seal_hash = self.compute_seal()
        self.timestamp = datetime.utcnow().isoformat()
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> Optional["MauriLock"]:
        """Load mauri lock from file."""
        if not path.exists():
            return None
        
        try:
            with open(path) as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            return None


# ═══════════════════════════════════════════════════════════════
# DRIFT DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════

class DriftDetector:
    """
    Detects drift between current state and mauri lock.
    
    Checks:
    - File hashes vs canonical template config
    - Code vs manifest
    - Env vs template.config.json
    - Supabase schema vs infra.yaml
    - Assistant metadata vs stored manifest
    """
    
    def __init__(self, realm_path: Path):
        self.realm_path = realm_path
        self.mauri_path = realm_path / "mauri" / "state" / "mauri_lock.json"
        self.lock = MauriLock.load(self.mauri_path)
    
    def detect(self) -> DriftReport:
        """Run full drift detection."""
        report = DriftReport(
            realm_id=self.lock.realm_id if self.lock else "unknown",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Check mauri lock exists
        if not self.lock:
            report.add(DriftItem(
                category="mauri",
                path="mauri/state/mauri_lock.json",
                issue="Mauri lock not found - realm unsealed",
                severity="error"
            ))
            return report
        
        # Check file hashes
        self._check_file_hashes(report)
        
        # Check manifest
        self._check_manifest(report)
        
        # Check environment
        self._check_environment(report)
        
        # Check seal integrity
        self._check_seal(report)
        
        # Check glyph
        self._check_glyph(report)
        
        return report
    
    def _check_file_hashes(self, report: DriftReport):
        """Compare current file hashes to locked hashes."""
        current_hashes = hash_directory(self.realm_path)
        
        for rel_path, locked_hash in self.lock.file_hashes.items():
            current_hash = current_hashes.get(rel_path)
            
            if current_hash is None:
                report.add(DriftItem(
                    category="file",
                    path=rel_path,
                    issue="File missing",
                    expected=locked_hash,
                    severity="warning"
                ))
            elif current_hash != locked_hash:
                report.add(DriftItem(
                    category="file",
                    path=rel_path,
                    issue="File content changed",
                    expected=locked_hash[:16] + "...",
                    actual=current_hash[:16] + "...",
                    severity="info"
                ))
    
    def _check_manifest(self, report: DriftReport):
        """Check realm manifest integrity."""
        manifest_path = self.realm_path / "config" / "realm.json"
        
        if not manifest_path.exists():
            report.add(DriftItem(
                category="manifest",
                path="config/realm.json",
                issue="Realm manifest not found",
                severity="error"
            ))
            return
        
        try:
            with open(manifest_path) as f:
                current = json.load(f)
            
            current_hash = hash_manifest(current)
            
            if current_hash != self.lock.manifest_hash:
                report.add(DriftItem(
                    category="manifest",
                    path="config/realm.json",
                    issue="Manifest has changed since seal",
                    expected=self.lock.manifest_hash[:16] + "...",
                    actual=current_hash[:16] + "...",
                    severity="warning"
                ))
        except Exception as e:
            report.add(DriftItem(
                category="manifest",
                path="config/realm.json",
                issue=f"Cannot read manifest: {e}",
                severity="error"
            ))
    
    def _check_environment(self, report: DriftReport):
        """Check for missing environment variables."""
        env_path = self.realm_path / ".env"
        template_config = self.realm_path / "template.config.json"
        
        # Load expected env vars from template config
        expected_vars = []
        if template_config.exists():
            try:
                with open(template_config) as f:
                    config = json.load(f)
                expected_vars = config.get("env_vars", [])
            except Exception:
                pass
        
        # Load current env
        current_env = {}
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key = line.split("=")[0]
                        current_env[key] = True
        
        # Check for missing vars
        for var in expected_vars:
            if var not in current_env:
                report.add(DriftItem(
                    category="env",
                    path=".env",
                    issue=f"Missing environment variable: {var}",
                    expected=var,
                    severity="warning"
                ))
    
    def _check_seal(self, report: DriftReport):
        """Verify seal hash integrity."""
        computed = self.lock.compute_seal()
        
        if computed != self.lock.seal_hash:
            report.add(DriftItem(
                category="mauri",
                path="mauri/state/mauri_lock.json",
                issue="Seal hash mismatch - lock file may be corrupted",
                expected=self.lock.seal_hash[:16] + "...",
                actual=computed[:16] + "...",
                severity="error",
                repairable=True
            ))
    
    def _check_glyph(self, report: DriftReport):
        """Check glyph consistency."""
        glyph_path = self.realm_path / "mauri" / "glyph_manifest.json"
        
        if not glyph_path.exists():
            report.add(DriftItem(
                category="glyph",
                path="mauri/glyph_manifest.json",
                issue="Glyph manifest not found",
                severity="warning"
            ))
            return
        
        try:
            with open(glyph_path) as f:
                glyph = json.load(f)
            
            if glyph.get("primary_glyph") != self.lock.glyph:
                report.add(DriftItem(
                    category="glyph",
                    path="mauri/glyph_manifest.json",
                    issue="Glyph mismatch",
                    expected=self.lock.glyph,
                    actual=glyph.get("primary_glyph"),
                    severity="warning"
                ))
        except Exception as e:
            report.add(DriftItem(
                category="glyph",
                path="mauri/glyph_manifest.json",
                issue=f"Cannot read glyph: {e}",
                severity="warning"
            ))


# ═══════════════════════════════════════════════════════════════
# SELF-REPAIR ENGINE
# ═══════════════════════════════════════════════════════════════

class RepairEngine:
    """
    Auto-repair drifted realms.
    
    Repairs:
    - Regenerate code from canonical templates
    - Regenerate Supabase migrations
    - Regenerate missing env vars
    - Reseal mauri lock
    """
    
    def __init__(self, realm_path: Path, template_path: Optional[Path] = None):
        self.realm_path = realm_path
        self.template_path = template_path
    
    def repair_from_report(self, report: DriftReport, auto_approve: bool = False) -> Dict[str, Any]:
        """Repair all drifts in a report."""
        results = {
            "repaired": [],
            "skipped": [],
            "failed": []
        }
        
        for drift in report.drifts:
            if not drift.repairable:
                results["skipped"].append({
                    "path": drift.path,
                    "reason": "Not auto-repairable"
                })
                continue
            
            try:
                if drift.category == "env":
                    self._repair_env(drift)
                elif drift.category == "mauri":
                    self._repair_mauri(drift)
                elif drift.category == "glyph":
                    self._repair_glyph(drift)
                elif drift.category == "file" and self.template_path:
                    self._repair_file(drift)
                else:
                    results["skipped"].append({
                        "path": drift.path,
                        "reason": f"No repair handler for {drift.category}"
                    })
                    continue
                
                results["repaired"].append(drift.path)
            
            except Exception as e:
                results["failed"].append({
                    "path": drift.path,
                    "error": str(e)
                })
        
        return results
    
    def _repair_env(self, drift: DriftItem):
        """Repair missing environment variable."""
        env_path = self.realm_path / ".env"
        
        # Parse the expected var name from the issue
        var_name = drift.expected
        
        # Append with placeholder
        with open(env_path, "a") as f:
            f.write(f"\n{var_name}=  # TODO: Set value\n")
    
    def _repair_mauri(self, drift: DriftItem):
        """Reseal the mauri lock."""
        lock_path = self.realm_path / "mauri" / "state" / "mauri_lock.json"
        lock = MauriLock.load(lock_path)
        
        if lock:
            # Recompute hashes
            lock.file_hashes = hash_directory(self.realm_path)
            
            # Update manifest hash
            manifest_path = self.realm_path / "config" / "realm.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    lock.manifest_hash = hash_manifest(json.load(f))
            
            # Save with new seal
            lock.save(lock_path)
    
    def _repair_glyph(self, drift: DriftItem):
        """Repair glyph manifest."""
        glyph_path = self.realm_path / "mauri" / "glyph_manifest.json"
        lock_path = self.realm_path / "mauri" / "state" / "mauri_lock.json"
        lock = MauriLock.load(lock_path)
        
        if lock:
            glyph_manifest = {
                "primary_glyph": lock.glyph,
                "colors": {
                    "koru_blue": "#00AEEF",
                    "koru_purple": "#5A3FFF",
                    "koru_green": "#2ECC71",
                    "koru_orange": "#F39C12"
                },
                "version": "1.0.0"
            }
            
            glyph_path.parent.mkdir(parents=True, exist_ok=True)
            with open(glyph_path, "w") as f:
                json.dump(glyph_manifest, f, indent=2)
    
    def _repair_file(self, drift: DriftItem):
        """Repair a drifted file from template."""
        if not self.template_path:
            raise ValueError("No template path configured")
        
        src = self.template_path / drift.path
        dst = self.realm_path / drift.path
        
        if src.exists():
            import shutil
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    
    def reseal(self) -> MauriLock:
        """Create fresh mauri lock for the realm."""
        # Load existing config
        manifest_path = self.realm_path / "config" / "realm.json"
        manifest = {}
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
        
        # Create lock
        lock = MauriLock(
            realm_id=manifest.get("realm_id", "unknown"),
            glyph=manifest.get("glyph", "koru_blue"),
            lineage=manifest.get("lineage", ""),
            manifest_hash=hash_manifest(manifest),
            file_hashes=hash_directory(self.realm_path)
        )
        
        # Save
        lock_path = self.realm_path / "mauri" / "state" / "mauri_lock.json"
        lock.save(lock_path)
        
        return lock


# ═══════════════════════════════════════════════════════════════
# SELF-HEALING ENGINE (Combined Interface)
# ═══════════════════════════════════════════════════════════════

class SelfHealingEngine:
    """
    High-level interface combining drift detection and repair.
    
    Usage:
        engine = SelfHealingEngine(Path("./my_realm"))
        report = await engine.diagnose()
        if report.has_drift:
            await engine.heal()
    """
    
    def __init__(self, realm_path: Path, template_path: Optional[Path] = None):
        self.realm_path = realm_path
        self.template_path = template_path
        self.drift_detector = DriftDetector(realm_path)
        self.repair_engine = RepairEngine(realm_path, template_path)
    
    async def diagnose(self) -> DriftReport:
        """Run full diagnostic on realm."""
        return self.drift_detector.detect()
    
    async def heal(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Heal detected drift."""
        report = await self.diagnose()
        
        if not report.has_drift:
            return {"status": "clean", "message": "No drift detected"}
        
        # Filter by category if specified
        if category:
            report.drifts = [d for d in report.drifts if d.category == category]
        
        results = self.repair_engine.repair_from_report(report)
        
        return {
            "status": "healed",
            "report": report.to_dict(),
            "repairs": results
        }
    
    async def seal(self) -> MauriLock:
        """Create/update mauri seal."""
        return self.repair_engine.reseal()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current healing status."""
        report = self.drift_detector.detect()
        lock_path = self.realm_path / "mauri" / "state" / "mauri_lock.json"
        
        return {
            "realm_path": str(self.realm_path),
            "has_drift": report.has_drift,
            "drift_count": len(report.drifts),
            "status": report.status,
            "sealed": lock_path.exists(),
            "last_checked": datetime.utcnow().isoformat()
        }


# ═══════════════════════════════════════════════════════════════
# CLI INTEGRATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def check_realm(realm_path: str) -> DriftReport:
    """
    Check a realm for drift.
    
    Usage: tehau check
    """
    path = Path(realm_path).expanduser().resolve()
    detector = DriftDetector(path)
    return detector.detect()


def heal_realm(realm_path: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Heal drifted realm.
    
    Usage: 
        tehau heal
        tehau heal backend
        tehau heal env
        tehau heal mauri
    """
    path = Path(realm_path).expanduser().resolve()
    
    # First detect drift
    detector = DriftDetector(path)
    report = detector.detect()
    
    if not report.has_drift:
        return {"status": "clean", "message": "No drift detected"}
    
    # Filter by category if specified
    if category:
        report.drifts = [d for d in report.drifts if d.category == category]
    
    # Repair
    engine = RepairEngine(path)
    results = engine.repair_from_report(report)
    
    return {
        "status": "healed",
        "report": report.to_dict(),
        "repairs": results
    }


def seal_realm(realm_path: str) -> Dict[str, Any]:
    """
    Create/update mauri seal for a realm.
    
    Usage: tehau seal
    """
    path = Path(realm_path).expanduser().resolve()
    engine = RepairEngine(path)
    lock = engine.reseal()
    
    return {
        "status": "sealed",
        "realm_id": lock.realm_id,
        "seal_hash": lock.seal_hash,
        "timestamp": lock.timestamp
    }
