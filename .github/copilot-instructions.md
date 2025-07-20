# GitHub Copilot Instructions for MCP Azure DevOps Server

When generating code, follow these instructions carefully. I am GitHub Copilot.

## Project Context

**Project:** MCP Azure DevOps Server  
**Purpose:** Model Context Protocol server for Azure DevOps variable groups and service connections  
**Tech Stack:** FastMCP 1.11.0, Python 3.10+, httpx, Pydantic, pytest  
**Package Manager:** uv  
**Deployment:** VS Code MCP integration ready

## Code Generation Guidelines

- **Security First:** Never expose PATs or secrets in logs, always use environment variables
- **Type Safety:** Use full type hints with Pydantic models for all data structures
- **Async Patterns:** Use async/await throughout, avoid blocking operations
- **Error Handling:** Wrap Azure DevOps API calls with proper exception handling
- **Performance:** Use httpx async client with connection pooling for API calls

## Code Style and Structure

- **Line Length:** 100 characters maximum (black formatter)
- **Import Order:** Use isort profile "black" with trailing commas
- **Type Checking:** Follow mypy strict mode requirements
- **Docstrings:** Use Google-style docstrings for all public functions
- **Architecture:** Maintain layered architecture: FastMCP → Services → Client → Azure DevOps API

## Naming Conventions

- **Files:** Use snake_case (e.g., `variable_group_service.py`)
- **Classes:** Use PascalCase with domain context (e.g., `VariableGroupService`, `ServiceConnectionClient`)
- **Functions:** Use snake_case with action verbs (e.g., `list_variable_groups`, `get_service_connection_details`)
- **Constants:** Use UPPER_SNAKE_CASE (e.g., `DEFAULT_API_VERSION`, `MAX_RETRIES`)
- **Models:** Match Azure DevOps terminology (e.g., `VariableGroup`, `ServiceConnection`)

## Testing Standards

- **Framework:** pytest with pytest-asyncio for async tests
- **Coverage:** Aim for >80% coverage on critical paths
- **Mocking:** Use pytest-mock for Azure DevOps API responses
- **Structure:** Mirror src/ structure in tests/ directory
- **Naming:** Prefix test functions with `test_` and use descriptive names

## Version Control Standards

- **Commits:** Use conventional commits (feat:, fix:, docs:, test:, refactor:)
- **Branches:** Use feature/ prefix for new features, fix/ for bug fixes
- **PRs:** Include tests and update documentation for new tools

## Package Management

- **Primary:** Use `uv pip install -e .` for development setup
- **Dependencies:** Add to pyproject.toml [project.dependencies] section
- **Dev Dependencies:** Add to [project.optional-dependencies.dev] section
- **Lock File:** Commit uv.lock for reproducible builds

## MCP Tool Development

- **Decorators:** Use `@mcp.tool()` for FastMCP tool registration
- **Return Types:** Return `Dict[str, Any]` with keys: success, data, message, error
- **Input Validation:** Use Pydantic models or typed parameters for validation
- **Documentation:** Include clear docstrings with Args and Returns sections
- **Error Responses:** Standardize error format with success=False and error message

## Azure DevOps Integration

- **Authentication:** Use PAT stored in AZURE_DEVOPS_PAT environment variable
- **API Version:** Use azure-devops>=7.0.0 SDK when possible, fallback to REST API
- **Rate Limiting:** Implement retry logic with exponential backoff
- **Organization:** Use AZURE_DEVOPS_ORGANIZATION environment variable
- **Projects:** Support both project names and GUIDs as parameters

## Security Requirements

- **Secrets:** Never log or return secret values from variable groups
- **PATs:** Store in environment variables, never in code or logs
- **Input Sanitization:** Validate all user inputs before Azure DevOps API calls
- **Error Messages:** Sanitize error responses to avoid information disclosure
- **Audit:** Log all operations with correlation IDs for security auditing

## Development Workflow
- **Environment:** Use `uv` for virtual environment management
- **use context7**: to check documentation and context
- **use `uv`** to install dependencies example commands:
  - `uv add <package>` for adding packages
  - `uv remove <package>` for removing packages
- **Setup:** Run `uv python setup_dev.py` for initial environment setup
- **Testing:** Use `uv pytest` for running tests, `uv pytest --cov=src` for coverage
- **Quality:** Run `uv pre-commit run --all-files` before committing
- **Local Server:** Use `mcp-ado-server` command to test MCP integration locally

## Performance Standards

- **Async Operations:** Use httpx async client for all Azure DevOps API calls
- **Connection Pooling:** Reuse HTTP connections via client singleton pattern
- **Response Time:** Target <2s for variable group/service connection operations
- **Memory Usage:** Use streaming for large responses when possible
- **Caching:** Consider implementing Redis caching for frequently accessed data
