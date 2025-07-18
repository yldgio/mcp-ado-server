"""
Azure DevOps API client for MCP server.
"""

import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from .config import Config
from .models import Project, ServiceConnection, VariableGroup

logger = logging.getLogger(__name__)


class AzureDevOpsAPIError(Exception):
    """Exception raised for Azure DevOps API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AzureDevOpsClient:
    """Client for interacting with Azure DevOps REST API."""

    def __init__(self, config: Config):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._auth_header = self._create_auth_header()

    def _create_auth_header(self) -> str:
        """Create the authorization header value."""
        # Azure DevOps uses basic auth with empty username and PAT as password
        credentials = f":{self.config.personal_access_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    async def __aenter__(self) -> "AzureDevOpsClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.request_timeout),
            headers={
                "Authorization": self._auth_header,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        return self

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client_initialized(self) -> None:
        """Ensure the HTTP client is initialized."""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.request_timeout),
                headers={
                    "Authorization": self._auth_header,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Azure DevOps API."""
        # Auto-initialize client if needed
        await self._ensure_client_initialized()

        # Add API version to parameters
        if params is None:
            params = {}
        params["api-version"] = self.config.api_version

        logger.debug(f"Making {method} request to {url} with params: {params}")

        try:
            assert self._client is not None  # Type guard after initialization
            response = await self._client.request(
                method=method, url=url, params=params, json=json_data
            )

            if response.status_code >= 400:
                error_data = None
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    pass

                raise AzureDevOpsAPIError(
                    f"API request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            return response.json()

        except httpx.RequestError as e:
            raise AzureDevOpsAPIError(f"Request failed: {str(e)}")

    async def get_projects(self) -> List[Project]:
        """Get all projects in the organization."""
        url = f"{self.config.api_url}/projects"

        response = await self._make_request("GET", url)
        projects = []

        for project_data in response.get("value", []):
            projects.append(Project.from_api_response(project_data))

        return projects

    async def get_project(self, project_id_or_name: str) -> Optional[Project]:
        """Get a specific project by ID or name."""
        url = f"{self.config.api_url}/projects/{project_id_or_name}"

        try:
            response = await self._make_request("GET", url)
            return Project.from_api_response(response)
        except AzureDevOpsAPIError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_variable_groups(
        self, project: str, group_name: Optional[str] = None
    ) -> List[VariableGroup]:
        """Get variable groups for a project."""
        # Use project-specific API URL for variable groups
        url = f"{self.config.project_api_url(project)}/distributedtask/variablegroups"

        params = {}
        if group_name:
            params["groupName"] = group_name

        response = await self._make_request("GET", url, params=params)
        variable_groups = []

        for vg_data in response.get("value", []):
            variable_groups.append(VariableGroup.from_api_response(vg_data))

        return variable_groups

    async def get_variable_group(self, project: str, group_id: int) -> Optional[VariableGroup]:
        """Get a specific variable group by ID."""
        # Use project-specific API URL for variable group details
        url = f"{self.config.project_api_url(project)}/distributedtask/variablegroups/{group_id}"

        try:
            response = await self._make_request("GET", url)
            return VariableGroup.from_api_response(response)
        except AzureDevOpsAPIError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_service_connections(
        self, project: str, connection_type: Optional[str] = None, include_shared: bool = True
    ) -> List[ServiceConnection]:
        """Get service connections for a project."""
        # Use project-specific API URL for service connections
        url = f"{self.config.project_api_url(project)}/serviceendpoint/endpoints"

        params = {}
        if connection_type:
            params["type"] = connection_type
        if include_shared:
            params["includeShared"] = "true"

        response = await self._make_request("GET", url, params=params)
        service_connections = []

        for sc_data in response.get("value", []):
            service_connections.append(ServiceConnection.from_api_response(sc_data))

        return service_connections

    async def get_service_connection(
        self, project: str, connection_id: str
    ) -> Optional[ServiceConnection]:
        """Get a specific service connection by ID."""
        # Use project-specific API URL for service connection details
        url = f"{self.config.project_api_url(project)}/serviceendpoint/endpoints/{connection_id}"
        logger.info(f"Fetching service connection from URL: {url}")
        try:
            response = await self._make_request("GET", url)
            return ServiceConnection.from_api_response(response)
        except AzureDevOpsAPIError as e:
            if e.status_code == 404:
                return None
            raise

    async def test_connection(self) -> bool:
        """Test the connection to Azure DevOps."""
        try:
            projects = await self.get_projects()
            logger.info(f"Successfully connected to Azure DevOps. Found {len(projects)} projects.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Azure DevOps: {e}")
            return False
