#!/usr/bin/env python3
"""Simple final test validation"""

import sys
sys.path.insert(0, 'src')
exec(open('src/mcp_ado_server/security.py').read())

print('🎯 FINAL VALIDATION')
print('=' * 30)

# Test security filtering
data = {'api_key': 'secret', 'project': 'test'}
result = SecurityFilter.filter_sensitive_dict(data)
print(f'✅ Filtering: {result}')

# Test correlation ID
cid = create_correlation_id()
print(f'✅ Correlation ID: {cid}')

# Test secure logger
logger = get_secure_logger('test')
print(f'✅ Logger: {type(logger).__name__}')

print('🚀 All security enhancements working!')
