# MCP Azure DevOps Server

A Model Context Protocol (MCP) server for interacting with Azure DevOps, focusing on variable groups and service connections.

## Features

- **Variable Groups**: List and inspect variable groups in Azure DevOps projects
- **Service Connections**: List and inspect service connections in Azure DevOps projects
- **Secure Authentication**: Support for Personal Access Tokens and Azure AD
- **Type Safety**: Full type hints and Pydantic models
- **Async Support**: Efficient async/await implementation
- **Structured Logging**: Comprehensive logging with correlation IDs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                         │
│  (Tool handlers, Server setup, Transport management)       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│  (VariableGroupService, ServiceConnectionService)          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Azure DevOps Client Layer                  │
│  (Authentication, HTTP client, API wrappers)               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
│  (Configuration, Logging, Error handling)                  │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
# Azure DevOps Configuration
AZURE_DEVOPS_ORGANIZATION=your-org
AZURE_DEVOPS_PAT=your-personal-access-token

# Optional: Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Usage

### VS Code Configuration (MCP Integration)

To use this MCP server with VS Code and GitHub Copilot, follow these steps:

#### 1. Install VS Code Extension

Install the **MCP Client** extension from the VS Code marketplace or use the integrated MCP support in GitHub Copilot.

#### 2. Configure MCP Settings

Add the following configuration to your VS Code `settings.json`:

```json
{
  "mcp.servers": {
    "azure-devops": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "d:\\projects\\training\\vibe\\mcp-ado",
        "mcp-ado-server"
      ],
      "env": {
        "AZURE_DEVOPS_ORGANIZATION": "your-organization",
        "AZURE_DEVOPS_PAT": "your-personal-access-token",
        "LOG_LEVEL": "INFO"
      },
      "initializationOptions": {
        "timeout": 30000,
        "retries": 3
      }
    }
  }
}
```

> **📁 Quick Start**: Copy the complete configuration from [`examples/vscode-settings.json`](examples/vscode-settings.json)

#### 3. Alternative: Using Python Directly

If you prefer not to use `uv`, configure with Python directly:

```json
{
  "mcp.servers": {
    "azure-devops": {
      "command": "python",
      "args": [
        "-m",
        "mcp_ado_server.main"
      ],
      "cwd": "d:\\projects\\training\\vibe\\mcp-ado",
      "env": {
        "AZURE_DEVOPS_ORGANIZATION": "your-organization",
        "AZURE_DEVOPS_PAT": "your-personal-access-token"
      }
    }
  }
}
```

#### 4. Environment Variables Setup

Create a `.env` file in the project root or use VS Code's environment configuration:

```bash
# Azure DevOps Configuration
AZURE_DEVOPS_ORGANIZATION=your-organization
AZURE_DEVOPS_PAT=your-personal-access-token

# Optional: Advanced Configuration
AZURE_DEVOPS_API_VERSION=7.0
LOG_LEVEL=INFO
LOG_FORMAT=json
HTTP_TIMEOUT=30
MAX_RETRIES=3
```

#### 5. Verify MCP Connection

1. Restart VS Code after configuration
2. Open the Command Palette (`Ctrl+Shift+P`)
3. Run `MCP: Show Connected Servers`
4. Verify that `azure-devops` appears in the list
5. Check the Output panel for any connection errors

#### 6. Using MCP Tools in Copilot

Once configured, you can use the tools in GitHub Copilot chats:

```
@copilot List all variable groups in the MyProject project

@copilot Show me service connections for the DevOps-Project, filtering by Azure type

@copilot What variable groups exist in project "Infrastructure" with name containing "prod"?
```

#### 7. Troubleshooting

**Common Issues:**

- **Authentication Errors**: Verify your PAT has correct permissions
- **Connection Timeout**: Increase timeout in `initializationOptions`
- **Command Not Found**: Ensure `uv` is in your PATH or use absolute path
- **Permission Denied**: Check Azure DevOps project permissions

**Debug Mode:**

Enable debug logging by setting:

```json
{
  "mcp.servers": {
    "azure-devops": {
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Running the Server Standalone

For testing or standalone usage:

```bash
# Start the MCP server
mcp-ado-server

# Or with custom configuration
mcp-ado-server --config /path/to/config.toml
```

### Available Tools

#### 1. List Variable Groups

```json
{
  "name": "list_variable_groups",
  "description": "List all variable groups in an Azure DevOps project",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project": {"type": "string", "description": "Project name or ID"},
      "group_name": {"type": "string", "description": "Filter by group name (optional)"}
    },
    "required": ["project"]
  }
}
```

#### 2. List Service Connections

```json
{
  "name": "list_service_connections",
  "description": "List all service connections in an Azure DevOps project",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project": {"type": "string", "description": "Project name or ID"},
      "type": {"type": "string", "description": "Filter by connection type (optional)"},
      "include_shared": {"type": "boolean", "description": "Include shared connections", "default": true}
    },
    "required": ["project"]
  }
}
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_variable_groups.py
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Type checking
mypy src

# Run all quality checks
pre-commit run --all-files
```

## Security

### Authentication

- **Personal Access Token (PAT)**: Primary authentication method
- **Azure AD**: Enterprise authentication support
- **Service Principal**: For automated scenarios

### Required Scopes

- `Variable Groups (read)`: For variable group operations
- `Service Connections (read)`: For service connection operations
- `Project and Team (read)`: For project validation

### Security Best Practices

- Store tokens securely using environment variables
- Use minimal required token scopes
- Implement proper input validation
- Log all operations for audit purposes
- Respect Azure DevOps API rate limits

## Documentation

- **[VS Code Setup Guide](docs/VSCODE_SETUP.md)**: Complete guide for configuring MCP in VS Code
- **[API Documentation](docs/API.md)**: Detailed API reference
- **[Architecture Overview](docs/ARCHITECTURE.md)**: System design and architecture decisions

## API Documentation

For detailed API documentation, see [API.md](docs/API.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

- Open an issue on GitHub
- Check the [troubleshooting guide](docs/TROUBLESHOOTING.md)
- Review the [FAQ](docs/FAQ.md)
