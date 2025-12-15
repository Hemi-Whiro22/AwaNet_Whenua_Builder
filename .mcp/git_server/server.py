#!/usr/bin/env python3
"""
Git/GitHub MCP Server
=====================
MCP server for Git and GitHub operations within AwaOS.

Provides:
- Repository initialization
- Commit and push operations
- GitHub repo creation
- Tag management
- Deployment versioning
- Te Ao + Mini Te Pō stack versioning

Environment:
    GITHUB_TOKEN - Personal access token for GitHub API
    GIT_USER_NAME - Git user name
    GIT_USER_EMAIL - Git user email
"""

import os
import json
import asyncio
import subprocess
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

# GitHub API
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AwaOS")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "awaos@local")
GITHUB_API = "https://api.github.com"


@dataclass
class GitConfig:
    """Git configuration."""
    token: str
    user_name: str
    user_email: str
    
    @property
    def has_github(self) -> bool:
        return bool(self.token)


# ═══════════════════════════════════════════════════════════════
# SHELL UTILITIES
# ═══════════════════════════════════════════════════════════════

def run(cmd: str, cwd: Optional[str] = None, check: bool = True) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


# ═══════════════════════════════════════════════════════════════
# GIT CLIENT
# ═══════════════════════════════════════════════════════════════

