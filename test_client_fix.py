#!/usr/bin/env python3
"""
Test script to verify the Azure DevOps client fix.
"""

import asyncio
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_ado_server.fastmcp_server import list_variable_groups


async def test_fastmcp_tools():
    """Test the FastMCP tools with the fixed client."""
    print("🔍 Testing FastMCP Tools with Fixed Client...")

    try:
        # Test list variable groups
        print("📋 Testing list_variable_groups...")
        result = await list_variable_groups("MUR")

        if result.get("success"):
            print(f"✅ Variable groups listed successfully")
            print(f"   Count: {result.get('count', 0)}")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Failed to list variable groups: {result.get('error', 'Unknown error')}")
            return False

        print("\n🎉 FastMCP tools are working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error testing FastMCP tools: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_fastmcp_tools())
    sys.exit(0 if success else 1)
