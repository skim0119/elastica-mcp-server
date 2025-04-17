"""Elastica MCP Server package."""

from importlib.metadata import version


def _get_version() -> str:
    """Get the version of the package."""
    try:
        return version("elastica-mcp-server")
    except Exception:
        return "0.0.0"  # fallback version


__version__ = _get_version()
