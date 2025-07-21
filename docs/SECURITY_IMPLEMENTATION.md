# Security Implementation Guide

This document describes the comprehensive security enhancements implemented in the MCP Azure DevOps Server to address logging security issues and implement parameter filtering for debug logs.

## 🛡️ Security Enhancements Overview

### 1. **SecurityFilter Class**
Advanced filtering system that automatically detects and redacts sensitive information from logs, responses, and debug output.

### 2. **SecureLogger Class**
Drop-in replacement for standard logging that provides automatic security filtering with correlation ID support.

### 3. **Parameter Filtering**
Comprehensive filtering of HTTP request parameters, headers, and JSON payloads before logging.

### 4. **Security Validation Script**
Automated scanning tool to detect potential secrets and security vulnerabilities in the codebase.

## 🔧 Implementation Details

### Security Filter Features

#### **Sensitive Key Detection**
```python
# Automatically detects sensitive keys by name patterns
sensitive_patterns = [
    "password", "secret", "token", "key", "credential",
    "auth", "bearer", "api-key", "authorization", "pat"
]
```

#### **Value Pattern Matching**
```python
# Detects values that look like secrets
patterns = [
    # Azure PAT pattern (52 chars base64)
    r"[A-Za-z0-9+/]{52}",
    # GitHub tokens
    r"gh[pousr]_[A-Za-z0-9_]{36,251}",
    # GUIDs
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
]
```

#### **Deep Dictionary Scanning**
- Recursively filters nested dictionaries
- Handles lists containing dictionaries
- Configurable replacement strings
- Optional deep scanning control

### Secure Logging Features

#### **Request Logging with Filtering**
```python
secure_logger.debug_request(
    method="POST",
    url="https://api.example.com/data?api_key=secret123",
    params={"project": "test", "token": "secret"},
    correlation_id="abc123"
)
# Output: [abc123] HTTP Request: {'method': 'POST', 'url': 'https://api.example.com/data?api_key=[FILTERED]', 'params': {'project': 'test', 'token': '[FILTERED]'}}
```

#### **Security Event Logging**
```python
secure_logger.security_event(
    event_type="AUTHENTICATION_FAILURE",
    description="Invalid credentials",
    severity="WARNING",
    username="john",
    password="secret123"
)
# Output: SECURITY_EVENT: AUTHENTICATION_FAILURE | Invalid credentials | Context: {'username': 'john', 'password': '[FILTERED]'}
```

#### **Correlation ID Support**
- Unique 8-character correlation IDs for request tracing
- Automatic correlation ID generation
- Consistent correlation ID propagation across log entries

## 🚀 Usage Examples

### Basic Usage

```python
from mcp_ado_server.security import get_secure_logger, create_correlation_id

# Get secure logger for your module
secure_logger = get_secure_logger(__name__)
correlation_id = create_correlation_id()

# Safe HTTP request logging
secure_logger.debug_request(
    method="GET",
    url="https://dev.azure.com/org/project/_apis/distributedtask/variablegroups",
    params={"api-version": "7.0", "groupName": "secrets"},
    headers={"Authorization": "Basic abc123=="},
    correlation_id=correlation_id
)

# Error logging with context
try:
    # ... some operation
    pass
except Exception as e:
    secure_logger.error_with_context(
        message="Operation failed",
        error=e,
        correlation_id=correlation_id,
        project="myproject",
        api_key="secret123"  # This will be filtered out
    )

# Security event logging
secure_logger.security_event(
    event_type="VARIABLE_GROUP_ACCESS",
    description="Variable group accessed",
    correlation_id=correlation_id,
    group_name="production-secrets"
)
```

### Advanced Filtering

```python
from mcp_ado_server.security import SecurityFilter

# Custom filtering
data = {
    "username": "john.doe",
    "password": "secret123",
    "project": {
        "name": "myproject",
        "api_key": "abc123def456"
    }
}

# Filter with custom replacement
filtered = SecurityFilter.filter_sensitive_dict(
    data,
    replacement="***REDACTED***",
    deep_scan=True
)
# Result: {'username': 'john.doe', 'password': '***REDACTED***', 'project': {'name': 'myproject', 'api_key': '***REDACTED***'}}

# URL parameter filtering
unsafe_url = "https://api.example.com/data?username=john&api_key=secret123&project=test"
safe_url = SecurityFilter.filter_url_params(unsafe_url)
# Result: "https://api.example.com/data?username=john&api_key=[FILTERED]&project=test"
```

## 🔍 Security Validation

### Running Security Scans

The included security scanner checks for:
- Hardcoded secrets and credentials
- Insecure file permissions
- Missing .gitignore entries
- Environment file security
- Dependency vulnerabilities

```bash
# Run basic security scan
python scripts/security_scan.py

# Scan specific path with JSON output
python scripts/security_scan.py --path /path/to/project --json

# Fail CI/CD on high-severity issues
python scripts/security_scan.py --fail-on-high
```

### Security Scan Output Example

```
🔍 Starting security scan of /project/path
📁 Scanning files for potential secrets...
🌐 Checking environment file security...
📋 Checking .gitignore configuration...
🔒 Checking file permissions...
📦 Checking dependencies for vulnerabilities...

============================================================
🛡️  SECURITY SCAN REPORT
============================================================

📊 SUMMARY:
   Total issues found: 0
   🔴 High severity: 0
   🟡 Medium severity: 0
   🟠 Low severity: 0
   ℹ️  Informational: 2

============================================================
🎯 OVERALL ASSESSMENT:
✅ GOOD: No critical security issues found
```

## 📋 Integration Checklist

### ✅ **Pre-Implementation Checklist**
- [x] Install security dependencies
- [x] Create security filter module
- [x] Implement secure logger
- [x] Create comprehensive tests
- [x] Update client code to use secure logging
- [x] Update service code to use secure logging

### ✅ **Post-Implementation Validation**
- [x] Run security scan to verify no secrets in code
- [x] Test logging with sensitive data
- [x] Verify correlation ID generation
- [x] Test security event logging
- [x] Validate filtering accuracy

## 🚨 Security Considerations

### **What Gets Filtered**

**Automatically Filtered Keys:**
- `password`, `secret`, `token`, `key`, `credential`
- `auth`, `bearer`, `api-key`, `authorization`
- `pat`, `client_secret`, `tenant_id`

**Automatically Filtered Values:**
- 52-character base64 strings (Azure PAT format)
- GitHub tokens (`gh*_...`)
- Long alphanumeric strings (20+ chars)
- GUID patterns

### **What Doesn't Get Filtered**
- Short values (< 10 characters)
- Common words and phrases
- Placeholder values (`your-token`, `example-key`)
- Non-sensitive configuration values

### **Configuration Options**
- Custom replacement strings
- Deep scanning on/off
- Custom sensitive patterns
- Severity levels for security events

## 🔧 Maintenance

### **Regular Tasks**
1. **Update Patterns**: Review and update secret detection patterns quarterly
2. **Security Scans**: Run automated security scans in CI/CD pipeline
3. **Log Review**: Periodically review logs to ensure no sensitive data leakage
4. **Dependency Updates**: Keep security dependencies updated

### **Monitoring**
- Watch for security events in logs
- Monitor correlation IDs for request tracing
- Set up alerts for authentication/authorization failures

## 📖 Related Documentation
- [Security Analysis Report](../SECURITY_ANALYSIS.md)
- [API Documentation](API.md)
- [Testing Guide](../tests/README.md)
- [Deployment Security](DEPLOYMENT_SECURITY.md)
