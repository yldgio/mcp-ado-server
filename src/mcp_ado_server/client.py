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
from .security import SecurityFilter, create_correlation_id, get_secure_logger

logger = logging.getLogger(__name__)
secure_logger = get_secure_logger(__name__)


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
        # Create correlation ID for request tracing
        correlation_id = create_correlation_id()
        
        # Auto-initialize client if needed
        await self._ensure_client_initialized()

        # Add API version to parameters
        if params is None:
            params = {}
        params["api-version"] = self.config.api_version

        # Log request with security filtering
        secure_logger.debug_request(
            method=method,
            url=url,
            params=params,
            headers={"Authorization": "[REDACTED]", "Content-Type": "application/json"},
            json_data=json_data,
            correlation_id=correlation_id
        )

        try:
            assert self._client is not None  # Type guard after initialization
            response = await self._client.request(
                method=method, url=url, params=params, json=json_data
            )

            # Log response with security context
            secure_logger.debug_response(
                status_code=response.status_code,
                response_size=len(response.content),
                correlation_id=correlation_id
            )

            if response.status_code >= 400:
                error_data = None
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    pass

                # Log security event for authentication failures
                if response.status_code == 401:
                    secure_logger.security_event(
                        event_type="AUTHENTICATION_FAILURE",
                        description="Azure DevOps API authentication failed",
                        severity="WARNING",
                        correlation_id=correlation_id,
                        status_code=response.status_code,
                        url=SecurityFilter.filter_url_params(url)
                    )
                elif response.status_code == 403:
                    secure_logger.security_event(
                        event_type="AUTHORIZATION_FAILURE",
                        description="Azure DevOps API authorization failed",
                        severity="WARNING",
                        correlation_id=correlation_id,
                        status_code=response.status_code,
                        url=SecurityFilter.filter_url_params(url)
                    )

                raise AzureDevOpsAPIError(
                    f"API request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            return response.json()

        except httpx.RequestError as e:
            secure_logger.error_with_context(
                message="HTTP request failed",
                error=e,
                correlation_id=correlation_id,
                url=SecurityFilter.filter_url_params(url),
                method=method
            )
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
        correlation_id = create_correlation_id()
        try:
            projects = await self.get_projects()
            secure_logger.info_with_context(
                message=f"Successfully connected to Azure DevOps. Found {len(projects)} projects.",
                correlation_id=correlation_id,
                project_count=len(projects)
            )
            return True
        except Exception as e:
            secure_logger.error_with_context(
                message="Failed to connect to Azure DevOps",
                error=e,
                correlation_id=correlation_id,
                organization=self.config.organization
            )
            return False
