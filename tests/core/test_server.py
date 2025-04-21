"""
Tests for the elastica-mcp-server instantiation.
"""

from typing import Generator

import pytest
from mcp.server.fastmcp import FastMCP

from elastica_mcp_server.server import instantiate_server


@pytest.fixture
def mcp_server() -> Generator[FastMCP, None, None]:
    """
    Create a server instance for testing.

    This fixture instantiates the server but doesn't start it,
    as we just want to test the instantiation and configuration.

    Returns:
        Generator[FastMCP, None, None]: Server instance for testing.
    """
    server = instantiate_server()
    yield server
    # No need to stop the server since we don't actually start it


def test_server_instantiation() -> None:
    """
    Test that the server instantiates correctly.
    """
    server = instantiate_server()
    assert isinstance(server, FastMCP)
