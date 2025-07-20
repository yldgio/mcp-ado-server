#!/usr/bin/env python3
"""
Test script to verify dev container setup works correctly.
This script tests the core functionality that should work in the dev container.
"""

import os
import subprocess
import sys
from pathlib import Path


def test_python_version():
    """Test that Python version meets requirements."""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 10:
        print("✓ Python version requirement met (>=3.10)")
        return True
    else:
        print("✗ Python version requirement not met (>=3.10)")
        return False


def test_package_import():
    """Test that the MCP ADO Server package can be imported."""
    try:
        import mcp_ado_server

        print("✓ mcp_ado_server package imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import mcp_ado_server: {e}")
        return False


def test_dependencies():
    """Test that key dependencies are available."""
    dependencies = [
        "mcp",
        "httpx",
        "pydantic",
        "python_dotenv",
        "structlog",
        "click",
        "azure.devops",
    ]

    success = True
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_").replace(".", "."))
            print(f"✓ {dep} imported successfully")
        except ImportError:
            print(f"✗ Failed to import {dep}")
            success = False

    return success


def test_dev_dependencies():
    """Test that development dependencies are available."""
    dev_deps = ["pytest", "black", "isort", "mypy"]

    success = True
    for dep in dev_deps:
        try:
            __import__(dep)
            print(f"✓ {dep} imported successfully")
        except ImportError:
            print(f"✗ Failed to import {dep}")
            success = False

    return success


def test_environment_variables():
    """Test that environment variables are configured."""
    env_vars = ["AZURE_DEVOPS_PAT", "AZURE_DEVOPS_ORGANIZATION"]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var} is set (value hidden for security)")
        else:
            print(f"⚠ {var} is not set (expected in dev container)")


def test_project_structure():
    """Test that project structure is correct."""
    required_files = [
        "pyproject.toml",
        "src/mcp_ado_server/__init__.py",
        "src/mcp_ado_server/main.py",
        "tests",
        ".devcontainer/devcontainer.json",
    ]

    success = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            success = False

    return success


def main():
    """Run all tests."""
    print("🧪 Testing MCP Azure DevOps Server setup...\n")

    tests = [
        ("Python Version", test_python_version),
        ("Package Import", test_package_import),
        ("Core Dependencies", test_dependencies),
        ("Dev Dependencies", test_dev_dependencies),
        ("Project Structure", test_project_structure),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))

    print(f"\n🔍 Environment Variables:")
    test_environment_variables()

    print(f"\n📊 Test Results Summary:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1

    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Dev container setup should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the setup before using dev container.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
