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

### Running the Server

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
