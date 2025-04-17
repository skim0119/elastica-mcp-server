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

## Launching the server

```bash
uvx --from git+https://github.com/skim0119/elastica-mcp-server@main elastica_mcp_server
```
