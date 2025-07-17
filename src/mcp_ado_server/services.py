"""
Service layer for MCP Azure DevOps Server.
"""

import logging
from typing import List, Optional

from .client import AzureDevOpsClient
from .models import MCPToolResult, ServiceConnection, VariableGroup

logger = logging.getLogger(__name__)


class VariableGroupService:
    """Service for managing variable groups."""
    
    def __init__(self, client: AzureDevOpsClient):
        self.client = client
    
    async def list_variable_groups(
        self, 
        project: str, 
        group_name: Optional[str] = None
    ) -> MCPToolResult:
        """List variable groups in a project."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return MCPToolResult.error(f"Project '{project}' not found")
            
            # Get variable groups
            variable_groups = await self.client.get_variable_groups(
                project=project_obj.id,
                group_name=group_name
            )
            
            if not variable_groups:
                message = f"No variable groups found in project '{project}'"
                if group_name:
                    message += f" with name '{group_name}'"
                return MCPToolResult.success([], message)
            
            # Format results
            results = []
            for vg in variable_groups:
                variable_count = len(vg.variables)
                secret_count = sum(1 for var in vg.variables.values() if var.is_secret)
                
                results.append({
                    "id": vg.id,
                    "name": vg.name,
                    "description": vg.description,
                    "type": vg.type.value,
                    "variable_count": variable_count,
                    "secret_count": secret_count,
                    "created_by": vg.created_by.display_name,
                    "created_on": vg.created_on.isoformat(),
                    "modified_by": vg.modified_by.display_name,
                    "modified_on": vg.modified_on.isoformat()
                })
            
            summary = f"Found {len(results)} variable group(s) in project '{project}'"
            if group_name:
                summary += f" with name '{group_name}'"
            
            return MCPToolResult.success(results, summary)
        
        except Exception as e:
            logger.error(f"Error listing variable groups: {e}")
            return MCPToolResult.error(
                "Failed to list variable groups",
                str(e)
            )
    
    async def get_variable_group_details(
        self, 
        project: str, 
        group_id: int
    ) -> MCPToolResult:
        """Get detailed information about a specific variable group."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return MCPToolResult.error(f"Project '{project}' not found")
            
            # Get variable group
            vg = await self.client.get_variable_group(project_obj.id, group_id)
            if not vg:
                return MCPToolResult.error(f"Variable group with ID {group_id} not found")
            
            # Format result with detailed information
            variables = []
            for name, var in vg.variables.items():
                variables.append({
                    "name": name,
                    "value": "[HIDDEN]" if var.is_secret else var.value,
                    "is_secret": var.is_secret,
                    "is_readonly": var.is_readonly
                })
            
            result = {
                "id": vg.id,
                "name": vg.name,
                "description": vg.description,
                "type": vg.type.value,
                "variables": variables,
                "created_by": {
                    "display_name": vg.created_by.display_name,
                    "unique_name": vg.created_by.unique_name
                },
                "created_on": vg.created_on.isoformat(),
                "modified_by": {
                    "display_name": vg.modified_by.display_name,
                    "unique_name": vg.modified_by.unique_name
                },
                "modified_on": vg.modified_on.isoformat(),
                "project_id": vg.project_id,
                "project_name": vg.project_name
            }
            
            return MCPToolResult.success(
                result,
                f"Variable group '{vg.name}' details"
            )
        
        except Exception as e:
            logger.error(f"Error getting variable group details: {e}")
            return MCPToolResult.error(
                "Failed to get variable group details",
                str(e)
            )


class ServiceConnectionService:
    """Service for managing service connections."""
    
    def __init__(self, client: AzureDevOpsClient):
        self.client = client
    
    async def list_service_connections(
        self, 
        project: str,
        connection_type: Optional[str] = None,
        include_shared: bool = True
    ) -> MCPToolResult:
        """List service connections in a project."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return MCPToolResult.error(f"Project '{project}' not found")
            
            # Get service connections
            service_connections = await self.client.get_service_connections(
                project=project_obj.id,
                connection_type=connection_type,
                include_shared=include_shared
            )
            
            if not service_connections:
                message = f"No service connections found in project '{project}'"
                if connection_type:
                    message += f" of type '{connection_type}'"
                return MCPToolResult.success([], message)
            
            # Format results
            results = []
            for sc in service_connections:
                results.append({
                    "id": sc.id,
                    "name": sc.name,
                    "type": sc.type.value,
                    "url": sc.url,
                    "description": sc.description,
                    "is_shared": sc.is_shared,
                    "is_ready": sc.is_ready,
                    "owner": sc.owner,
                    "authorization_scheme": sc.authorization.scheme,
                    "created_by": sc.created_by.display_name if sc.created_by else None,
                    "project_name": sc.project_name
                })
            
            summary = f"Found {len(results)} service connection(s) in project '{project}'"
            if connection_type:
                summary += f" of type '{connection_type}'"
            
            return MCPToolResult.success(results, summary)
        
        except Exception as e:
            logger.error(f"Error listing service connections: {e}")
            return MCPToolResult.error(
                "Failed to list service connections",
                str(e)
            )
    
    async def get_service_connection_details(
        self, 
        project: str, 
        connection_id: str
    ) -> MCPToolResult:
        """Get detailed information about a specific service connection."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return MCPToolResult.error(f"Project '{project}' not found")
            
            # Get service connection
            sc = await self.client.get_service_connection(project_obj.id, connection_id)
            if not sc:
                return MCPToolResult.error(f"Service connection with ID {connection_id} not found")
            
            # Format result with detailed information (excluding sensitive data)
            result = {
                "id": sc.id,
                "name": sc.name,
                "type": sc.type.value,
                "url": sc.url,
                "description": sc.description,
                "is_shared": sc.is_shared,
                "is_ready": sc.is_ready,
                "owner": sc.owner,
                "authorization": {
                    "scheme": sc.authorization.scheme,
                    # Don't expose sensitive parameters
                    "parameters": {k: "[HIDDEN]" for k in sc.authorization.parameters.keys()}
                },
                "created_by": {
                    "display_name": sc.created_by.display_name,
                    "unique_name": sc.created_by.unique_name
                } if sc.created_by else None,
                "project_id": sc.project_id,
                "project_name": sc.project_name,
                "data_keys": list(sc.data.keys()) if sc.data else []
            }
            
            return MCPToolResult.success(
                result,
                f"Service connection '{sc.name}' details"
            )
        
        except Exception as e:
            logger.error(f"Error getting service connection details: {e}")
            return MCPToolResult.error(
                "Failed to get service connection details",
                str(e)
            )
