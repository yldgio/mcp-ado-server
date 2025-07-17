"""
Tests for the configuration module.
"""

import os
import pytest
from unittest.mock import patch

from mcp_ado_server.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_from_env_with_required_vars(self):
        """Test creating config from environment variables."""
        with patch.dict(os.environ, {
            'AZURE_DEVOPS_ORGANIZATION': 'test-org',
            'AZURE_DEVOPS_PAT': 'test-pat'
        }):
            config = Config.from_env()
            assert config.organization == 'test-org'
            assert config.personal_access_token == 'test-pat'
            assert config.api_version == '7.0'
    
    def test_from_env_missing_organization(self):
        """Test error when organization is missing."""
        with patch.dict(os.environ, {
            'AZURE_DEVOPS_PAT': 'test-pat'
        }, clear=True):
            with pytest.raises(ValueError, match="AZURE_DEVOPS_ORGANIZATION"):
                Config.from_env()
    
    def test_from_env_missing_pat(self):
        """Test error when PAT is missing."""
        with patch.dict(os.environ, {
            'AZURE_DEVOPS_ORGANIZATION': 'test-org'
        }, clear=True):
            with pytest.raises(ValueError, match="AZURE_DEVOPS_PAT"):
                Config.from_env()
    
    def test_from_env_with_optional_vars(self):
        """Test creating config with optional environment variables."""
        with patch.dict(os.environ, {
            'AZURE_DEVOPS_ORGANIZATION': 'test-org',
            'AZURE_DEVOPS_PAT': 'test-pat',
            'API_VERSION': '6.0',
            'LOG_LEVEL': 'DEBUG',
            'REQUEST_TIMEOUT': '60',
            'MAX_RETRIES': '5',
            'CACHE_TTL_SECONDS': '600',
            'ENABLE_CACHING': 'false'
        }):
            config = Config.from_env()
            assert config.api_version == '6.0'
            assert config.log_level == 'DEBUG'
            assert config.request_timeout == 60
            assert config.max_retries == 5
            assert config.cache_ttl_seconds == 600
            assert config.enable_caching is False
    
    def test_base_url_property(self):
        """Test base URL property."""
        config = Config(
            organization='test-org',
            personal_access_token='test-pat'
        )
        assert config.base_url == 'https://dev.azure.com/test-org'
    
    def test_api_url_property(self):
        """Test API URL property."""
        config = Config(
            organization='test-org',
            personal_access_token='test-pat'
        )
        assert config.api_url == 'https://dev.azure.com/test-org/_apis'
    
    def test_validate_success(self):
        """Test successful validation."""
        config = Config(
            organization='test-org',
            personal_access_token='test-pat'
        )
        config.validate()  # Should not raise
    
    def test_validate_missing_organization(self):
        """Test validation error for missing organization."""
        config = Config(
            organization='',
            personal_access_token='test-pat'
        )
        with pytest.raises(ValueError, match="Organization is required"):
            config.validate()
    
    def test_validate_missing_pat(self):
        """Test validation error for missing PAT."""
        config = Config(
            organization='test-org',
            personal_access_token=''
        )
        with pytest.raises(ValueError, match="Personal Access Token is required"):
            config.validate()
    
    def test_validate_invalid_timeout(self):
        """Test validation error for invalid timeout."""
        config = Config(
            organization='test-org',
            personal_access_token='test-pat',
            request_timeout=0
        )
        with pytest.raises(ValueError, match="Request timeout must be positive"):
            config.validate()
    
    def test_validate_invalid_retries(self):
        """Test validation error for invalid retries."""
        config = Config(
            organization='test-org',
            personal_access_token='test-pat',
            max_retries=-1
        )
        with pytest.raises(ValueError, match="Max retries must be non-negative"):
            config.validate()
    
    def test_validate_invalid_cache_ttl(self):
        """Test validation error for invalid cache TTL."""
        config = Config(
            organization='test-org',
            personal_access_token='test-pat',
            cache_ttl_seconds=-1
        )
        with pytest.raises(ValueError, match="Cache TTL must be non-negative"):
            config.validate()
