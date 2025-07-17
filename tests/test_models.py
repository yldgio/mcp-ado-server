"""
Tests for the models module.
"""

from datetime import datetime

import pytest

from mcp_ado_server.models import (
    MCPToolResult,
    Project,
    ServiceConnection,
    ServiceConnectionType,
    ServiceEndpointAuthorization,
    User,
    VariableGroup,
    VariableGroupType,
    VariableValue,
)


class TestVariableGroup:
    """Test cases for VariableGroup model."""

    def test_from_api_response(self):
        """Test creating VariableGroup from API response."""
        api_data = {
            "id": 1,
            "name": "Test Variable Group",
            "description": "A test variable group",
            "type": "Vsts",
            "variables": {
                "var1": {"value": "value1", "isSecret": False, "isReadonly": False},
                "secret_var": {"value": "secret_value", "isSecret": True, "isReadonly": True},
            },
            "createdBy": {
                "id": "user1",
                "displayName": "John Doe",
                "uniqueName": "john.doe@example.com",
                "imageUrl": "https://example.com/avatar.jpg",
            },
            "createdOn": "2023-01-01T12:00:00Z",
            "modifiedBy": {
                "id": "user2",
                "displayName": "Jane Smith",
                "uniqueName": "jane.smith@example.com",
            },
            "modifiedOn": "2023-01-02T12:00:00Z",
            "projectId": "proj1",
            "projectName": "Test Project",
        }

        vg = VariableGroup.from_api_response(api_data)

        assert vg.id == 1
        assert vg.name == "Test Variable Group"
        assert vg.description == "A test variable group"
        assert vg.type == VariableGroupType.VSTS
        assert len(vg.variables) == 2
        assert vg.variables["var1"].value == "value1"
        assert vg.variables["var1"].is_secret is False
        assert vg.variables["secret_var"].is_secret is True
        assert vg.created_by.display_name == "John Doe"
        assert vg.modified_by.display_name == "Jane Smith"
        assert vg.project_id == "proj1"


class TestServiceConnection:
    """Test cases for ServiceConnection model."""

    def test_from_api_response(self):
        """Test creating ServiceConnection from API response."""
        api_data = {
            "id": "conn1",
            "name": "Test Service Connection",
            "type": "azurerm",
            "url": "https://management.azure.com/",
            "description": "A test service connection",
            "authorization": {
                "scheme": "ServicePrincipal",
                "parameters": {"tenantid": "tenant1", "serviceprincipalid": "sp1"},
            },
            "data": {"subscriptionId": "sub1", "subscriptionName": "Test Subscription"},
            "isShared": False,
            "isReady": True,
            "owner": "Library",
            "createdBy": {
                "id": "user1",
                "displayName": "John Doe",
                "uniqueName": "john.doe@example.com",
            },
            "serviceEndpointProjectReferences": [
                {"projectReference": {"id": "proj1", "name": "Test Project"}}
            ],
        }

        sc = ServiceConnection.from_api_response(api_data)

        assert sc.id == "conn1"
        assert sc.name == "Test Service Connection"
        assert sc.type == ServiceConnectionType.AZURE_RM
        assert sc.url == "https://management.azure.com/"
        assert sc.description == "A test service connection"
        assert sc.authorization.scheme == "ServicePrincipal"
        assert sc.authorization.parameters["tenantid"] == "tenant1"
        assert sc.is_shared is False
        assert sc.is_ready is True
        assert sc.owner == "Library"
        assert sc.created_by.display_name == "John Doe"
        assert sc.project_id == "proj1"
        assert sc.project_name == "Test Project"


class TestProject:
    """Test cases for Project model."""

    def test_from_api_response(self):
        """Test creating Project from API response."""
        api_data = {
            "id": "proj1",
            "name": "Test Project",
            "description": "A test project",
            "url": "https://dev.azure.com/test-org/proj1",
            "state": "wellFormed",
            "visibility": "private",
            "lastUpdateTime": "2023-01-01T12:00:00Z",
        }

        project = Project.from_api_response(api_data)

        assert project.id == "proj1"
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.url == "https://dev.azure.com/test-org/proj1"
        assert project.state == "wellFormed"
        assert project.visibility == "private"
        assert isinstance(project.last_update_time, datetime)


class TestMCPToolResult:
    """Test cases for MCPToolResult model."""

    def test_success_result(self):
        """Test creating a successful result."""
        data = {"key": "value"}
        result = MCPToolResult.success(data, "Operation successful")

        assert result.is_error is False
        assert len(result.content) == 2
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "Operation successful"
        assert result.content[1]["type"] == "text"
        assert "{'key': 'value'}" in result.content[1]["text"]

    def test_error_result(self):
        """Test creating an error result."""
        result = MCPToolResult.error("Something went wrong", "Additional details")

        assert result.is_error is True
        assert len(result.content) == 2
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "Error: Something went wrong"
        assert result.content[1]["type"] == "text"
        assert result.content[1]["text"] == "Details: Additional details"

    def test_success_result_without_message(self):
        """Test creating a successful result without message."""
        data = [1, 2, 3]
        result = MCPToolResult.success(data)

        assert result.is_error is False
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert "[1, 2, 3]" in result.content[0]["text"]

    def test_error_result_without_details(self):
        """Test creating an error result without details."""
        result = MCPToolResult.error("Something went wrong")

        assert result.is_error is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "Error: Something went wrong"