class GitClient:
    """Git operations wrapper."""
    
    def __init__(self, config: GitConfig):
        self.config = config
    
    # ─────────────────────────────────────────────────────────
    # LOCAL GIT OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def init(self, path: str) -> str:
        """Initialize a new git repository."""
        path = os.path.expanduser(path)
        os.makedirs(path, exist_ok=True)
        run(f"git init", cwd=path)
        run(f'git config user.name "{self.config.user_name}"', cwd=path)
        run(f'git config user.email "{self.config.user_email}"', cwd=path)
        return f"Repository initialized at {path}"
    
    def add(self, path: str, files: str = ".") -> str:
        """Stage files for commit."""
        path = os.path.expanduser(path)
        return run(f"git add {files}", cwd=path)
    
    def commit(self, path: str, message: str) -> str:
        """Commit staged changes."""
        path = os.path.expanduser(path)
        # Escape quotes in message
        message = message.replace('"', '\\"')
        return run(f'git commit -m "{message}"', cwd=path, check=False)
    
    def push(self, path: str, remote: str = "origin", branch: str = "main") -> str:
        """Push commits to remote."""
        path = os.path.expanduser(path)
        return run(f"git push {remote} {branch}", cwd=path, check=False)
    
    def pull(self, path: str, remote: str = "origin", branch: str = "main") -> str:
        """Pull changes from remote."""
        path = os.path.expanduser(path)
        return run(f"git pull {remote} {branch}", cwd=path, check=False)
    
    def status(self, path: str) -> str:
        """Get repository status."""
        path = os.path.expanduser(path)
        return run("git status --short", cwd=path)
    
    def log(self, path: str, count: int = 5) -> str:
        """Get recent commit log."""
        path = os.path.expanduser(path)
        return run(f"git log --oneline -n {count}", cwd=path)
    
    def branch(self, path: str, name: Optional[str] = None) -> str:
        """List branches or create new branch."""
        path = os.path.expanduser(path)
        if name:
            return run(f"git checkout -b {name}", cwd=path, check=False)
        return run("git branch", cwd=path)
    
    def checkout(self, path: str, ref: str) -> str:
        """Checkout a branch or commit."""
        path = os.path.expanduser(path)
        return run(f"git checkout {ref}", cwd=path, check=False)
    
    def tag(self, path: str, name: str, message: Optional[str] = None) -> str:
        """Create a tag."""
        path = os.path.expanduser(path)
        if message:
            message = message.replace('"', '\\"')
            return run(f'git tag -a {name} -m "{message}"', cwd=path)
        return run(f"git tag {name}", cwd=path)
    
    def list_tags(self, path: str) -> List[str]:
        """List all tags."""
        path = os.path.expanduser(path)
        output = run("git tag", cwd=path)
        return output.split("\n") if output else []
    
    def remote_add(self, path: str, name: str, url: str) -> str:
        """Add a remote."""
        path = os.path.expanduser(path)
        return run(f"git remote add {name} {url}", cwd=path, check=False)
    
    def remote_list(self, path: str) -> str:
        """List remotes."""
        path = os.path.expanduser(path)
        return run("git remote -v", cwd=path)
    
    def commit_push(self, path: str, message: str) -> Dict[str, str]:
        """Add all, commit, and push."""
        path = os.path.expanduser(path)
        add_result = self.add(path)
        commit_result = self.commit(path, message)
        push_result = self.push(path)
        return {
            "add": add_result,
            "commit": commit_result,
            "push": push_result
        }
    
    def rollback(self, path: str, tag: str) -> str:
        """Rollback to a specific tag."""
        path = os.path.expanduser(path)
        return run(f"git checkout {tag}", cwd=path, check=False)
    
    # ─────────────────────────────────────────────────────────
    # GITHUB API OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def _github_headers(self) -> Dict[str, str]:
        """Get GitHub API headers."""
        return {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def github_create_repo(
        self, 
        name: str, 
        description: str = "",
        private: bool = True,
        org: Optional[str] = None
    ) -> Dict:
        """Create a new GitHub repository."""
        if not self.config.has_github:
            return {"error": "GITHUB_TOKEN not configured"}
        
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": False
        }
        
        if org:
            url = f"{GITHUB_API}/orgs/{org}/repos"
        else:
            url = f"{GITHUB_API}/user/repos"
        
        response = requests.post(url, json=data, headers=self._github_headers())
        
        if response.status_code == 201:
            repo = response.json()
            return {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "clone_url": repo["clone_url"],
                "ssh_url": repo["ssh_url"],
                "html_url": repo["html_url"]
            }
        return {"error": response.text}
    
    def github_list_repos(self, limit: int = 30) -> List[Dict]:
        """List user's GitHub repositories."""
        if not self.config.has_github:
            return [{"error": "GITHUB_TOKEN not configured"}]
        
        response = requests.get(
            f"{GITHUB_API}/user/repos",
            params={"per_page": limit, "sort": "updated"},
            headers=self._github_headers()
        )
        
        if response.status_code == 200:
            return [
                {
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "private": r["private"],
                    "html_url": r["html_url"]
                }
                for r in response.json()
            ]
        return [{"error": response.text}]
    
    def github_create_release(
        self,
        repo: str,  # owner/repo format
        tag: str,
        name: str,
        body: str = "",
        draft: bool = False,
        prerelease: bool = False
    ) -> Dict:
        """Create a GitHub release."""
        if not self.config.has_github:
            return {"error": "GITHUB_TOKEN not configured"}
        
        data = {
            "tag_name": tag,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        
        response = requests.post(
            f"{GITHUB_API}/repos/{repo}/releases",
            json=data,
            headers=self._github_headers()
        )
        
        if response.status_code == 201:
            release = response.json()
            return {
                "id": release["id"],
                "tag_name": release["tag_name"],
                "html_url": release["html_url"]
            }
        return {"error": response.text}


# ═══════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════

def create_git_server() -> "Server":
    """Create and configure the Git MCP server."""
    
    if not HAS_MCP:
        raise RuntimeError("MCP SDK not installed")
    
    server = Server("git")
    config = GitConfig(GITHUB_TOKEN, GIT_USER_NAME, GIT_USER_EMAIL)
    client = GitClient(config)
    
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="init",
                description="Initialize a new git repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Repository path"}
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="commit_push",
                description="Add, commit, and push changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["path", "message"]
                }
            ),
            Tool(
                name="status",
                description="Get repository status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="log",
                description="Get recent commit log",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "count": {"type": "integer", "default": 5}
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="branch",
                description="List or create branches",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "name": {"type": "string", "description": "New branch name (optional)"}
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="checkout",
                description="Checkout a branch or tag",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "ref": {"type": "string"}
                    },
                    "required": ["path", "ref"]
                }
            ),
            Tool(
                name="tag",
                description="Create a tag",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "name": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["path", "name"]
                }
            ),
            Tool(
                name="rollback",
                description="Rollback to a specific tag",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "tag": {"type": "string"}
                    },
                    "required": ["path", "tag"]
                }
            ),
            Tool(
                name="remote_add",
                description="Add a git remote",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "name": {"type": "string", "default": "origin"},
                        "url": {"type": "string"}
                    },
                    "required": ["path", "url"]
                }
            ),
            Tool(
                name="github_create_repo",
                description="Create a new GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string", "default": ""},
                        "private": {"type": "boolean", "default": True},
                        "org": {"type": "string", "description": "Organization (optional)"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="github_list_repos",
                description="List your GitHub repositories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 30}
                    }
                }
            ),
            Tool(
                name="github_create_release",
                description="Create a GitHub release",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "owner/repo format"},
                        "tag": {"type": "string"},
                        "name": {"type": "string"},
                        "body": {"type": "string", "default": ""},
                        "prerelease": {"type": "boolean", "default": False}
                    },
                    "required": ["repo", "tag", "name"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "init":
                result = client.init(arguments["path"])
            elif name == "commit_push":
                result = client.commit_push(arguments["path"], arguments["message"])
            elif name == "status":
                result = client.status(arguments["path"])
            elif name == "log":
                result = client.log(arguments["path"], arguments.get("count", 5))
            elif name == "branch":
                result = client.branch(arguments["path"], arguments.get("name"))
            elif name == "checkout":
                result = client.checkout(arguments["path"], arguments["ref"])
            elif name == "tag":
                result = client.tag(
                    arguments["path"],
                    arguments["name"],
                    arguments.get("message")
                )
            elif name == "rollback":
                result = client.rollback(arguments["path"], arguments["tag"])
            elif name == "remote_add":
                result = client.remote_add(
                    arguments["path"],
                    arguments.get("name", "origin"),
                    arguments["url"]
                )
            elif name == "github_create_repo":
                result = client.github_create_repo(
                    arguments["name"],
                    arguments.get("description", ""),
                    arguments.get("private", True),
                    arguments.get("org")
                )
            elif name == "github_list_repos":
                result = client.github_list_repos(arguments.get("limit", 30))
            elif name == "github_create_release":
                result = client.github_create_release(
                    arguments["repo"],
                    arguments["tag"],
                    arguments["name"],
                    arguments.get("body", ""),
                    arguments.get("draft", False),
                    arguments.get("prerelease", False)
                )
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            if isinstance(result, str):
                return [TextContent(type="text", text=result)]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    
    return server


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════

async def main():
    """Run the Git MCP server."""
    from mcp.server.stdio import stdio_server
    
    server = create_git_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
