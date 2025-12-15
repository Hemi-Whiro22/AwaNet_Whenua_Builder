"""
Te Hau Template Renderer

Handles placeholder replacement in template files.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional


PLACEHOLDER_PATTERN = r"\{\{(.*?)\}\}"


def render_template_string(template: str, context: Dict[str, str]) -> str:
    """
    Replace placeholders in a template string.
    
    Args:
        template: Template string with {{placeholder}} syntax
        context: Dictionary of placeholder -> value mappings
        
    Returns:
        Rendered string with placeholders replaced
    """
    def replace_match(match):
        key = match.group(1).strip()
        return context.get(key, match.group(0))
    
    return re.sub(PLACEHOLDER_PATTERN, replace_match, template)


def render_template_file(
    src_path: Path, 
    dst_path: Path, 
    context: Dict[str, str]
) -> None:
    """
    Render a template file to a destination.
    
    Args:
        src_path: Source template file
        dst_path: Destination file path
        context: Placeholder values
    """
    template = src_path.read_text(encoding='utf-8')
    rendered = render_template_string(template, context)
    
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(rendered, encoding='utf-8')


def render_directory(
    src_root: Path, 
    dst_root: Path, 
    context: Dict[str, str],
    skip_patterns: Optional[List[str]] = None
) -> List[Path]:
    """
    Render all files in a directory tree.
    
    Args:
        src_root: Source directory
        dst_root: Destination directory
        context: Placeholder values
        skip_patterns: Glob patterns to skip
        
    Returns:
        List of rendered file paths
    """
    skip_patterns = skip_patterns or ['.git', '__pycache__', '*.pyc', 'node_modules']
    rendered_files = []
    
    for src_path in src_root.rglob('*'):
        # Skip directories and patterns
        if src_path.is_dir():
            continue
            
        rel_path = src_path.relative_to(src_root)
        
        # Check skip patterns
        should_skip = False
        for pattern in skip_patterns:
            if rel_path.match(pattern):
                should_skip = True
                break
        
        if should_skip:
            continue
        
        # Render filename if it contains placeholders
        rel_path_str = str(rel_path)
        rendered_rel_path = render_template_string(rel_path_str, context)
        dst_path = dst_root / rendered_rel_path
        
        # Render content for text files
        if is_text_file(src_path):
            render_template_file(src_path, dst_path, context)
        else:
            # Copy binary files directly
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            dst_path.write_bytes(src_path.read_bytes())
        
        rendered_files.append(dst_path)
    
    return rendered_files


def is_text_file(path: Path) -> bool:
    """
    Check if a file is likely a text file.
    
    Args:
        path: File path to check
        
    Returns:
        True if file appears to be text
    """
    text_extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml',
        '.md', '.txt', '.html', '.css', '.scss', '.toml', '.ini',
        '.sh', '.bash', '.zsh', '.env', '.sql', '.graphql'
    }
    
    # Check extension
    if path.suffix.lower() in text_extensions:
        return True
    
    # Check common filenames
    text_filenames = {
        'Dockerfile', 'Makefile', '.gitignore', '.env.template',
        'requirements.txt', 'README', 'LICENSE'
    }
    
    if path.name in text_filenames:
        return True
    
    return False


def load_template_config(template_path: Path) -> Dict:
    """
    Load template configuration from template.config.json.
    
    Args:
        template_path: Path to template directory
        
    Returns:
        Template configuration dictionary
    """
    config_path = template_path / "template.config.json"
    
    if not config_path.exists():
        return {
            "placeholders": [],
            "renderable_files": [],
            "skip_patterns": []
        }
    
    return json.loads(config_path.read_text(encoding='utf-8'))


def get_required_placeholders(template_path: Path) -> List[str]:
    """
    Extract all placeholders from a template directory.
    
    Args:
        template_path: Path to template directory
        
    Returns:
        List of unique placeholder names
    """
    placeholders = set()
    
    for file_path in template_path.rglob('*'):
        if file_path.is_file() and is_text_file(file_path):
            try:
                content = file_path.read_text(encoding='utf-8')
                matches = re.findall(PLACEHOLDER_PATTERN, content)
                placeholders.update(match.strip() for match in matches)
            except UnicodeDecodeError:
                continue
    
    return sorted(placeholders)
