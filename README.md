# Elastica MCP Server

A Python-based Model Context Protocol (MCP) server for controlling Elastica soft slender-body physics simulations with natural language.

## Features

- Run Elastica simulations through MCP
- Control simulation parameters remotely
- Monitor simulation state in real-time
- Support for various Elastica examples (including continuum snake models)

## Requirements

- Python 3.10+
- PyElastica >= 0.3.3
- MCP
- uv (for source installation)

## Launching the server

```bash
git clone https://github.com/skim0119/elastica-mcp-server.git
uv sync
elastica_mcp_server
```

```bash
# uvx --from git+https://github.com/skim0119/elastica-mcp-server@main elastica_mcp_server  # not sure how to do this yet
```

## mcp.json setup

```json
{
    "mcpServers": {
        "elastica-simulation-server": {
            "command": "elastica_mcp_server",
            "args": []
        }
    }
}
```