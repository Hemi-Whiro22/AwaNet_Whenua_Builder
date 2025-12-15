"""
Te Hau Filesystem Operations

Safe file and directory operations for realm management.
"""

import shutil
from pathlib import Path
from typing import Dict, Optional, List
import json


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_empty_directory(path: Path) -> Path:
    """
    Ensure a directory exists and is empty.
    
    Args:
        path: Directory path
        
    Returns:
        The path (for chaining)
    """
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_tree(src: Path, dst: Path) -> Path:
    """
    Copy a directory tree to a new location.
    
    Args:
        src: Source directory
        dst: Destination directory
        
    Returns:
        Destination path
    """
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def write_json(path: Path, data: Dict, indent: int = 2) -> None:
    """
    Write data to a JSON file.
    
    Args:
        path: File path
        data: Data to write
        indent: JSON indentation level
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=indent, ensure_ascii=False),
        encoding='utf-8'
    )


def read_json(path: Path) -> Dict:
    """
    Read data from a JSON file.
    
    Args:
        path: File path
        
    Returns:
        Parsed JSON data
    """
    return json.loads(path.read_text(encoding='utf-8'))


def write_env(path: Path, env_dict: Dict[str, str]) -> None:
    """
    Write environment variables to a .env file.
    
    Args:
        path: File path
        env_dict: Environment variables
    """
    lines = []
    for key, value in env_dict.items():
        # Quote values with special characters
        if any(c in value for c in ' \t\n"\''):
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def read_env(path: Path) -> Dict[str, str]:
    """
    Read environment variables from a .env file.
    
    Args:
        path: File path
        
    Returns:
        Dictionary of environment variables
    """
    env_dict = {}
    
    if not path.exists():
        return env_dict
    
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            key, value = line.split('=', 1)
            # Remove quotes
            value = value.strip('"\'')
            env_dict[key.strip()] = value
    
    return env_dict


def get_awaos_root() -> Path:
    """
    Get the AwaOS installation root directory.
    
    Returns:
        Path to AwaOS root
    """
    # Check for AWAOS_ROOT environment variable
    import os
    if 'AWAOS_ROOT' in os.environ:
        return Path(os.environ['AWAOS_ROOT'])
    
    # Default to parent of te_hau package
    return Path(__file__).parent.parent.parent


def get_template_path() -> Path:
    """
    Get the path to the project template.
    
    Returns:
        Path to project_template directory
    """
    return get_awaos_root() / "project_template"


def get_projects_path() -> Path:
    """
    Get the path where new projects are created.
    
    Returns:
        Path to projects directory (~/.awanet/projects)
    """
    return get_user_config_path() / "projects"


def get_user_config_path() -> Path:
    """
    Get the user configuration directory.
    
    Returns:
        Path to ~/.awanet
    """
    return Path.home() / ".awanet"


# Alias for compatibility
get_awanet_path = get_user_config_path


def list_realms() -> List[str]:
    """
    List all existing realm projects.
    
    Returns:
        List of realm names
    """
    projects_path = get_projects_path()
    
    if not projects_path.exists():
        return []
    
    realms = []
    for path in projects_path.iterdir():
        if path.is_dir() and (path / "mauri" / "realm_lock.json").exists():
            realms.append(path.name)
    
    return sorted(realms)


def realm_exists(realm_name: str) -> bool:
    """
    Check if a realm already exists.
    
    Args:
        realm_name: Name of the realm
        
    Returns:
        True if realm exists
    """
    return realm_name in list_realms()
