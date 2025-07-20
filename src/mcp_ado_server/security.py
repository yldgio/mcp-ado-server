"""
Security utilities for MCP Azure DevOps Server.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class SecurityFilter:
    """Security utilities for filtering sensitive data from logs and responses."""

    # Common patterns that indicate sensitive data
    SENSITIVE_PATTERNS = [
        "password",
        "secret",
        "token",
        "apikey",
        "api_key", 
        "accesskey",
        "access_key",
        "secretkey",
        "secret_key",
        "credential",
        "auth",
        "bearer",
        "authorization",
        "pat",
        "client_secret",
        "client_id",
        "tenant_id",
    ]

    # Regex patterns for common secret formats
    SECRET_REGEXES = [
        # Azure PAT pattern (base64-like, 52 chars)
        re.compile(r"[A-Za-z0-9+/]{52}"),
        # GitHub token pattern
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,251}"),
        # Generic API key pattern (alphanumeric, 20+ chars)
        re.compile(r"[A-Za-z0-9]{20,}"),
        # GUID pattern
        re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"),
    ]

    @classmethod
    def is_sensitive_key(cls, key: str) -> bool:
        """Check if a key name indicates sensitive data."""
        if not key:
            return False
        
        key_lower = key.lower().replace("_", "").replace("-", "")
        
        # Check for exact matches first
        if key_lower in cls.SENSITIVE_PATTERNS:
            return True
            
        # Check for patterns that should match as substrings
        substring_patterns = ["password", "secret", "token", "credential", "auth", "bearer", "authorization", "pat"]
        for pattern in substring_patterns:
            if pattern in key_lower:
                return True
                
        # Check for specific API key patterns
        api_key_patterns = ["apikey", "accesskey", "secretkey", "clientsecret", "clientid", "tenantid"]
        for pattern in api_key_patterns:
            if pattern == key_lower:
                return True
                
        return False

    @classmethod
    def is_sensitive_value(cls, value: str) -> bool:
        """Check if a value matches common secret patterns."""
        if not isinstance(value, str) or len(value) < 10:
            return False
        
        # Check against known secret patterns
        for pattern in cls.SECRET_REGEXES:
            if pattern.fullmatch(value):
                return True
        
        return False

    @classmethod
    def filter_sensitive_dict(
        cls, 
        data: Dict[str, Any], 
        replacement: str = "[FILTERED]",
        deep_scan: bool = True
    ) -> Dict[str, Any]:
        """Filter sensitive data from dictionary."""
        if not isinstance(data, dict):
            return data

        filtered = {}
        for key, value in data.items():
            # Check if key indicates sensitive data
            if cls.is_sensitive_key(key):
                filtered[key] = replacement
            elif isinstance(value, dict) and deep_scan:
                # Recursively filter nested dictionaries
                filtered[key] = cls.filter_sensitive_dict(value, replacement, deep_scan)
            elif isinstance(value, list) and deep_scan:
                # Filter lists that might contain dictionaries
                filtered[key] = [
                    cls.filter_sensitive_dict(item, replacement, deep_scan) 
                    if isinstance(item, dict) else item
                    for item in value
                ]
            elif isinstance(value, str) and deep_scan and cls.is_sensitive_value(value):
                # Check if value looks like a secret
                filtered[key] = replacement
            else:
                filtered[key] = value

        return filtered

    @classmethod
    def filter_url_params(cls, url: str, replacement: str = "[FILTERED]") -> str:
        """Filter sensitive data from URL parameters."""
        if "?" not in url:
            return url
        
        base_url, query_string = url.split("?", 1)
        params = []
        
        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                if cls.is_sensitive_key(key):
                    params.append(f"{key}={replacement}")
                else:
                    params.append(param)
            else:
                params.append(param)
        
        return f"{base_url}?{'&'.join(params)}"

    @classmethod
    def sanitize_for_logging(
        cls, 
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Sanitize request data for safe logging."""
        sanitized: Dict[str, Any] = {
            "method": method,
            "url": cls.filter_url_params(url),
        }
        
        if params:
            sanitized["params"] = cls.filter_sensitive_dict(params)
        
        if headers:
            # Always filter headers as they often contain auth tokens
            sanitized["headers"] = cls.filter_sensitive_dict(headers, "[REDACTED]")
        
        if json_data:
            sanitized["json_data"] = cls.filter_sensitive_dict(json_data)
        
        return sanitized


