"""
FastMCP Configuration
=====================
Mounts all MCP services as a single consolidated MCP server.

This is the production deployment strategy where one fastMCP instance
loads all service servers (tepo, git, render, supabase) and exposes
them as a single MCP endpoint to GPT Platform.

Usage:
    pip install fastmcp
    python -m fastmcp mount tepo git render supabase
"""

import os
import json
from pathlib import Path

# Configuration for fastMCP mounting
SERVICES = {
    "tepo": {
        "path": "mcp_services/tepo/server.py",
        "env": {
            "TE_PO_BASE_URL": os.getenv("TE_PO_BASE_URL", "http://localhost:8010"),
            "TE_PO_AUTH_TOKEN": os.getenv("TE_PO_AUTH_TOKEN", ""),
            "TE_PO_TIMEOUT": "60",
        },
    },
    "git": {
        "path": "mcp_services/git/server.py",
        "env": {
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        },
    },
    "render": {
        "path": "mcp_services/render/server.py",
        "env": {
            "RENDER_API_KEY": os.getenv("RENDER_API_KEY", ""),
        },
    },
    "supabase": {
        "path": "mcp_services/supabase/server.py",
        "env": {
            "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
            "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
        },
    },
}

# Server configuration
SERVER_CONFIG = {
    "name": "awa-network-mcp",
    "description": "Consolidated MCP for Awa Network - Te Pō, Git, Render, Supabase",
    "version": "1.0.0",
    "host": "127.0.0.1",
    "port": int(os.getenv("MCP_PORT", "3000")),
}

# fastMCP mounting command
"""
To run with fastMCP:

    pip install fastmcp
    python -m fastmcp mount tepo git render supabase --host 127.0.0.1 --port 3000

Or programmatically:

    from fastmcp import create_server, Server
    from pathlib import Path
    
    app = create_server()
    
    # Add each service
    for service_name, config in SERVICES.items():
        server_path = Path(config["path"])
        env_vars = config["env"]
        # Mount server...
"""

# Docker Compose alternative (for all services)
DOCKER_COMPOSE = """
version: '3.9'

services:
  # TepoMCP Server
  tepo-mcp:
    build:
      context: .
      dockerfile: tepo/Dockerfile
    environment:
      TE_PO_BASE_URL: ${TE_PO_BASE_URL:- http://localhost:8010}
      TE_PO_AUTH_TOKEN: ${TE_PO_AUTH_TOKEN:- }
      TE_PO_TIMEOUT: "60"
    ports:
      - "3001:8000"
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Git MCP Server
  git-mcp:
    build:
      context: .
      dockerfile: git/Dockerfile
    environment:
      GITHUB_TOKEN: ${GITHUB_TOKEN:- }
    ports:
      - "3002:8000"
    networks:
      - mcp-network

  # Render MCP Server
  render-mcp:
    build:
      context: .
      dockerfile: render/Dockerfile
    environment:
      RENDER_API_KEY: ${RENDER_API_KEY:- }
    ports:
      - "3003:8000"
    networks:
      - mcp-network

  # Supabase MCP Server
  supabase-mcp:
    build:
      context: .
      dockerfile: supabase/Dockerfile
    environment:
      SUPABASE_URL: ${SUPABASE_URL:- }
      SUPABASE_KEY: ${SUPABASE_KEY:- }
    ports:
      - "3004:8000"
    networks:
      - mcp-network

  # fastMCP Router (optional - aggregates all)
  fastmcp-router:
    image: python:3.11-slim
    working_dir: /app
    command: python -m fastmcp mount tepo git render supabase
    environment:
      TE_PO_BASE_URL: ${TE_PO_BASE_URL:- http://tepo-mcp:8000}
      TE_PO_AUTH_TOKEN: ${TE_PO_AUTH_TOKEN:- }
      GITHUB_TOKEN: ${GITHUB_TOKEN:- }
      RENDER_API_KEY: ${RENDER_API_KEY:- }
      SUPABASE_URL: ${SUPABASE_URL:- }
      SUPABASE_KEY: ${SUPABASE_KEY:- }
      MCP_HOST: "0.0.0.0"
      MCP_PORT: "3000"
    volumes:
      - .:/app
    ports:
      - "3000:3000"
    depends_on:
      - tepo-mcp
      - git-mcp
      - render-mcp
      - supabase-mcp
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
"""


def get_service_config(service_name: str) -> dict:
    """Get configuration for a specific service."""
    return SERVICES.get(service_name, {})


def get_all_services() -> dict:
    """Get all service configurations."""
    return SERVICES


def get_server_config() -> dict:
    """Get server configuration."""
    return SERVER_CONFIG


if __name__ == "__main__":
    print("FastMCP Configuration for Awa Network MCP Services")
    print("=" * 60)
    print("\nServices:")
    for service_name, config in SERVICES.items():
        print(f"\n  {service_name}:")
        print(f"    Path: {config['path']}")
        print(f"    Env: {list(config['env'].keys())}")
    print("\nServer:")
    print(f"  Host: {SERVER_CONFIG['host']}")
    print(f"  Port: {SERVER_CONFIG['port']}")
    print("\nDeployment Options:")
    print("  1. Separate services (development)")
    print("  2. fastMCP mount (single endpoint)")
    print("  3. Docker Compose (containerized)")
    print("  4. Render deployment (production)")
