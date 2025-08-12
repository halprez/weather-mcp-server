#!/bin/bash
# Weather MCP Server Launcher

echo "🌟 Starting Weather MCP Server"
echo "=============================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "⚠️  Docker not running - AIFS will use mock data"
    echo "🐳 To enable real AIFS predictions, start Docker and run:"
    echo "   docker-compose up --build"
    echo ""
fi

# Option 1: Run with Docker Compose (recommended)
if [ "$1" = "docker" ]; then
    echo "🐳 Starting complete Docker stack..."
    docker-compose up --build

# Option 2: Run HTTP server locally
elif [ "$1" = "http" ]; then
    echo "🌐 Starting HTTP MCP server on port 8081..."
    python weather_mcp/mcp_server.py

# Option 3: Run tests
elif [ "$1" = "test" ]; then
    echo "🧪 Running test suite..."
    python weather_mcp/mcp_server.py test

# Default: Show help
else
    echo "Usage: ./run.sh [docker|http|test]"
    echo ""
    echo "Options:"
    echo "  docker  - Start complete Docker stack (AIFS + MCP server)"
    echo "  http    - Start HTTP MCP server locally"
    echo "  test    - Run built-in tests"
    echo ""
    echo "Examples:"
    echo "  ./run.sh docker   # Full Docker deployment"
    echo "  ./run.sh http     # Local HTTP server"
    echo "  ./run.sh test     # Test the application"
    echo ""
    echo "📖 Check the README.md for complete setup instructions"
fi