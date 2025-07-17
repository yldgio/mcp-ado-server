"""
Data models for Azure DevOps resources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class VariableGroupType(str, Enum):
    """Types of variable groups."""

    VSTS = "Vsts"
    AZURE_KEY_VAULT = "AzureKeyVault"


class ServiceConnectionType(str, Enum):
    """Types of service connections."""

    AZURE_RM = "azurerm"
    GITHUB = "github"
    DOCKER_REGISTRY = "dockerregistry"
    KUBERNETES = "kubernetes"
    GENERIC = "generic"


@dataclass
class User:
    """Represents a user in Azure DevOps."""

    id: str
    display_name: str
    unique_name: str
    image_url: Optional[str] = None


@dataclass
class VariableValue:
    """Represents a variable value in a variable group."""

    value: Optional[str]
    is_secret: bool
    is_readonly: bool = False


@dataclass
class VariableGroup:
    """Represents an Azure DevOps variable group."""

    id: int
    name: str
    description: Optional[str]
    type: VariableGroupType
    variables: Dict[str, VariableValue]
    created_by: User
    created_on: datetime
    modified_by: User
    modified_on: datetime
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "VariableGroup":
        """Create a VariableGroup from Azure DevOps API response."""
        variables = {}
        for key, var_data in data.get("variables", {}).items():
            variables[key] = VariableValue(
                value=var_data.get("value"),
                is_secret=var_data.get("isSecret", False),
                is_readonly=var_data.get("isReadonly", False),
            )

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            type=VariableGroupType(data["type"]),
            variables=variables,
            created_by=User(
                id=data["createdBy"]["id"],
                display_name=data["createdBy"]["displayName"],
                unique_name=data["createdBy"]["uniqueName"],
                image_url=data["createdBy"].get("imageUrl"),
            ),
            created_on=datetime.fromisoformat(data["createdOn"].replace("Z", "+00:00")),
            modified_by=User(
                id=data["modifiedBy"]["id"],
                display_name=data["modifiedBy"]["displayName"],
                unique_name=data["modifiedBy"]["uniqueName"],
                image_url=data["modifiedBy"].get("imageUrl"),
            ),
            modified_on=datetime.fromisoformat(data["modifiedOn"].replace("Z", "+00:00")),
            project_id=data.get("projectId"),
            project_name=data.get("projectName"),
            provider_data=data.get("providerData"),
        )


@dataclass
class ServiceEndpointAuthorization:
    """Represents authorization for a service endpoint."""

    scheme: str
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceConnection:
    """Represents an Azure DevOps service connection."""

    id: str
    name: str
    type: ServiceConnectionType
    url: Optional[str]
    description: Optional[str]
    authorization: ServiceEndpointAuthorization
    data: Dict[str, Any]
    is_shared: bool
    is_ready: bool
    owner: str
    created_by: Optional[User] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ServiceConnection":
        """Create a ServiceConnection from Azure DevOps API response."""
        auth_data = data.get("authorization", {})
        authorization = ServiceEndpointAuthorization(
            scheme=auth_data.get("scheme", ""), parameters=auth_data.get("parameters", {})
        )

        created_by = None
        if "createdBy" in data:
            created_by = User(
                id=data["createdBy"]["id"],
                display_name=data["createdBy"]["displayName"],
                unique_name=data["createdBy"]["uniqueName"],
                image_url=data["createdBy"].get("imageUrl"),
            )

        return cls(
            id=data["id"],
            name=data["name"],
            type=ServiceConnectionType(data.get("type", "generic")),
            url=data.get("url"),
            description=data.get("description"),
            authorization=authorization,
            data=data.get("data", {}),
            is_shared=data.get("isShared", False),
            is_ready=data.get("isReady", False),
            owner=data.get("owner", ""),
            created_by=created_by,
            project_id=data.get("serviceEndpointProjectReferences", [{}])[0]
            .get("projectReference", {})
            .get("id"),
            project_name=data.get("serviceEndpointProjectReferences", [{}])[0]
            .get("projectReference", {})
            .get("name"),
        )


@dataclass
class Project:
    """Represents an Azure DevOps project."""

    id: str
    name: str
    description: Optional[str]
    url: str
    state: str
    visibility: str
    last_update_time: datetime

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Project":
        """Create a Project from Azure DevOps API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            url=data["url"],
            state=data["state"],
            visibility=data["visibility"],
            last_update_time=datetime.fromisoformat(data["lastUpdateTime"].replace("Z", "+00:00")),
        )


@dataclass
class MCPToolResult:
    """Represents the result of an MCP tool execution."""

    content: List[Dict[str, Any]]
    is_error: bool = False

    @classmethod
    def success(cls, data: Any, message: Optional[str] = None) -> "MCPToolResult":
        """Create a successful result."""
        content = [{"type": "text", "text": str(data)}]
        if message:
            content.insert(0, {"type": "text", "text": message})
        return cls(content=content, is_error=False)

    @classmethod
    def error(cls, message: str, details: Optional[str] = None) -> "MCPToolResult":
        """Create an error result."""
        content = [{"type": "text", "text": f"Error: {message}"}]
        if details:
            content.append({"type": "text", "text": f"Details: {details}"})
        return cls(content=content, is_error=True)
