"""
Basic tests to verify the project is working.
"""

def test_import_modules():
    """Test that all modules can be imported successfully."""
    try:
        from mcp_ado_server.config import Config
        from mcp_ado_server.models import VariableGroup, ServiceConnection
        from mcp_ado_server.client import AzureDevOpsClient
        from mcp_ado_server.services import VariableGroupService, ServiceConnectionService
        from mcp_ado_server.server import MCPAzureDevOpsServer
        assert True
    except ImportError as e:
        assert False, f"Failed to import modules: {e}"


def test_config_creation():
    """Test that Config can be created."""
    config = Config(
        organization="test-org",
        personal_access_token="test-pat"
    )
    assert config.organization == "test-org"
    assert config.personal_access_token == "test-pat"
    assert config.base_url == "https://dev.azure.com/test-org"
    assert config.api_url == "https://dev.azure.com/test-org/_apis"


def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    from mcp_ado_server.models import MCPToolResult
    
    # Test success result
    result = MCPToolResult.success("test data", "Success message")
    assert result.is_error is False
    assert len(result.content) == 2
    assert result.content[0]["text"] == "Success message"
    
    # Test error result
    error_result = MCPToolResult.error("Something went wrong", "Error details")
    assert error_result.is_error is True
    assert len(error_result.content) == 2
    assert "Error: Something went wrong" in error_result.content[0]["text"]
