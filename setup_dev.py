#!/usr/bin/env python3
"""
Setup script for development environment using uv.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    return result


def check_uv_installed():
    """Check if uv is installed."""
    result = run_command("uv --version", check=False)
    return result.returncode == 0


def install_uv():
    """Install uv if not already installed."""
    if sys.platform == "win32":
        print("Please install uv manually on Windows:")
        print('powershell -c "irm https://astral.sh/uv/install.ps1 | iex"')
        sys.exit(1)
    else:
        print("Installing uv...")
        run_command("curl -LsSf https://astral.sh/uv/install.sh | sh")


def setup_environment():
    """Set up the development environment."""
    print("Setting up MCP Azure DevOps Server development environment...")

    # Check if uv is installed
    if not check_uv_installed():
        print("uv is not installed. Installing...")
        install_uv()

    # Create virtual environment
    print("Creating virtual environment...")
    run_command("uv venv")

    # Install dependencies
    print("Installing dependencies...")
    run_command("uv pip install -e .")

    # Install development dependencies
    print("Installing development dependencies...")
    run_command('uv pip install -e ".[dev]"')

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        if sys.platform == "win32":
            run_command(f"copy {env_example} {env_file}")
        else:
            run_command(f"cp {env_example} {env_file}")
        print("Please edit .env file with your Azure DevOps configuration")

    # Install pre-commit hooks
    print("Installing pre-commit hooks...")
    run_command("uv run pre-commit install")

    print("\n✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your Azure DevOps configuration")
    print("2. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("3. Run the server: mcp-ado-server")
    print("4. Run tests: pytest")


if __name__ == "__main__":
    setup_environment()
