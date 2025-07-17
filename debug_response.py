"""
Debug the response format to understand the data structure.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_ado_server.client import AzureDevOpsClient
from mcp_ado_server.config import Config
from mcp_ado_server.services import ServiceConnectionService, VariableGroupService


async def main():
    """Debug the response format."""
    logging.basicConfig(level=logging.WARNING)

    try:
        config = Config.from_env()
        config.validate()

        client = AzureDevOpsClient(config)
        vg_service = VariableGroupService(client)

        async with client:
            test_project = "MUR"
            print(f"🔍 Debugging response format for project: {test_project}")

            # Get variable groups and examine raw response
            vg_result = await vg_service.list_variable_groups(test_project)

            print(f"\n📋 Raw Variable Groups Response:")
            print(f"   is_error: {vg_result.is_error}")
            print(f"   content length: {len(vg_result.content)}")

            for i, content in enumerate(vg_result.content):
                print(f"\n   Content [{i}]:")
                print(f"     Type: {type(content)}")
                print(f"     Keys: {content.keys() if isinstance(content, dict) else 'Not a dict'}")
                if isinstance(content, dict) and "text" in content:
                    text_content = content["text"]
                    print(f"     Text type: {type(text_content)}")
                    print(f"     Text preview: {repr(text_content[:200])}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
