# Dev Container Setup Guide

## 🚀 Quick Start

This guide will help you set up and use the dev container for MCP Azure DevOps Server development.

## Prerequisites

✅ **Required:**

- VS Code or VS Code Insiders
- Docker Desktop installed and running
- Dev Containers extension (`ms-vscode-remote.remote-containers`)

✅ **Environment Variables (Required):**

```bash
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_ORGANIZATION=your_organization_name
```

## 🔧 Setup Steps

### 1. Clone and Open Project
```bash
git clone <repository-url>
cd mcp-ado
code-insiders .  # or code .
```

### 2. Environment Variables Setup

Create a `.env` file in the project root (if not exists):
```bash
AZURE_DEVOPS_PAT=your_pat_token_here
AZURE_DEVOPS_ORGANIZATION=your_org_name_here
```

**Security Note:** The `.env` file should be in your `.gitignore` to prevent committing secrets.

### 3. Open in Dev Container

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run: `Dev Containers: Reopen in Container`
3. Wait for container to build and setup (first time may take 5-10 minutes)

### 4. Verify Setup

Once the container is running, open a terminal and run:
```bash
# Test basic functionality
python --version  # Should show Python 3.10+
uv --version      # Should show uv package manager

# Test MCP server
mcp-ado-server --help

# Run tests
pytest tests/ -v
```

## 📦 What's Included

### Base Environment
- **Python 3.10** (Debian Bullseye base)
- **uv package manager** for fast dependency management
- **GitHub CLI** for repository operations

### VS Code Extensions
- Python language support
- mypy type checker
- Black formatter
- isort import organizer
- Flake8 linter
- Jupyter notebooks
- GitHub Copilot & Chat

### Development Tools
- All project dependencies pre-installed
- pytest for testing
- Pre-commit hooks ready
- Port 8000 forwarded for local testing

## 🔨 Development Workflow

### Daily Development
```bash
# Start working
code-insiders .
# Reopen in container if not already

# Install new dependencies
uv pip install new-package
uv pip install -e .[dev]  # Reinstall project

# Run tests
pytest tests/ -v
pytest tests/test_specific.py::test_function -v

# Format code (automatic on save)
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run MCP server locally
mcp-ado-server
```

### Testing Azure DevOps Integration
```bash
# Test variable groups
python -c "
from mcp_ado_server.client import AzureDevOpsClient
client = AzureDevOpsClient()
print('Client initialized successfully')
"

# Test with real data (requires valid PAT)
mcp-ado-server
```

## 🐛 Troubleshooting

### Common Issues

**1. Container won't start**
- Ensure Docker Desktop is running
- Check that Dev Containers extension is installed
- Try: `Dev Containers: Rebuild Container`

**2. Python packages not found**
- Run: `uv pip install -e .[dev]` in container terminal
- Verify virtual environment: `which python`

**3. Azure DevOps connection fails**
- Check environment variables: `echo $AZURE_DEVOPS_PAT`
- Verify PAT has correct permissions (Variable Groups, Service Connections)
- Test organization name: `echo $AZURE_DEVOPS_ORGANIZATION`

**4. Port 8000 not accessible**
- Check VS Code Ports panel
- Manually forward port if needed
- Verify MCP server is running: `ps aux | grep mcp-ado-server`

### Environment Variable Issues

If environment variables aren't available in the container:

1. **Check local environment:**
   ```bash
   # On host system
   echo $AZURE_DEVOPS_PAT
   echo $AZURE_DEVOPS_ORGANIZATION
   ```

2. **Set in VS Code settings:**
   Add to `.vscode/settings.json`:
   ```json
   {
     "terminal.integrated.env.linux": {
       "AZURE_DEVOPS_PAT": "your_token",
       "AZURE_DEVOPS_ORGANIZATION": "your_org"
     }
   }
   ```

3. **Manual setup in container:**
   ```bash
   export AZURE_DEVOPS_PAT="your_token"
   export AZURE_DEVOPS_ORGANIZATION="your_org"
   ```

## 🚦 Performance Tips

- **First Build:** Takes 5-10 minutes (downloads base image, installs packages)
- **Subsequent Starts:** ~30-60 seconds (uses cached layers)
- **Rebuild:** Only needed when changing devcontainer.json or Dockerfile

### Speed up Development
- Keep container running between sessions
- Use `uv` for fast package operations
- Enable file watching for hot reload during development

## 📋 Verification Checklist

After setup, verify these work:

- [ ] Python 3.10+ available
- [ ] uv package manager working
- [ ] mcp-ado-server command available
- [ ] pytest runs successfully
- [ ] Environment variables accessible
- [ ] VS Code extensions loaded
- [ ] Port 8000 forwarded
- [ ] Azure DevOps API accessible

## 🆘 Need Help?

1. **Check the logs:**
   - View > Output > Dev Containers
   - View > Problems (for VS Code issues)

2. **Common commands:**
   ```bash
   # Rebuild container
   # Command Palette: "Dev Containers: Rebuild Container"

   # Check container status
   docker ps

   # View container logs
   docker logs <container_id>
   ```

3. **Reset everything:**
   ```bash
   # Command Palette: "Dev Containers: Rebuild Container"
   # Select "Rebuild Without Cache"
   ```

## 🎯 Next Steps

Once your dev container is working:

1. Run the test suite: `pytest tests/ -v`
2. Test MCP server: `mcp-ado-server --help`
3. Connect to Azure DevOps: Test with your PAT
4. Start developing: Add new tools and features
5. Commit changes: Use pre-commit hooks

---

Happy coding! 🎉
