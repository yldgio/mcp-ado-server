#!/usr/bin/env python3
"""
Simple MCP Azure DevOps Server launcher.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_ado_server.client import AzureDevOpsClient
from mcp_ado_server.config import Config
from mcp_ado_server.services import ServiceConnectionService, VariableGroupService


class SimpleMCPServer:
    """A simple MCP server that handles requests via JSON."""

    def __init__(self, config: Config):
        self.config = config
        self.client = AzureDevOpsClient(config)
        self.vg_service = VariableGroupService(self.client)
        self.sc_service = ServiceConnectionService(self.client)

    async def initialize(self):
        """Initialize the server."""
        async with self.client:
            if not await self.client.test_connection():
                raise RuntimeError("Failed to connect to Azure DevOps")
        print(f"✅ Connected to Azure DevOps organization: {self.config.organization}")

    async def handle_request(self, method: str, params: dict) -> dict:
        """Handle a tool request."""
        try:
            if method == "list_variable_groups":
                project = params.get("project_name")
                if not project:
                    return {"error": "project_name parameter required"}
                result = await self.vg_service.list_variable_groups(project)
                return {"success": True, "data": result.content}

            elif method == "get_variable_group_details":
                project = params.get("project_name")
                group_id = params.get("group_id")
                if not project or not group_id:
                    return {"error": "project_name and group_id parameters required"}
                result = await self.vg_service.get_variable_group_details(project, int(group_id))
                return {"success": True, "data": result.content}

            elif method == "list_service_connections":
                project = params.get("project_name")
                if not project:
                    return {"error": "project_name parameter required"}
                result = await self.sc_service.list_service_connections(project)
                return {"success": True, "data": result.content}

            elif method == "get_service_connection_details":
                project = params.get("project_name")
                connection_id = params.get("connection_id")
                if not project or not connection_id:
                    return {"error": "project_name and connection_id parameters required"}
                result = await self.sc_service.get_service_connection_details(
                    project, connection_id
                )
                return {"success": True, "data": result.content}

            else:
                return {"error": f"Unknown method: {method}"}

        except Exception as e:
            return {"error": str(e)}


async def main():
    """Main server loop."""
    logging.basicConfig(level=logging.INFO)

    # Load configuration
    config = Config.from_env()
    config.validate()

    # Create server
    server = SimpleMCPServer(config)
    await server.initialize()

    print("🚀 MCP Azure DevOps Server is running!")
    print("📋 Available methods:")
    print("   - list_variable_groups(project_name)")
    print("   - get_variable_group_details(project_name, group_id)")
    print("   - list_service_connections(project_name)")
    print("   - get_service_connection_details(project_name, connection_id)")
    print()
    print("💡 Example usage:")
    print("   python simple_server.py")
    print(
        "   Then call: await server.handle_request('list_variable_groups', {'project_name': 'MUR'})"
    )
    print()
    print("🔗 Projects found in your organization:")

    async with server.client:
        projects = await server.client.get_projects()
        for i, project in enumerate(projects[:10]):
            print(f"   {i+1}. {project.name}")
        if len(projects) > 10:
            print(f"   ... and {len(projects) - 10} more")

    print()
    print("✨ Server is ready for use!")


if __name__ == "__main__":
    asyncio.run(main())
