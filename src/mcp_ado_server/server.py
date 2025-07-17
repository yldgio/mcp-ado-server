"""
MCP Server implementation for Azure DevOps.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from .client import AzureDevOpsClient
from .config import Config
from .services import ServiceConnectionService, VariableGroupService

logger = logging.getLogger(__name__)


class MCPAzureDevOpsServer:
    """MCP Server for Azure DevOps interactions."""
    
    def __init__(self, config: Config):
        self.config = config
        self.server = Server("mcp-ado-server")
        self.client: Optional[AzureDevOpsClient] = None
        self.variable_group_service: Optional[VariableGroupService] = None
        self.service_connection_service: Optional[ServiceConnectionService] = None
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register MCP handlers."""
        self.server.list_tools = self._list_tools
        self.server.call_tool = self._call_tool
    
    async def _list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools."""
        tools = [
            Tool(
                name="list_variable_groups",
                description="List all variable groups in an Azure DevOps project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name or ID"
                        },
                        "group_name": {
                            "type": "string",
                            "description": "Filter by group name (optional)"
                        }
                    },
                    "required": ["project"]
                }
            ),
            Tool(
                name="get_variable_group_details",
                description="Get detailed information about a specific variable group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name or ID"
                        },
                        "group_id": {
                            "type": "integer",
                            "description": "Variable group ID"
                        }
                    },
                    "required": ["project", "group_id"]
                }
            ),
            Tool(
                name="list_service_connections",
                description="List all service connections in an Azure DevOps project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name or ID"
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by connection type (optional)"
                        },
                        "include_shared": {
                            "type": "boolean",
                            "description": "Include shared connections",
                            "default": True
                        }
                    },
                    "required": ["project"]
                }
            ),
            Tool(
                name="get_service_connection_details",
                description="Get detailed information about a specific service connection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name or ID"
                        },
                        "connection_id": {
                            "type": "string",
                            "description": "Service connection ID"
                        }
                    },
                    "required": ["project", "connection_id"]
                }
            )
        ]
        
        return ListToolsResult(tools=tools)
    
    async def _call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls."""
        if not self.client:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Azure DevOps client not initialized")],
                isError=True
            )
        
        try:
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            if tool_name == "list_variable_groups":
                result = await self.variable_group_service.list_variable_groups(
                    project=arguments["project"],
                    group_name=arguments.get("group_name")
                )
            elif tool_name == "get_variable_group_details":
                result = await self.variable_group_service.get_variable_group_details(
                    project=arguments["project"],
                    group_id=arguments["group_id"]
                )
            elif tool_name == "list_service_connections":
                result = await self.service_connection_service.list_service_connections(
                    project=arguments["project"],
                    connection_type=arguments.get("type"),
                    include_shared=arguments.get("include_shared", True)
                )
            elif tool_name == "get_service_connection_details":
                result = await self.service_connection_service.get_service_connection_details(
                    project=arguments["project"],
                    connection_id=arguments["connection_id"]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {tool_name}")],
                    isError=True
                )
            
            # Convert result to MCP format
            content = []
            for item in result.content:
                if item.get("type") == "text":
                    content.append(TextContent(type="text", text=item["text"]))
                else:
                    # For structured data, convert to formatted JSON
                    formatted_data = json.dumps(item, indent=2, default=str)
                    content.append(TextContent(type="text", text=formatted_data))
            
            return CallToolResult(
                content=content,
                isError=result.is_error
            )
        
        except Exception as e:
            logger.error(f"Error executing tool {request.params.name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )
    
    async def initialize(self) -> None:
        """Initialize the server and services."""
        try:
            # Initialize Azure DevOps client
            self.client = AzureDevOpsClient(self.config)
            
            # Initialize services
            self.variable_group_service = VariableGroupService(self.client)
            self.service_connection_service = ServiceConnectionService(self.client)
            
            logger.info("MCP Azure DevOps Server initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
    
    async def run(self) -> None:
        """Run the MCP server."""
        try:
            await self.initialize()
            
            # Test connection
            async with self.client as client:
                if not await client.test_connection():
                    raise RuntimeError("Failed to connect to Azure DevOps")
            
            # Run the server
            async with stdio_server() as streams:
                await self.server.run(
                    streams[0],
                    streams[1],
                    InitializationOptions(
                        server_name="mcp-ado-server",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities()
                    )
                )
        
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
