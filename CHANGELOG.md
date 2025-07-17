# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-07-17

### ⚠️ BREAKING CHANGES

- Server now uses FastMCP 1.11.0 architecture instead of legacy Server class
- Service layer returns `Dict[str, Any]` instead of `MCPToolResult` objects

### Added

- FastMCP 1.11.0 architecture with `@mcp.tool()` decorators
- Automatic client initialization (no manual async context manager required)
- Comprehensive integration tests for FastMCP tools
- Git conventional commits configuration
- Migration completion documentation

### Changed

- Upgraded MCP dependency from 0.1.0 to 1.11.0
- Migrated from legacy Server class to FastMCP decorator-based approach
- Converted service layer to return dictionaries instead of custom objects
- Updated main entry point to use FastMCP server

### Fixed

- "Client not initialized" error with automatic client lifecycle management
- Service layer compatibility with FastMCP expectations
- All tools now properly handle dictionary responses

### Technical

- **Coverage**: 60% overall with 40/40 tests passing
- **Architecture**: Clean separation of FastMCP tools, service layer, and client
- **Error Handling**: Robust error propagation from Azure DevOps API to tools
- **Type Safety**: Full Pydantic model validation throughout

## [1.0.0] - 2025-07-17

### Added

- Initial MCP Server implementation for Azure DevOps
- Support for listing and retrieving variable groups
- Support for listing and retrieving service connections
- Azure DevOps REST API client with PAT authentication
- Comprehensive test suite with pytest
- Pre-commit hooks for code quality
- VS Code MCP integration documentation
- Docker and development environment setup

### Technical Foundation

- Python 3.10+ with uv package manager
- Async/await patterns throughout
- Layered architecture with dependency injection
- Type safety with Pydantic models
- Structured logging with structlog
