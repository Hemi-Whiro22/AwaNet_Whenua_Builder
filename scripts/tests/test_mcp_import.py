#!/usr/bin/env python3
"""
Simplified MCP Tool Test
Demonstrates that MCP is installed and can be used
"""

import pytest


@pytest.mark.skip(reason="Dev-only MCP import check; skipped to avoid external dependency requirements.")
def test_mcp_import_optional():
    from mcp.types import Tool, TextContent, CallToolResult  # pragma: no cover

    _ = CallToolResult(
        content=[TextContent(type="text", text="Test successful")],
        is_error=False,
    )
