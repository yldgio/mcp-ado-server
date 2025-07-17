"""
Tests for the Azure DevOps client module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from mcp_ado_server.client import AzureDevOpsClient, AzureDevOpsAPIError
from mcp_ado_server.config import Config


@pytest.fixture
def config():
    """Create a test configuration."""
    return Config(
        organization='test-org',
        personal_access_token='test-pat',
        api_version='7.0'
    )


@pytest.fixture
def client(config):
    """Create a test client."""
    return AzureDevOpsClient(config)


class TestAzureDevOpsClient:
    """Test cases for AzureDevOpsClient."""
    
    def test_create_auth_header(self, client):
        """Test creating authorization header."""
        auth_header = client._create_auth_header()
        # The header should be "Basic " + base64(":test-pat")
        assert auth_header.startswith("Basic ")
        assert len(auth_header) > 6  # "Basic " + encoded content
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test using client as async context manager."""
        async with client as c:
            assert c._client is not None
            assert isinstance(c._client, httpx.AsyncClient)
        # Client should be closed after exiting context
        assert c._client is None or c._client.is_closed
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": [{"id": 1, "name": "test"}]}
        
        with patch.object(client, '_client') as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)
            
            result = await client._make_request("GET", "https://test.com/api")
            
            assert result == {"value": [{"id": 1, "name": "test"}]}
            mock_client.request.assert_called_once_with(
                method="GET",
                url="https://test.com/api",
                params={"api-version": "7.0"},
                json=None
            )
    
    @pytest.mark.asyncio
    async def test_make_request_api_error(self, client):
        """Test API request with error response."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.json.return_value = {"message": "Resource not found"}
        
        with patch.object(client, '_client') as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)
            
            with pytest.raises(AzureDevOpsAPIError) as exc_info:
                await client._make_request("GET", "https://test.com/api")
            
            assert exc_info.value.status_code == 404
            assert "Not Found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        """Test API request with network error."""
        with patch.object(client, '_client') as mock_client:
            mock_client.request = AsyncMock(side_effect=httpx.RequestError("Network error"))
            
            with pytest.raises(AzureDevOpsAPIError) as exc_info:
                await client._make_request("GET", "https://test.com/api")
            
            assert "Request failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_projects_success(self, client):
        """Test successful project retrieval."""
        mock_response = {
            "value": [
                {
                    "id": "proj1",
                    "name": "Test Project",
                    "description": "A test project",
                    "url": "https://dev.azure.com/test-org/proj1",
                    "state": "wellFormed",
                    "visibility": "private",
                    "lastUpdateTime": "2023-01-01T12:00:00Z"
                }
            ]
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            projects = await client.get_projects()
            
            assert len(projects) == 1
            assert projects[0].name == "Test Project"
            assert projects[0].id == "proj1"
    
    @pytest.mark.asyncio
    async def test_get_project_success(self, client):
        """Test successful single project retrieval."""
        mock_response = {
            "id": "proj1",
            "name": "Test Project",
            "description": "A test project",
            "url": "https://dev.azure.com/test-org/proj1",
            "state": "wellFormed",
            "visibility": "private",
            "lastUpdateTime": "2023-01-01T12:00:00Z"
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            project = await client.get_project("proj1")
            
            assert project is not None
            assert project.name == "Test Project"
            assert project.id == "proj1"
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client):
        """Test project retrieval when project doesn't exist."""
        error = AzureDevOpsAPIError("Not found", status_code=404)
        
        with patch.object(client, '_make_request', side_effect=error):
            project = await client.get_project("nonexistent")
            
            assert project is None
    
    @pytest.mark.asyncio
    async def test_get_variable_groups_success(self, client):
        """Test successful variable groups retrieval."""
        mock_response = {
            "value": [
                {
                    "id": 1,
                    "name": "Test Variable Group",
                    "description": "A test variable group",
                    "type": "Vsts",
                    "variables": {
                        "var1": {
                            "value": "value1",
                            "isSecret": False,
                            "isReadonly": False
                        }
                    },
                    "createdBy": {
                        "id": "user1",
                        "displayName": "John Doe",
                        "uniqueName": "john.doe@example.com"
                    },
                    "createdOn": "2023-01-01T12:00:00Z",
                    "modifiedBy": {
                        "id": "user2",
                        "displayName": "Jane Smith",
                        "uniqueName": "jane.smith@example.com"
                    },
                    "modifiedOn": "2023-01-02T12:00:00Z"
                }
            ]
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            vgs = await client.get_variable_groups("proj1")
            
            assert len(vgs) == 1
            assert vgs[0].name == "Test Variable Group"
            assert vgs[0].id == 1
    
    @pytest.mark.asyncio
    async def test_get_service_connections_success(self, client):
        """Test successful service connections retrieval."""
        mock_response = {
            "value": [
                {
                    "id": "conn1",
                    "name": "Test Service Connection",
                    "type": "azurerm",
                    "url": "https://management.azure.com/",
                    "description": "A test service connection",
                    "authorization": {
                        "scheme": "ServicePrincipal",
                        "parameters": {
                            "tenantid": "tenant1",
                            "serviceprincipalid": "sp1"
                        }
                    },
                    "data": {},
                    "isShared": False,
                    "isReady": True,
                    "owner": "Library",
                    "serviceEndpointProjectReferences": [
                        {
                            "projectReference": {
                                "id": "proj1",
                                "name": "Test Project"
                            }
                        }
                    ]
                }
            ]
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            scs = await client.get_service_connections("proj1")
            
            assert len(scs) == 1
            assert scs[0].name == "Test Service Connection"
            assert scs[0].id == "conn1"
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, client):
        """Test successful connection test."""
        mock_projects = [
            MagicMock(name="Test Project")
        ]
        
        with patch.object(client, 'get_projects', return_value=mock_projects):
            result = await client.test_connection()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, client):
        """Test failed connection test."""
        with patch.object(client, 'get_projects', side_effect=Exception("Connection failed")):
            result = await client.test_connection()
            
            assert result is False
