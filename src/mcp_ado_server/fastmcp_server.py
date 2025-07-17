"""
MCP Server implementation for Azure DevOps using FastMCP.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .client import AzureDevOpsClient
from .config import Config
from .services import ServiceConnectionService, VariableGroupService

logger = logging.getLogger(__name__)


# Create FastMCP server instance
mcp = FastMCP("Azure DevOps Server")


# Global variables for services (initialized during startup)
client: Optional[AzureDevOpsClient] = None
variable_group_service: Optional[VariableGroupService] = None
service_connection_service: Optional[ServiceConnectionService] = None


async def initialize_services():
    """Initialize services with configuration."""
    global client, variable_group_service, service_connection_service

    try:
        config = Config.from_env()
        client = AzureDevOpsClient(config)
        variable_group_service = VariableGroupService(client)
        service_connection_service = ServiceConnectionService(client)
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@mcp.tool()
async def list_variable_groups(project: str, group_name: Optional[str] = None) -> Dict[str, Any]:
    """
    List all variable groups in an Azure DevOps project.

    Args:
        project: Project name or ID
        group_name: Filter by group name (optional)

    Returns:
        Dictionary containing variable groups data
    """
    if variable_group_service is None:
        await initialize_services()

    try:
        result = await variable_group_service.list_variable_groups(
            project=project, group_name=group_name
        )
        # Result is now a dictionary, not MCPToolResult
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data", []),
                "message": result.get("message", ""),
                "count": len(result.get("data", [])),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": result.get("message", "Failed to list variable groups"),
            }
    except Exception as e:
        logger.error(f"Error listing variable groups: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to list variable groups: {str(e)}",
        }


@mcp.tool()
async def get_variable_group(project: str, group_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific variable group.

    Args:
        project: Project name or ID
        group_id: Variable group ID

    Returns:
        Dictionary containing variable group details
    """
    if variable_group_service is None:
        await initialize_services()

    try:
        result = await variable_group_service.get_variable_group_details(
            project=project, group_id=group_id
        )
        # Result is now a dictionary, not MCPToolResult
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", ""),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": result.get("message", "Failed to get variable group details"),
            }
    except Exception as e:
        logger.error(f"Error getting variable group details: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get variable group details: {str(e)}",
        }


@mcp.tool()
async def list_service_connections(
    project: str, connection_type: Optional[str] = None, include_shared: bool = True
) -> Dict[str, Any]:
    """
    List all service connections in an Azure DevOps project.

    Args:
        project: Project name or ID
        connection_type: Filter by connection type (optional)
        include_shared: Include shared connections (default: True)

    Returns:
        Dictionary containing service connections data
    """
    if service_connection_service is None:
        await initialize_services()

    try:
        result = await service_connection_service.list_service_connections(
            project=project, connection_type=connection_type, include_shared=include_shared
        )
        # Result is now a dictionary, not MCPToolResult
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data", []),
                "message": result.get("message", ""),
                "count": len(result.get("data", [])),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": result.get("message", "Failed to list service connections"),
            }
    except Exception as e:
        logger.error(f"Error listing service connections: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to list service connections: {str(e)}",
        }


@mcp.tool()
async def get_service_connection(project: str, connection_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific service connection.

    Args:
        project: Project name or ID
        connection_id: Service connection ID

    Returns:
        Dictionary containing service connection details
    """
    if service_connection_service is None:
        await initialize_services()

    try:
        result = await service_connection_service.get_service_connection_details(
            project=project, connection_id=connection_id
        )
        # Result is now a dictionary, not MCPToolResult
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", ""),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": result.get("message", "Failed to get service connection details"),
            }
    except Exception as e:
        logger.error(f"Error getting service connection {connection_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get service connection {connection_id}: {str(e)}",
        }


def run_server():
    """Run the MCP server."""
    try:
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Run the FastMCP server
        mcp.run()

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    run_server()
