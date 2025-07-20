#!/usr/bin/env python3
"""Debug script to test the failing security tests."""

import logging
from src.mcp_ado_server.security import SecurityFilter, SecureLogger, get_secure_logger

def test_none_filtering():
    """Test the None value filtering issue."""
    print("=== Testing None value filtering ===")
    data = {"key1": None, "password": None, "key3": "value"}
    filtered = SecurityFilter.filter_sensitive_dict(data)
    
    print(f"Input: {data}")
    print(f"Output: {filtered}")
    print(f"password value: {repr(filtered['password'])}")
    print(f"Expected '[FILTERED]', Got: {repr(filtered['password'])}")
    
    # Test assertion
    try:
        assert filtered["password"] == "[FILTERED]"
        print("✅ test_filter_none_values should PASS")
    except AssertionError as e:
        print(f"❌ test_filter_none_values should FAIL: {e}")

def test_debug_request_logging():
    """Test the debug request logging issue."""
    print("\n=== Testing debug request logging ===")
    
    # Set up logging to capture output
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    logger = logging.getLogger("test_debug")
    logger.setLevel(logging.DEBUG)
    
    # Create a list to capture log messages
    log_messages = []
    
    # Create a custom handler to capture messages
    class ListHandler(logging.Handler):
        def emit(self, record):
            log_messages.append(record.getMessage())
    
    handler = ListHandler()
    logger.addHandler(handler)
    
    secure_logger = SecureLogger(logger)
    
    # Test the debug_request call
    secure_logger.debug_request(
        method="POST",
        url="https://api.example.com/test?api_key=secret123",
        params={"project": "test", "token": "secret"},
        correlation_id="test123"
    )
    
    if log_messages:
        log_message = log_messages[0]
        print(f"Log message: {log_message}")
        
        # Check assertions
        checks = [
            ("[test123]" in log_message, "[test123] should be in message"),
            ("HTTP Request:" in log_message, "HTTP Request: should be in message"),
            ("api_key=[FILTERED]" in log_message, "api_key=[FILTERED] should be in message"),
            ("token=[FILTERED]" in log_message, "token=[FILTERED] should be in message"),
            ("project=test" in log_message or "'project': 'test'" in log_message, "project=test should be in message")
        ]
        
        for check, description in checks:
            if check:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                
        # Overall result
        if all(check for check, _ in checks):
            print("✅ test_debug_request_logging should PASS")
        else:
            print("❌ test_debug_request_logging should FAIL")
    else:
        print("❌ No log messages captured!")

if __name__ == "__main__":
    test_none_filtering()
    test_debug_request_logging()
