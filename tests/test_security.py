"""
Tests for security functionality.
"""

import logging

import pytest

from mcp_ado_server.security import (
    SecureLogger,
    SecurityFilter,
    create_correlation_id,
    get_secure_logger,
)


class TestSecurityFilter:
    """Test cases for SecurityFilter class."""

    def test_is_sensitive_key(self):
        """Test sensitive key detection."""
        # Sensitive keys
        assert SecurityFilter.is_sensitive_key("password")
        assert SecurityFilter.is_sensitive_key("SECRET_KEY")
        assert SecurityFilter.is_sensitive_key("api-token")
        assert SecurityFilter.is_sensitive_key("Azure_DevOps_PAT")
        assert SecurityFilter.is_sensitive_key("Authorization")
        assert SecurityFilter.is_sensitive_key("client_secret")

        # Non-sensitive keys
        assert not SecurityFilter.is_sensitive_key("username")
        assert not SecurityFilter.is_sensitive_key("project_name")
        assert not SecurityFilter.is_sensitive_key("url")
        assert not SecurityFilter.is_sensitive_key("description")
        assert not SecurityFilter.is_sensitive_key("")

    def test_is_sensitive_value(self):
        """Test sensitive value detection."""
        # Sensitive values (patterns that look like secrets)
        assert SecurityFilter.is_sensitive_value(
            "abcdef123456789012345678901234567890123456789012"
        )  # 52 chars
        assert SecurityFilter.is_sensitive_value("12345678-1234-1234-1234-123456789012")  # GUID

        # Non-sensitive values
        assert not SecurityFilter.is_sensitive_value("short")
        assert not SecurityFilter.is_sensitive_value("normal text value")
        assert not SecurityFilter.is_sensitive_value("https://example.com")
        assert not SecurityFilter.is_sensitive_value("")
        assert not SecurityFilter.is_sensitive_value(None)  # type: ignore

    def test_filter_sensitive_dict_by_key(self):
        """Test dictionary filtering by key names."""
        data = {
            "username": "john.doe",
            "password": "secret123",
            "api_token": "abc123def456",
            "project_name": "MyProject",
            "secret_key": "very-secret-value",
        }

        filtered = SecurityFilter.filter_sensitive_dict(data)

        assert filtered["username"] == "john.doe"
        assert filtered["password"] == "[FILTERED]"
        assert filtered["api_token"] == "[FILTERED]"
        assert filtered["project_name"] == "MyProject"
        assert filtered["secret_key"] == "[FILTERED]"

    def test_filter_sensitive_dict_nested(self):
        """Test nested dictionary filtering."""
        data = {
            "config": {
                "username": "john.doe",
                "password": "secret123",
                "nested": {"api_key": "abc123"},
            },
            "metadata": {"version": "1.0", "secret": "hidden"},
        }

        filtered = SecurityFilter.filter_sensitive_dict(data, deep_scan=True)

        assert filtered["config"]["username"] == "john.doe"
        assert filtered["config"]["password"] == "[FILTERED]"
        assert filtered["config"]["nested"]["api_key"] == "[FILTERED]"
        assert filtered["metadata"]["version"] == "1.0"
        assert filtered["metadata"]["secret"] == "[FILTERED]"

    def test_filter_sensitive_dict_custom_replacement(self):
        """Test custom replacement string."""
        data = {"password": "secret123", "username": "john"}
        filtered = SecurityFilter.filter_sensitive_dict(data, replacement="***HIDDEN***")

        assert filtered["password"] == "***HIDDEN***"
        assert filtered["username"] == "john"

    def test_filter_sensitive_dict_with_lists(self):
        """Test filtering dictionaries within lists."""
        data = {
            "items": [
                {"name": "item1", "secret": "secret1"},
                {"name": "item2", "api_key": "key123"},
            ],
            "metadata": {"version": "1.0"},
        }

        filtered = SecurityFilter.filter_sensitive_dict(data, deep_scan=True)

        assert filtered["items"][0]["name"] == "item1"
        assert filtered["items"][0]["secret"] == "[FILTERED]"
        assert filtered["items"][1]["name"] == "item2"
        assert filtered["items"][1]["api_key"] == "[FILTERED]"
        assert filtered["metadata"]["version"] == "1.0"

    def test_filter_url_params(self):
        """Test URL parameter filtering."""
        # URL with sensitive parameters
        url = "https://api.example.com/data?username=john&api_key=secret123&project=test"
        filtered = SecurityFilter.filter_url_params(url)
        expected = "https://api.example.com/data?username=john&api_key=[FILTERED]&project=test"
        assert filtered == expected

        # URL without parameters
        simple_url = "https://api.example.com/data"
        assert SecurityFilter.filter_url_params(simple_url) == simple_url

        # URL with no sensitive parameters
        safe_url = "https://api.example.com/data?username=john&project=test"
        assert SecurityFilter.filter_url_params(safe_url) == safe_url

    def test_sanitize_for_logging(self):
        """Test complete request sanitization."""
        params = {"project": "test", "api_key": "secret123"}
        headers = {"Authorization": "Bearer token123", "Content-Type": "application/json"}
        json_data = {"username": "john", "password": "secret"}

        sanitized = SecurityFilter.sanitize_for_logging(
            method="POST",
            url="https://api.example.com/data?token=abc123",
            params=params,
            headers=headers,
            json_data=json_data,
        )

        assert sanitized["method"] == "POST"
        assert sanitized["url"] == "https://api.example.com/data?token=[FILTERED]"
        assert sanitized["params"]["project"] == "test"
        assert sanitized["params"]["api_key"] == "[FILTERED]"
        assert sanitized["headers"]["Authorization"] == "[REDACTED]"
        assert sanitized["headers"]["Content-Type"] == "application/json"
        assert sanitized["json_data"]["username"] == "john"
        assert sanitized["json_data"]["password"] == "[FILTERED]"


