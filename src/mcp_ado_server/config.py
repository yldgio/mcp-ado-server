"""
Configuration management for MCP Azure DevOps Server.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration for the MCP Azure DevOps Server."""

    # Azure DevOps Configuration
    organization: str
    personal_access_token: str
    api_version: str = "7.0"

    # Server Configuration
    log_level: str = "INFO"
    log_format: str = "json"

    # HTTP Client Configuration
    request_timeout: int = 30
    max_retries: int = 3

    # Cache Configuration
    cache_ttl_seconds: int = 300
    enable_caching: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        organization = os.getenv("AZURE_DEVOPS_ORGANIZATION")
        if not organization:
            raise ValueError("AZURE_DEVOPS_ORGANIZATION environment variable is required")

        pat = os.getenv("AZURE_DEVOPS_PAT")
        if not pat:
            raise ValueError("AZURE_DEVOPS_PAT environment variable is required")

        return cls(
            organization=organization,
            personal_access_token=pat,
            api_version=os.getenv("API_VERSION", "7.0"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
        )

    @property
    def base_url(self) -> str:
        """Get the base URL for Azure DevOps API."""
        return f"https://dev.azure.com/{self.organization}"

    @property
    def api_url(self) -> str:
        """Get the organization-level API URL for Azure DevOps."""
        return f"{self.base_url}/_apis"

    def project_api_url(self, project: str) -> str:
        """Get the project-specific API URL for Azure DevOps.

        Args:
            project: Project name or ID

        Returns:
            Project-specific API URL in format: https://dev.azure.com/{organization}/{project}/_apis
        """
        return f"{self.base_url}/{project}/_apis"

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.organization:
            raise ValueError("Organization is required")

        if not self.personal_access_token:
            raise ValueError("Personal Access Token is required")

        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")

        if self.cache_ttl_seconds < 0:
            raise ValueError("Cache TTL must be non-negative")
