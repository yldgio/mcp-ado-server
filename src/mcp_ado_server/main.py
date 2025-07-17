"""
Main entry point for the MCP Azure DevOps Server.
"""

import asyncio
import logging
import sys
from typing import Optional

import click
from .config import Config
from .server import MCPAzureDevOpsServer


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Setup logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_format.lower() == "json":
        # For production, you might want to use a JSON formatter like structlog
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=[handler],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set specific logger levels
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


@click.command()
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to configuration file'
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default='INFO',
    help='Logging level'
)
@click.option(
    '--log-format',
    type=click.Choice(['json', 'text'], case_sensitive=False),
    default='json',
    help='Logging format'
)
def main(
    config: Optional[str] = None,
    log_level: str = 'INFO',
    log_format: str = 'json'
) -> None:
    """MCP Azure DevOps Server - A Model Context Protocol server for Azure DevOps."""
    try:
        # Load configuration
        if config:
            # TODO: Implement config file loading
            raise NotImplementedError("Config file loading not yet implemented")
        else:
            server_config = Config.from_env()
            server_config.validate()
        
        # Override logging settings if provided
        if log_level:
            server_config.log_level = log_level
        if log_format:
            server_config.log_format = log_format
        
        # Setup logging
        setup_logging(server_config.log_level, server_config.log_format)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting MCP Azure DevOps Server")
        logger.info(f"Organization: {server_config.organization}")
        logger.info(f"API Version: {server_config.api_version}")
        logger.info(f"Log Level: {server_config.log_level}")
        
        # Create and run server
        server = MCPAzureDevOpsServer(server_config)
        asyncio.run(server.run())
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
