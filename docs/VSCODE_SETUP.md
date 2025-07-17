# VS Code MCP Configuration Guide

## Overview

This guide provides detailed instructions for configuring the MCP Azure DevOps Server with VS Code and GitHub Copilot.

## Prerequisites

1. **VS Code**: Version 1.80 or later
2. **GitHub Copilot**: Extension installed and activated
3. **MCP Server**: Azure DevOps MCP Server installed (see main README)
4. **Azure DevOps**: Valid organization and Personal Access Token

## Step-by-Step Configuration

### 1. Install Required Extensions

```bash
# Via VS Code Extensions Marketplace
# Search for and install:
# - GitHub Copilot
# - MCP Client (if available)
```

### 2. Configure VS Code Settings

Open VS Code settings (`Ctrl+,`) and add the MCP server configuration:

#### Method A: Using Settings UI

1. Open Settings (`Ctrl+,`)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Add the configuration below

#### Method B: Direct settings.json Edit

Open your `settings.json` file and add:

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
        "AZURE_DEVOPS_ORGANIZATION": "CINECA-DataPlatform",
        "AZURE_DEVOPS_PAT": "your-personal-access-token",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json"
      },
      "initializationOptions": {
        "timeout": 30000,
        "retries": 3,
        "healthCheck": true
      }
    }
  },
  "mcp.logLevel": "info",
  "mcp.autoReconnect": true
}
```

### 3. Environment Setup Options

#### Option A: VS Code Environment Variables

Configure directly in VS Code settings:

```json
{
  "mcp.servers": {
    "azure-devops": {
      "env": {
        "AZURE_DEVOPS_ORGANIZATION": "your-org",
        "AZURE_DEVOPS_PAT": "your-token",
        "AZURE_DEVOPS_API_VERSION": "7.0",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Option B: .env File

Create `.env` file in project root:

```bash
# Azure DevOps Configuration
AZURE_DEVOPS_ORGANIZATION=CINECA-DataPlatform
AZURE_DEVOPS_PAT=your-personal-access-token

# Optional Configuration
AZURE_DEVOPS_API_VERSION=7.0
LOG_LEVEL=INFO
LOG_FORMAT=json
HTTP_TIMEOUT=30
MAX_RETRIES=3
```

#### Option C: System Environment Variables

Set system-wide environment variables:

```powershell
# PowerShell (Windows)
$env:AZURE_DEVOPS_ORGANIZATION="your-org"
$env:AZURE_DEVOPS_PAT="your-token"
```

```bash
# Bash (Linux/Mac)
export AZURE_DEVOPS_ORGANIZATION="your-org"
export AZURE_DEVOPS_PAT="your-token"
```

### 4. Alternative Python Configuration

If you prefer using Python directly instead of uv:

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
        "AZURE_DEVOPS_ORGANIZATION": "your-org",
        "AZURE_DEVOPS_PAT": "your-token"
      }
    }
  }
}
```

### 5. Verification and Testing

#### Check MCP Connection

1. **Restart VS Code** after configuration changes
2. Open Command Palette (`Ctrl+Shift+P`)
3. Run: `MCP: Show Connected Servers`
4. Verify `azure-devops` appears in the list

#### Test MCP Tools

Use GitHub Copilot to test the tools:

```
@copilot List variable groups in CINECA-DataPlatform project

@copilot Show service connections for MyProject

