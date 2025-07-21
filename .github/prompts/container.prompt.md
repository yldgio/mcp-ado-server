---
mode: agent
---
# Dev Container Setup Prompt

Configure a dev container for MCP Azure DevOps Server with these requirements:
Act as a senior software architect.

**Base:** Python 3.10+ dev container image
**Tools:** uv package manager, GitHub CLI
**VS Code Extensions:** Python, mypy, black, isort
**Ports:** Forward 8000 for local testing
**Environment:** Pass through AZURE_DEVOPS_PAT and AZURE_DEVOPS_ORGANIZATION
**Setup:** Auto-install project dependencies with `uv pip install -e .[dev]`
**Location:** Create .devcontainer/devcontainer.json

Keep configuration minimal and focused on FastMCP development workflow.
Use Microsoft dev container base images for compatibility.
Include only essential tools for Python MCP server development.
