#!/usr/bin/env python3
"""
Security validation script for MCP Azure DevOps Server.

This script scans the codebase for potential security vulnerabilities including:
- Hardcoded secrets and credentials
- Sensitive patterns in source code
- Configuration issues
- Dependency vulnerabilities
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'


class SecurityScanner:
    """Security scanner for detecting potential vulnerabilities."""

    # Patterns that indicate potential secrets
    SECRET_PATTERNS = [
        # API Keys and Tokens
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,})["\']', 'API Key'),
        (r'(?i)(access[_-]?token|accesstoken)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'Access Token'),
        (r'(?i)(bearer[_-]?token|bearertoken)\s*[:=]\s*["\']([a-zA-Z0-9_\-\+\/]{20,})["\']', 'Bearer Token'),
        
        # Azure DevOps PAT (Personal Access Token) - 52 character base64
        (r'(?i)(pat|personal[_-]?access[_-]?token)\s*[:=]\s*["\']([A-Za-z0-9+\/]{52})["\']', 'Azure DevOps PAT'),
        
        # Generic secrets
        (r'(?i)(secret|password|passwd)\s*[:=]\s*["\']([a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]{8,})["\']', 'Secret/Password'),
        
        # Database connection strings
        (r'(?i)(connection[_-]?string|connectionstring)\s*[:=]\s*["\']([^"\']+)["\']', 'Connection String'),
        
        # URLs with embedded credentials
        (r'(?i)(https?:\/\/[a-zA-Z0-9]+:[a-zA-Z0-9]+@[^\s"\']+)', 'URL with credentials'),
        
        # GUIDs that might be sensitive
        (r'(?i)(client[_-]?id|tenant[_-]?id|subscription[_-]?id)\s*[:=]\s*["\']([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})["\']', 'GUID'),
    ]

    # File extensions to scan
    SCAN_EXTENSIONS = ['.py', '.json', '.yaml', '.yml', '.toml', '.txt', '.md', '.env']
    
    # Files and directories to exclude
    EXCLUDE_PATTERNS = [
        r'\.git/',
        r'\.mypy_cache/',
        r'__pycache__/',
        r'\.pytest_cache/',
        r'htmlcov/',
        r'\.venv/',
        r'venv/',
        r'node_modules/',
        r'\.env\.example$',  # Example files are OK
        r'test_.*\.py$',     # Test files may have dummy secrets
        r'.*\.lock$',        # Lock files
        r'.*\.log$',         # Log files
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[Dict] = []

    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        relative_path = file_path.relative_to(self.project_root)
        
        # Check exclude patterns
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, str(relative_path)):
                return False
        
        # Check file extension
        return file_path.suffix.lower() in self.SCAN_EXTENSIONS

    def scan_file_for_secrets(self, file_path: Path) -> List[Dict]:
        """Scan a single file for potential secrets."""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.splitlines(), 1):
                for pattern, secret_type in self.SECRET_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Skip if it's clearly a placeholder or example
                        matched_value = match.group(2) if len(match.groups()) > 1 else match.group(1)
                        if self.is_placeholder_value(matched_value):
                            continue
                            
                        findings.append({
                            'type': 'potential_secret',
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': line_num,
                            'secret_type': secret_type,
                            'pattern': pattern,
                            'line_content': line.strip(),
                            'severity': 'HIGH'
                        })
                        
        except Exception as e:
            findings.append({
                'type': 'scan_error',
                'file': str(file_path.relative_to(self.project_root)),
                'error': str(e),
                'severity': 'LOW'
            })
            
        return findings

    def is_placeholder_value(self, value: str) -> bool:
        """Check if a value appears to be a placeholder."""
        placeholder_indicators = [
            'your-', 'example', 'placeholder', 'replace', 'change',
            'todo', 'fixme', 'dummy', 'test', 'sample', 'fake',
            'xxx', '000', '123', 'abc', 'def'
        ]
        
        value_lower = value.lower()
        return any(indicator in value_lower for indicator in placeholder_indicators)

    def check_environment_file_security(self) -> List[Dict]:
        """Check for .env files and their security."""
        findings = []
        
        # Look for .env files
        env_files = list(self.project_root.glob('**/.env'))
        env_files.extend(list(self.project_root.glob('**/.env.local')))
        env_files.extend(list(self.project_root.glob('**/.env.production')))
        
        for env_file in env_files:
            if env_file.name.endswith('.example'):
                continue  # Example files are OK
                
            findings.append({
                'type': 'env_file_found',
                'file': str(env_file.relative_to(self.project_root)),
                'message': 'Environment file found - ensure it\'s in .gitignore',
                'severity': 'MEDIUM'
            })
            
        return findings

    def check_git_ignore(self) -> List[Dict]:
        """Check .gitignore for important security entries."""
        findings = []
        gitignore_path = self.project_root / '.gitignore'
        
        if not gitignore_path.exists():
            findings.append({
                'type': 'missing_gitignore',
                'message': '.gitignore file is missing',
                'severity': 'MEDIUM'
            })
            return findings
            
        try:
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                
            # Check for important patterns
            important_patterns = [
                ('.env', 'Environment files'),
                ('*.log', 'Log files'),
                ('__pycache__/', 'Python cache'),
                ('.mypy_cache/', 'MyPy cache'),
            ]
            
            for pattern, description in important_patterns:
                if pattern not in gitignore_content:
                    findings.append({
                        'type': 'gitignore_missing_pattern',
                        'pattern': pattern,
                        'description': description,
                        'message': f'Missing {pattern} in .gitignore',
                        'severity': 'LOW'
                    })
                    
        except Exception as e:
            findings.append({
                'type': 'gitignore_read_error',
                'error': str(e),
                'severity': 'LOW'
            })
            
        return findings

    def check_file_permissions(self) -> List[Dict]:
        """Check for files with overly permissive permissions."""
        findings = []
        
        # This is primarily useful on Unix systems
        if os.name != 'posix':
            return findings
            
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
                
            if self.should_scan_file(file_path):
                try:
                    mode = file_path.stat().st_mode
                    # Check if world-writable
                    if mode & 0o002:
                        findings.append({
                            'type': 'file_permission',
                            'file': str(file_path.relative_to(self.project_root)),
                            'message': 'File is world-writable',
                            'severity': 'MEDIUM'
                        })
                except Exception:
                    pass  # Ignore permission errors
                    
        return findings

    def run_dependency_check(self) -> List[Dict]:
        """Run dependency security check using safety."""
        findings = []
        
        try:
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                findings.append({
                    'type': 'dependency_check',
                    'message': 'No known security vulnerabilities in dependencies',
                    'severity': 'INFO'
                })
            else:
                # Parse JSON output if available
                try:
                    import json
                    vulnerabilities = json.loads(result.stdout)
                    for vuln in vulnerabilities:
                        findings.append({
                            'type': 'dependency_vulnerability',
                            'package': vuln.get('package', 'unknown'),
                            'version': vuln.get('installed_version', 'unknown'),
                            'vulnerability': vuln.get('vulnerability', 'unknown'),
                            'message': vuln.get('description', 'Security vulnerability found'),
                            'severity': 'HIGH'
                        })
                except (json.JSONDecodeError, KeyError):
                    findings.append({
                        'type': 'dependency_check_error',
                        'message': f'Dependency check failed: {result.stderr}',
                        'severity': 'MEDIUM'
                    })
                    
        except FileNotFoundError:
            findings.append({
                'type': 'dependency_check_unavailable',
                'message': 'safety tool not installed - run "pip install safety" to enable dependency checking',
                'severity': 'INFO'
            })
        except Exception as e:
            findings.append({
                'type': 'dependency_check_error',
                'message': f'Error running dependency check: {str(e)}',
                'severity': 'LOW'
            })
            
        return findings

    def scan(self) -> List[Dict]:
        """Run complete security scan."""
        print(f"{BLUE}🔍 Starting security scan of {self.project_root}{RESET}")
        
        all_findings = []
        
        # Scan for secrets in files
        print(f"{BLUE}📁 Scanning files for potential secrets...{RESET}")
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and self.should_scan_file(file_path):
                findings = self.scan_file_for_secrets(file_path)
                all_findings.extend(findings)
        
        # Check environment files
        print(f"{BLUE}🌐 Checking environment file security...{RESET}")
        all_findings.extend(self.check_environment_file_security())
        
        # Check .gitignore
        print(f"{BLUE}📋 Checking .gitignore configuration...{RESET}")
        all_findings.extend(self.check_git_ignore())
        
        # Check file permissions
        print(f"{BLUE}🔒 Checking file permissions...{RESET}")
        all_findings.extend(self.check_file_permissions())
        
        # Run dependency check
        print(f"{BLUE}📦 Checking dependencies for vulnerabilities...{RESET}")
        all_findings.extend(self.run_dependency_check())
        
        return all_findings

    def print_report(self, findings: List[Dict]):
        """Print security scan report."""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}🛡️  SECURITY SCAN REPORT{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        # Group findings by severity
        by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': [], 'INFO': []}
        for finding in findings:
            severity = finding.get('severity', 'LOW')
            by_severity[severity].append(finding)
        
        # Print summary
        total_issues = len(findings)
        high_issues = len(by_severity['HIGH'])
        medium_issues = len(by_severity['MEDIUM'])
        low_issues = len(by_severity['LOW'])
        
        print(f"📊 {BLUE}SUMMARY:{RESET}")
        print(f"   Total issues found: {total_issues}")
        print(f"   🔴 High severity: {high_issues}")
        print(f"   🟡 Medium severity: {medium_issues}")
        print(f"   🟠 Low severity: {low_issues}")
        print(f"   ℹ️  Informational: {len(by_severity['INFO'])}")
        
        # Print details for each severity level
        for severity, color in [('HIGH', RED), ('MEDIUM', YELLOW), ('LOW', YELLOW), ('INFO', GREEN)]:
            if by_severity[severity]:
                print(f"\n{color}{'='*40}{RESET}")
                print(f"{color}{severity} SEVERITY ISSUES:{RESET}")
                print(f"{color}{'='*40}{RESET}")
                
                for finding in by_severity[severity]:
                    print(f"\n{color}• {finding.get('type', 'Unknown').replace('_', ' ').title()}:{RESET}")
                    
                    if 'file' in finding:
                        print(f"  📁 File: {finding['file']}")
                    if 'line' in finding:
                        print(f"  📍 Line: {finding['line']}")
                    if 'message' in finding:
                        print(f"  💬 Message: {finding['message']}")
                    if 'secret_type' in finding:
                        print(f"  🔑 Type: {finding['secret_type']}")
                    if 'line_content' in finding:
                        print(f"  📝 Content: {finding['line_content'][:100]}...")
        
        # Overall assessment
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}🎯 OVERALL ASSESSMENT:{RESET}")
        
        if high_issues > 0:
            print(f"{RED}❌ CRITICAL: {high_issues} high-severity issues found that need immediate attention{RESET}")
            return False
        elif medium_issues > 0:
            print(f"{YELLOW}⚠️  WARNING: {medium_issues} medium-severity issues found that should be addressed{RESET}")
            return True
        else:
            print(f"{GREEN}✅ GOOD: No critical security issues found{RESET}")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Security scanner for MCP Azure DevOps Server')
    parser.add_argument('--path', '-p', default='.', help='Path to scan (default: current directory)')
    parser.add_argument('--json', '-j', action='store_true', help='Output results in JSON format')
    parser.add_argument('--fail-on-high', action='store_true', help='Exit with non-zero code if high-severity issues found')
    
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    if not project_root.exists():
        print(f"{RED}Error: Path {project_root} does not exist{RESET}")
        sys.exit(1)
    
    scanner = SecurityScanner(project_root)
    findings = scanner.scan()
    
    if args.json:
        import json
        print(json.dumps(findings, indent=2))
    else:
        scan_passed = scanner.print_report(findings)
        
        if args.fail_on_high and not scan_passed:
            sys.exit(1)


if __name__ == '__main__':
    main()