@copilot What are the variable groups containing "prod" in their name?
```

#### Debug Connection Issues

Enable debug logging:

```json
{
  "mcp.servers": {
    "azure-devops": {
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  },
  "mcp.logLevel": "debug"
}
```

Check the Output panel:
1. View → Output
2. Select "MCP" from dropdown
3. Look for connection and error messages

### 6. Advanced Configuration

#### Custom Configuration File

Create a custom config file:

```json
{
  "mcp.servers": {
    "azure-devops": {
      "command": "uv",
      "args": [
        "run",
        "mcp-ado-server",
        "--config",
        "d:\\projects\\training\\vibe\\mcp-ado\\config\\production.toml"
      ]
    }
  }
}
```

#### Multiple Environment Support

Configure different environments:

```json
{
  "mcp.servers": {
    "azure-devops-dev": {
      "command": "uv",
      "args": ["run", "mcp-ado-server"],
      "env": {
        "AZURE_DEVOPS_ORGANIZATION": "dev-org",
        "AZURE_DEVOPS_PAT": "dev-token"
      }
    },
    "azure-devops-prod": {
      "command": "uv",
      "args": ["run", "mcp-ado-server"],
      "env": {
        "AZURE_DEVOPS_ORGANIZATION": "prod-org",
        "AZURE_DEVOPS_PAT": "prod-token"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `Unauthorized (401)`

**Solutions**:
- Verify PAT is correct and not expired
- Check PAT permissions include:
  - Variable Groups (read)
  - Service Connections (read)
  - Project and Team (read)

#### 2. Connection Timeout

**Error**: `Connection timeout`

**Solutions**:
- Increase timeout in `initializationOptions`
- Check network connectivity
- Verify organization name is correct

#### 3. Command Not Found

**Error**: `'uv' is not recognized`

**Solutions**:
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Use absolute path to uv executable
- Switch to Python configuration

#### 4. Permission Denied

**Error**: `Access denied to project`

**Solutions**:
- Verify user has access to the Azure DevOps project
- Check project permissions in Azure DevOps
- Confirm organization name is correct

### Debug Commands

```bash
# Test server manually
cd d:\projects\training\vibe\mcp-ado
uv run mcp-ado-server --debug

# Verify environment
uv run python -c "from src.mcp_ado_server.config import Config; print(Config.from_env())"

# Test Azure DevOps connection
uv run python -c "
from src.mcp_ado_server.client import AzureDevOpsClient
import asyncio
async def test():
    client = AzureDevOpsClient.from_env()
    projects = await client.get_projects()
    print(f'Found {len(projects)} projects')
asyncio.run(test())
"
```

### Performance Optimization

#### 1. Connection Pooling

```json
{
  "mcp.servers": {
    "azure-devops": {
      "initializationOptions": {
        "connectionPool": {
          "maxConnections": 10,
          "keepAlive": true
        }
      }
    }
  }
}
```

#### 2. Caching

```json
{
  "mcp.servers": {
    "azure-devops": {
      "env": {
        "CACHE_TTL": "300",
        "ENABLE_CACHING": "true"
      }
    }
  }
}
```

## Best Practices

### Security

1. **Never commit PATs** to version control
2. **Use environment variables** for sensitive data
3. **Rotate PATs regularly** (recommended: every 90 days)
4. **Use minimal permissions** for PATs
5. **Monitor PAT usage** in Azure DevOps

### Performance

1. **Use appropriate timeout values** (30s for most operations)
2. **Enable caching** for frequently accessed data
3. **Monitor memory usage** with debug logging
4. **Configure connection pooling** for high-volume usage

### Maintenance

1. **Keep MCP server updated** to latest version
2. **Monitor logs** for errors and warnings
3. **Test configuration** after VS Code updates
4. **Backup configuration** files

## Integration Examples

### Example Copilot Conversations

```
User: @copilot What variable groups exist in the Infrastructure project?

Copilot: I'll check the variable groups in the Infrastructure project for you.

[Uses list_variable_groups tool]

Found 3 variable groups in the Infrastructure project:
1. "prod-secrets" - Contains production environment secrets
2. "dev-config" - Development configuration variables
3. "shared-resources" - Shared resource identifiers

User: @copilot Show me service connections for DevOps-Project with Azure type

Copilot: Let me list the Azure service connections in the DevOps-Project.

[Uses list_service_connections tool with type filter]

Found 2 Azure service connections:
1. "azure-prod-subscription" - Connected to production subscription
2. "azure-dev-subscription" - Connected to development subscription
```

### Workflow Integration

```json
// Example: Use in VS Code tasks
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check Variable Groups",
      "type": "shell",
      "command": "echo",
      "args": ["Use @copilot to list variable groups"],
      "group": "build"
    }
  ]
}
```

This completes the VS Code MCP configuration guide. The server should now be fully integrated with your development environment.
