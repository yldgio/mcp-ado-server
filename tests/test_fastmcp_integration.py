"""
Integration test for FastMCP server with new service architecture.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_ado_server.fastmcp_server import (
    get_service_connection,
    get_variable_group,
    initialize_services,
    list_service_connections,
    list_variable_groups,
)


@pytest.fixture
def mock_config():
    """Mock configuration."""
    mock_config = MagicMock()
    mock_config.organization = "test-org"
    mock_config.pat = "test-pat"
    mock_config.base_url = "https://dev.azure.com/test-org"
    return mock_config


@pytest.fixture
def mock_services():
    """Mock services."""
    variable_group_service = AsyncMock()
    service_connection_service = AsyncMock()
    return variable_group_service, service_connection_service


class TestFastMCPIntegration:
    """Test FastMCP server integration with new service architecture."""

    @pytest.mark.asyncio
    async def test_list_variable_groups_success(self, mock_services):
        """Test successful variable groups listing."""
        variable_group_service, _ = mock_services

        # Mock service response in new format (dictionary)
        variable_group_service.list_variable_groups.return_value = {
            "success": True,
            "data": [
                {"id": 1, "name": "test-group-1", "variables": {}},
                {"id": 2, "name": "test-group-2", "variables": {}},
            ],
            "message": "Successfully retrieved variable groups",
        }

        # Mock the global service
        with patch("mcp_ado_server.fastmcp_server.variable_group_service", variable_group_service):
            result = await list_variable_groups("test-project")

        # Verify the result format
        assert result["success"] is True
        assert "data" in result
        assert "message" in result
        assert "count" in result
        assert result["count"] == 2
        assert len(result["data"]) == 2

        # Verify service was called correctly
        variable_group_service.list_variable_groups.assert_called_once_with(
            project="test-project", group_name=None
        )

    @pytest.mark.asyncio
    async def test_list_variable_groups_error(self, mock_services):
        """Test variable groups listing with error."""
        variable_group_service, _ = mock_services

        # Mock service response with error
        variable_group_service.list_variable_groups.return_value = {
            "success": False,
            "error": "API Error",
            "message": "Failed to fetch variable groups",
        }

        with patch("mcp_ado_server.fastmcp_server.variable_group_service", variable_group_service):
            result = await list_variable_groups("test-project")

        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "API Error"

    @pytest.mark.asyncio
    async def test_get_variable_group_success(self, mock_services):
        """Test successful variable group details retrieval."""
        variable_group_service, _ = mock_services

        # Mock service response
        variable_group_service.get_variable_group_details.return_value = {
            "success": True,
            "data": {
                "id": 123,
                "name": "test-group",
                "variables": {"key1": "value1", "key2": "value2"},
            },
            "message": "Successfully retrieved variable group details",
        }

        with patch("mcp_ado_server.fastmcp_server.variable_group_service", variable_group_service):
            result = await get_variable_group("test-project", 123)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["id"] == 123
        assert result["data"]["name"] == "test-group"

        # Verify service call
        variable_group_service.get_variable_group_details.assert_called_once_with(
            project="test-project", group_id=123
        )

    @pytest.mark.asyncio
    async def test_list_service_connections_success(self, mock_services):
        """Test successful service connections listing."""
        _, service_connection_service = mock_services

        # Mock service response
        service_connection_service.list_service_connections.return_value = {
            "success": True,
            "data": [
                {"id": "conn1", "name": "Azure Connection", "type": "AzureRM"},
                {"id": "conn2", "name": "GitHub Connection", "type": "GitHub"},
            ],
            "message": "Successfully retrieved service connections",
        }

        with patch(
            "mcp_ado_server.fastmcp_server.service_connection_service", service_connection_service
        ):
            result = await list_service_connections("test-project")

        # Verify result
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["data"]) == 2

        # Verify service call
        service_connection_service.list_service_connections.assert_called_once_with(
            project="test-project", connection_type=None, include_shared=True
        )

    @pytest.mark.asyncio
    async def test_get_service_connection_success(self, mock_services):
        """Test successful service connection details retrieval."""
        _, service_connection_service = mock_services

        # Mock service response
        service_connection_service.get_service_connection_details.return_value = {
            "success": True,
            "data": {"id": "conn123", "name": "Azure Connection", "type": "AzureRM", "ready": True},
            "message": "Successfully retrieved service connection details",
        }

        with patch(
            "mcp_ado_server.fastmcp_server.service_connection_service", service_connection_service
        ):
            result = await get_service_connection("test-project", "conn123")

        # Verify result
        assert result["success"] is True
        assert result["data"]["id"] == "conn123"
        assert result["data"]["name"] == "Azure Connection"

        # Verify service call
        service_connection_service.get_service_connection_details.assert_called_once_with(
            project="test-project", connection_id="conn123"
        )

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_services):
        """Test exception handling in FastMCP tools."""
        variable_group_service, _ = mock_services

        # Mock service to raise an exception
        variable_group_service.list_variable_groups.side_effect = Exception("Network error")

        with patch("mcp_ado_server.fastmcp_server.variable_group_service", variable_group_service):
            result = await list_variable_groups("test-project")

        # Verify error handling
        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]
        assert "Failed to list variable groups" in result["message"]
