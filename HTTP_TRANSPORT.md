# Weather MCP HTTP Transport

This implementation adds HTTP transport support to the Weather MCP server, allowing it to be accessed via HTTP instead of stdin/stdout. This enables web applications, mobile apps, and other HTTP clients to interact with the MCP server.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Start the HTTP Server

```bash
# Start on default port (8000)
uv run python -m weather_mcp.http_server

# Start on custom host/port
uv run python -m weather_mcp.http_server --host 0.0.0.0 --port 3000

# Enable verbose logging
uv run python -m weather_mcp.http_server --verbose
```

### 3. Test the Server

```bash
# Check server health
curl http://localhost:8000/health

# Get server information
curl http://localhost:8000/info

# Test MCP protocol
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## 📋 Architecture

The HTTP transport consists of several key components:

### `MCPHTTPTransport`
- Wraps the existing `EnhancedWeatherMCPServer`
- Handles HTTP requests and translates them to/from MCP JSON-RPC
- Maintains full MCP protocol compliance
- Supports CORS for web clients

### `MCPHTTPClient`
- Python client for connecting to MCP servers over HTTP
- Provides async methods for all MCP operations
- Handles JSON-RPC request/response formatting

### `HTTPServerRunner`
- Manages server lifecycle
- Handles graceful shutdown
- Provides command-line interface

## 🔗 API Endpoints

### Health Check
```
GET /health
```
Returns server health status and basic information.

### Server Information
```
GET /info
```
Returns detailed server information including available endpoints.

### MCP Protocol
```
POST /mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "METHOD_NAME",
  "params": {...}
}
```

All MCP methods are supported:
- `initialize` - Initialize MCP connection
- `tools/list` - List available tools
- `tools/call` - Call a specific tool

## 🛠️ Usage Examples

### Python Client

```python
from weather_mcp.http_transport import MCPHTTPClient

async def example():
    client = MCPHTTPClient("http://localhost:8000")
    
    # Initialize connection
    await client.initialize()
    
    # List tools
    tools = await client.list_tools()
    
    # Get weather forecast
    result = await client.call_tool(
        "get_graphcast_forecast",
        {
            "latitude": 28.2916,
            "longitude": -16.6291,
            "days": 5
        }
    )
```

### JavaScript/Web

```javascript
const response = await fetch('http://localhost:8000/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "get_graphcast_forecast",
      arguments: {
        latitude: 28.2916,
        longitude: -16.6291,
        days: 5
      }
    }
  })
});
```

### Curl

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_graphcast_forecast",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days": 5
      }
    }
  }'
```

## 📁 Examples

The `examples/` directory contains several usage examples:

- **`http_example.py`** - Complete Python client example
- **`curl_examples.sh`** - Shell script with curl examples
- **`web_interface.html`** - Interactive web interface

To run the examples:

```bash
# Run Python example (server must be running)
python examples/http_example.py

# Run curl examples (server must be running)
bash examples/curl_examples.sh

# Open web interface (server must be running)
open examples/web_interface.html
```

## 🔒 Security Considerations

### CORS
The server includes CORS support to allow web applications to connect. In production, you should configure CORS more restrictively:

```python
# Modify http_transport.py for production
cors = aiohttp_cors.setup(self.app, defaults={
    "https://your-domain.com": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods=["POST", "GET", "OPTIONS"]
    )
})
```

### HTTPS
For production deployment, use HTTPS:

```bash
# Use a reverse proxy like nginx
# Or run with SSL context (requires SSL certificates)
```

### Authentication
Consider adding authentication for production use:

```python
# Add authentication middleware to http_transport.py
async def auth_middleware(request, handler):
    # Implement your authentication logic
    return await handler(request)
```

## 🚀 Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "-m", "weather_mcp.http_server", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  weather-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
```

### Systemd Service
```ini
[Unit]
Description=Weather MCP HTTP Server
After=network.target

[Service]
Type=simple
User=weather-mcp
WorkingDirectory=/opt/weather-mcp
ExecStart=/opt/weather-mcp/venv/bin/python -m weather_mcp.http_server
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔧 Configuration

Environment variables can be used to configure the server:

```bash
export WEATHER_MCP_HOST=0.0.0.0
export WEATHER_MCP_PORT=8000
export WEATHER_MCP_LOG_LEVEL=INFO
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run HTTP transport tests specifically
python -m weather_mcp.test_http_client
```

## 🐛 Troubleshooting

### Server Won't Start
1. Check if port is already in use: `lsof -i :8000`
2. Verify dependencies are installed: `pip list | grep aiohttp`
3. Check Python version: `python --version` (requires Python 3.8+)

### CORS Issues
1. Check browser console for CORS errors
2. Verify server logs show CORS setup
3. Test with curl first to isolate browser issues

### Connection Refused
1. Verify server is running: `curl http://localhost:8000/health`
2. Check firewall settings
3. Verify host/port configuration

## 📚 Protocol Compliance

This HTTP transport maintains full MCP protocol compliance by:

1. **JSON-RPC 2.0**: All requests/responses follow JSON-RPC 2.0 specification
2. **MCP Methods**: All standard MCP methods are supported
3. **Error Handling**: Proper JSON-RPC error responses
4. **Notifications**: Support for notification-style requests (no response expected)

## 🔄 Migration from stdio

To migrate from stdio transport to HTTP:

### Before (stdio)
```python
# Run via stdin/stdout
python -m weather_mcp.mcp_server_v2
```

### After (HTTP)
```python
# Run via HTTP
python -m weather_mcp.http_server
```

Client code changes:
```python
# Before: stdio client
# Use MCP SDK with stdio transport

# After: HTTP client
from weather_mcp.http_transport import MCPHTTPClient
client = MCPHTTPClient("http://localhost:8000")
```

The HTTP transport is fully backward compatible - all existing MCP functionality works exactly the same way.