"""
Service layer for MCP Azure DevOps Server.
"""

import logging
from typing import Any, Dict, List, Optional

from .client import AzureDevOpsClient
from .models import ServiceConnection, VariableGroup

logger = logging.getLogger(__name__)


class VariableGroupService:
    """Service for managing variable groups."""

    def __init__(self, client: AzureDevOpsClient):
        self.client = client

    async def list_variable_groups(
        self, project: str, group_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """List variable groups in a project."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return {"success": False, "error": f"Project '{project}' not found", "data": []}

            # Get variable groups
            variable_groups = await self.client.get_variable_groups(
                project=project_obj.id, group_name=group_name
            )

            if not variable_groups:
                message = f"No variable groups found in project '{project}'"
                if group_name:
                    message += f" with name '{group_name}'"
                return {"success": True, "data": [], "message": message}

            # Format results
            results = []
            for vg in variable_groups:
                variable_count = len(vg.variables)
                secret_count = sum(1 for var in vg.variables.values() if var.is_secret)

                results.append(
                    {
                        "id": vg.id,
                        "name": vg.name,
                        "description": vg.description,
                        "type": vg.type.value,
                        "variable_count": variable_count,
                        "secret_count": secret_count,
                        "created_by": vg.created_by.display_name,
                        "created_on": vg.created_on.isoformat(),
                        "modified_by": vg.modified_by.display_name,
                        "modified_on": vg.modified_on.isoformat(),
                    }
                )

            summary = f"Found {len(results)} variable group(s) in project '{project}'"
            if group_name:
                summary += f" with name '{group_name}'"

            return {"success": True, "data": results, "message": summary}

        except Exception as e:
            logger.error(f"Error listing variable groups: {e}")
            return {"success": False, "error": str(e), "data": []}

    async def get_variable_group_details(self, project: str, group_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific variable group."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return {"success": False, "error": f"Project '{project}' not found"}

            # Get variable group
            vg = await self.client.get_variable_group(project=project_obj.id, group_id=group_id)
            if not vg:
                return {"success": False, "error": f"Variable group with ID {group_id} not found"}

            # Format detailed result
            result = {
                "id": vg.id,
                "name": vg.name,
                "description": vg.description,
                "type": vg.type.value,
                "variables": {},
                "created_by": {
                    "id": vg.created_by.id,
                    "display_name": vg.created_by.display_name,
                    "unique_name": vg.created_by.unique_name,
                },
                "created_on": vg.created_on.isoformat(),
                "modified_by": {
                    "id": vg.modified_by.id,
                    "display_name": vg.modified_by.display_name,
                    "unique_name": vg.modified_by.unique_name,
                },
                "modified_on": vg.modified_on.isoformat(),
                "project_id": vg.project_id,
                "project_name": vg.project_name or project,
            }

            # Include variables with values (secrets are masked)
            for name, var in vg.variables.items():
                result["variables"][name] = {
                    "value": "[SECRET]" if var.is_secret else var.value,
                    "is_secret": var.is_secret,
                }

            return {
                "success": True,
                "data": result,
                "message": f"Variable group '{vg.name}' details",
            }

        except Exception as e:
            logger.error(f"Error getting variable group details: {e}")
            return {"success": False, "error": str(e)}


class ServiceConnectionService:
    """Service for managing service connections."""

    def __init__(self, client: AzureDevOpsClient):
        self.client = client

    async def list_service_connections(
        self, project: str, connection_type: Optional[str] = None, include_shared: bool = True
    ) -> Dict[str, Any]:
        """List service connections in a project."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return {"success": False, "error": f"Project '{project}' not found", "data": []}

            # Get service connections
            service_connections = await self.client.get_service_connections(
                project=project_obj.id, include_shared=include_shared
            )

            # Filter by connection type if specified
            if connection_type:
                service_connections = [
                    sc
                    for sc in service_connections
                    if sc.type.value.lower() == connection_type.lower()
                ]

            if not service_connections:
                message = f"No service connections found in project '{project}'"
                if connection_type:
                    message += f" of type '{connection_type}'"
                return {"success": True, "data": [], "message": message}

            # Format results
            results = []
            for sc in service_connections:
                results.append(
                    {
                        "id": sc.id,
                        "name": sc.name,
                        "type": sc.type.value,
                        "url": sc.url,
                        "description": sc.description,
                        "is_shared": sc.is_shared,
                        "is_ready": sc.is_ready,
                        "owner": sc.owner,
                        "created_by": sc.created_by.display_name if sc.created_by else "Unknown",
                    }
                )

            summary = f"Found {len(results)} service connection(s) in project '{project}'"
            if connection_type:
                summary += f" of type '{connection_type}'"

            return {"success": True, "data": results, "message": summary}

        except Exception as e:
            logger.error(f"Error listing service connections: {e}")
            return {"success": False, "error": str(e), "data": []}

    async def get_service_connection_details(
        self, project: str, connection_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific service connection."""
        try:
            # Validate project exists
            project_obj = await self.client.get_project(project)
            if not project_obj:
                return {"success": False, "error": f"Project '{project}' not found"}

            # Get service connection
            sc = await self.client.get_service_connection(
                project=project_obj.id, connection_id=connection_id
            )
            if not sc:
                return {
                    "success": False,
                    "error": f"Service connection with ID {connection_id} not found",
                }

            # Format detailed result
            result = {
                "id": sc.id,
                "name": sc.name,
                "type": sc.type.value,
                "url": sc.url,
                "description": sc.description,
                "is_shared": sc.is_shared,
                "is_ready": sc.is_ready,
                "owner": sc.owner,
                "created_by": {
                    "id": sc.created_by.id,
                    "display_name": sc.created_by.display_name,
                    "unique_name": sc.created_by.unique_name,
                }
                if sc.created_by
                else None,
                "project_id": sc.project_id,
                "project_name": sc.project_name or project,
                "authorization": {
                    "scheme": sc.authorization.scheme,
                    "parameters": {
                        key: "[REDACTED]"
                        if "password" in key.lower()
                        or "secret" in key.lower()
                        or "key" in key.lower()
                        else value
                        for key, value in sc.authorization.parameters.items()
                    },
                },
                "data": {
                    key: "[REDACTED]"
                    if "password" in key.lower() or "secret" in key.lower() or "key" in key.lower()
                    else value
                    for key, value in sc.data.items()
                },
            }

            return {
                "success": True,
                "data": result,
                "message": f"Service connection '{sc.name}' details",
            }

        except Exception as e:
            logger.error(f"Error getting service connection details: {e}")
            return {"success": False, "error": str(e)}