class SecureLogger:
    """Secure logging wrapper that automatically filters sensitive data."""
    
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance
        self.security_filter = SecurityFilter()

    def debug_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log HTTP request with security filtering."""
        sanitized = SecurityFilter.sanitize_for_logging(
            method, url, params, headers, json_data
        )
        
        # Format the log message in a more readable way for debugging
        parts = []
        parts.append(f"method={sanitized['method']}")
        parts.append(f"url={sanitized['url']}")
        
        if 'params' in sanitized:
            param_strs = [f"{k}={v}" for k, v in sanitized['params'].items()]
            parts.append(f"params=({', '.join(param_strs)})")
            
        if 'headers' in sanitized:
            header_strs = [f"{k}={v}" for k, v in sanitized['headers'].items()]
            parts.append(f"headers=({', '.join(header_strs)})")
            
        if 'json_data' in sanitized:
            json_strs = [f"{k}={v}" for k, v in sanitized['json_data'].items()]
            parts.append(f"json_data=({', '.join(json_strs)})")
        
        log_message = f"HTTP Request: {', '.join(parts)}"
        if correlation_id:
            log_message = f"[{correlation_id}] {log_message}"
            
        self.logger.debug(log_message)

    def debug_response(
        self,
        status_code: int,
        response_size: int,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log HTTP response with security context."""
        log_message = f"HTTP Response: status={status_code}, size={response_size}bytes"
        if correlation_id:
            log_message = f"[{correlation_id}] {log_message}"
            
        self.logger.debug(log_message)

    def error_with_context(
        self,
        message: str,
        error: Exception,
        correlation_id: Optional[str] = None,
        **context
    ) -> None:
        """Log error with filtered context."""
        filtered_context = SecurityFilter.filter_sensitive_dict(context)
        
        log_message = f"Error: {message} - {type(error).__name__}: {str(error)}"
        if filtered_context:
            log_message += f" | Context: {filtered_context}"
        if correlation_id:
            log_message = f"[{correlation_id}] {log_message}"
            
        self.logger.error(log_message)

    def info_with_context(
        self,
        message: str,
        correlation_id: Optional[str] = None,
        **context
    ) -> None:
        """Log info with filtered context."""
        filtered_context = SecurityFilter.filter_sensitive_dict(context)
        
        log_message = message
        if filtered_context:
            log_message += f" | Context: {filtered_context}"
        if correlation_id:
            log_message = f"[{correlation_id}] {log_message}"
            
        self.logger.info(log_message)

    def security_event(
        self,
        event_type: str,
        description: str,
        severity: str = "INFO",
        correlation_id: Optional[str] = None,
        **context
    ) -> None:
        """Log security-relevant events."""
        filtered_context = SecurityFilter.filter_sensitive_dict(context)
        
        log_message = f"SECURITY_EVENT: {event_type} | {description}"
        if filtered_context:
            log_message += f" | Context: {filtered_context}"
        if correlation_id:
            log_message = f"[{correlation_id}] {log_message}"
        
        # Log at appropriate level based on severity
        if severity.upper() == "ERROR":
            self.logger.error(log_message)
        elif severity.upper() == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)


def create_correlation_id() -> str:
    """Create a unique correlation ID for request tracing."""
    import uuid
    return str(uuid.uuid4())[:8]


def get_secure_logger(name: str) -> SecureLogger:
    """Get a secure logger instance for the specified module."""
    return SecureLogger(logging.getLogger(name))
