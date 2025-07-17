"""
MCP Azure DevOps Server

A Model Context Protocol server for interacting with Azure DevOps,
focusing on variable groups and service connections.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import MCPAzureDevOpsServer
from .config import Config
from .models import VariableGroup, ServiceConnection

__all__ = [
    "MCPAzureDevOpsServer",
    "Config", 
    "VariableGroup",
    "ServiceConnection",
]
