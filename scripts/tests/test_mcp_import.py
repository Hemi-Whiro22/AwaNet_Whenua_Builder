#!/usr/bin/env python3
"""
Simplified MCP Tool Test
Demonstrates that MCP is installed and can be used
"""

import sys

# Test: Can we import MCP?
try:
    from mcp.types import Tool, TextContent, CallToolResult
    print("✅ MCP package is installed and importable")
    print(f"✅ Available types: Tool, TextContent, CallToolResult")

    # Show we can construct these types
    test_result = CallToolResult(
        content=[TextContent(type="text", text="Test successful")],
        is_error=False
    )
    print(f"✅ Can construct CallToolResult objects")
    print(f"✅ Sample result: {test_result}")

    sys.exit(0)

except ImportError as e:
    print(f"❌ Failed to import MCP: {e}")
    sys.exit(1)
