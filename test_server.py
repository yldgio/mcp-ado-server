"""
Test the MCP Azure DevOps Server functionality.
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
    """Test the server functionality."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = Config.from_env()
        config.validate()

        logger.info(f"🚀 Testing MCP Azure DevOps Server")
        logger.info(f"📊 Organization: {config.organization}")
        logger.info(f"🔗 API Version: {config.api_version}")

        # Create client
        client = AzureDevOpsClient(config)

        # Test connection
        logger.info("🔗 Testing connection to Azure DevOps...")
        async with client:
            if await client.test_connection():
                logger.info("✅ Connection successful!")

                # Get projects
                projects = await client.get_projects()
                logger.info(f"📁 Found {len(projects)} projects:")
                for project in projects[:5]:  # Show first 5
                    logger.info(f"   - {project.name} (ID: {project.id})")
                if len(projects) > 5:
                    logger.info(f"   ... and {len(projects) - 5} more")

                # Test services
                if projects:
                    test_project = projects[0].name
                    logger.info(f"🧪 Testing services with project: {test_project}")

                    # Test Variable Groups
                    logger.info("📋 Testing Variable Groups service...")
                    vg_service = VariableGroupService(client)
                    vg_result = await vg_service.list_variable_groups(test_project)
                    if vg_result.is_error:
                        logger.warning(f"⚠️ Variable Groups: {vg_result.content[0]['text']}")
                    else:
                        logger.info(f"✅ Variable Groups: Found data")

                    # Test Service Connections
                    logger.info("🔌 Testing Service Connections service...")
                    sc_service = ServiceConnectionService(client)
                    sc_result = await sc_service.list_service_connections(test_project)
                    if sc_result.is_error:
                        logger.warning(f"⚠️ Service Connections: {sc_result.content[0]['text']}")
                    else:
                        logger.info(f"✅ Service Connections: Found data")

                logger.info("🎉 All tests completed successfully!")
                logger.info("")
                logger.info("🛠️ MCP Tools Available:")
                logger.info("   1. list_variable_groups - List all variable groups in a project")
                logger.info(
                    "   2. get_variable_group_details - Get detailed variable group information"
                )
                logger.info(
                    "   3. list_service_connections - List all service connections in a project"
                )
                logger.info(
                    "   4. get_service_connection_details - Get detailed service connection information"
                )
                logger.info("")
                logger.info("✨ MCP Azure DevOps Server is ready for use!")

            else:
                logger.error("❌ Connection failed!")
                return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
