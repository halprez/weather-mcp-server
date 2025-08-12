#!/bin/bash
# Weather MCP Server Starter Script for Claude Desktop
echo "Starting Weather MCP Server..." >&2
exec python3 weather_mcp/mcp_server.py stdio 2>/dev/null