class TestSecureLogger:
    """Test cases for SecureLogger class."""

    def test_secure_logger_creation(self):
        """Test secure logger instantiation."""
        logger = logging.getLogger("test")
        secure_logger = SecureLogger(logger)
        assert secure_logger.logger == logger
        assert isinstance(secure_logger.security_filter, SecurityFilter)

    def test_get_secure_logger(self):
        """Test get_secure_logger function."""
        secure_logger = get_secure_logger("test_module")
        assert isinstance(secure_logger, SecureLogger)
        assert secure_logger.logger.name == "test_module"

    def test_create_correlation_id(self):
        """Test correlation ID creation."""
        correlation_id = create_correlation_id()
        assert isinstance(correlation_id, str)
        assert len(correlation_id) == 8

        # Ensure different calls return different IDs
        another_id = create_correlation_id()
        assert correlation_id != another_id


class TestSecureLoggerIntegration:
    """Integration tests for SecureLogger with actual logging."""

    def test_debug_request_logging(self, caplog):
        """Test debug request logging with filtering."""
        logger = logging.getLogger("test_debug")
        logger.setLevel(logging.DEBUG)
        secure_logger = SecureLogger(logger)

        with caplog.at_level(logging.DEBUG):
            secure_logger.debug_request(
                method="POST",
                url="https://api.example.com/test?api_key=secret123",
                params={"project": "test", "token": "secret"},
                correlation_id="test123",
            )

        log_message = caplog.records[0].message
        assert "[test123]" in log_message
        assert "HTTP Request:" in log_message
        assert "api_key=[FILTERED]" in log_message
        assert "token=[FILTERED]" in log_message
        assert "project=test" in log_message or "'project': 'test'" in log_message

    def test_security_event_logging(self, caplog):
        """Test security event logging."""
        logger = logging.getLogger("test_security")
        logger.setLevel(logging.INFO)
        secure_logger = SecureLogger(logger)

        with caplog.at_level(logging.INFO):
            secure_logger.security_event(
                event_type="AUTHENTICATION_FAILURE",
                description="Invalid credentials",
                correlation_id="sec123",
                username="john",
                password="secret123",
            )

        log_message = caplog.records[0].message
        assert "[sec123]" in log_message
        assert "SECURITY_EVENT: AUTHENTICATION_FAILURE" in log_message
        assert "Invalid credentials" in log_message
        assert "password=[FILTERED]" in log_message or "'password': '[FILTERED]'" in log_message

    def test_error_with_context_logging(self, caplog):
        """Test error logging with context filtering."""
        logger = logging.getLogger("test_error")
        logger.setLevel(logging.ERROR)
        secure_logger = SecureLogger(logger)

        test_error = ValueError("Test error")

        with caplog.at_level(logging.ERROR):
            secure_logger.error_with_context(
                message="Operation failed",
                error=test_error,
                correlation_id="err123",
                api_key="secret123",
                project="test_project",
            )

        log_message = caplog.records[0].message
        assert "[err123]" in log_message
        assert "Error: Operation failed" in log_message
        assert "ValueError: Test error" in log_message
        assert "api_key=[FILTERED]" in log_message or "'api_key': '[FILTERED]'" in log_message
        assert "project=test_project" in log_message or "'project': 'test_project'" in log_message


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_filter_none_values(self):
        """Test handling of None values."""
        data = {"key1": None, "password": None, "key3": "value"}
        filtered = SecurityFilter.filter_sensitive_dict(data)

        assert filtered["key1"] is None
        assert filtered["password"] == "[FILTERED]"  # Still filtered even if None
        assert filtered["key3"] == "value"

    def test_filter_empty_dict(self):
        """Test filtering empty dictionary."""
        filtered = SecurityFilter.filter_sensitive_dict({})
        assert filtered == {}

    def test_filter_non_dict_input(self):
        """Test filtering non-dictionary input."""
        result = SecurityFilter.filter_sensitive_dict("not a dict")  # type: ignore
        assert result == "not a dict"

    def test_url_filter_edge_cases(self):
        """Test URL filtering edge cases."""
        # URL with parameter but no value
        url1 = "https://example.com?api_key="
        filtered1 = SecurityFilter.filter_url_params(url1)
        assert filtered1 == "https://example.com?api_key=[FILTERED]"

        # URL with parameter but no equals sign
        url2 = "https://example.com?standalone_param"
        filtered2 = SecurityFilter.filter_url_params(url2)
        assert filtered2 == url2  # Should remain unchanged

    def test_deep_scan_disabled(self):
        """Test filtering with deep scan disabled."""
        data = {"password": "secret1", "nested": {"api_key": "secret2"}}

        filtered = SecurityFilter.filter_sensitive_dict(data, deep_scan=False)
        assert filtered["password"] == "[FILTERED]"
        assert filtered["nested"]["api_key"] == "secret2"  # Should not be filtered
