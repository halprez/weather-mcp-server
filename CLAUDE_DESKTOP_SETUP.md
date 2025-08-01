# Claude Desktop Configuration

This guide shows how to configure Claude Desktop to use your Weather MCP server with both stdio and HTTP transports.

## 📍 Configuration File Location

The Claude Desktop configuration file is located at:

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

## 🔧 Method 1: stdio Transport (Recommended for Claude Desktop)

Claude Desktop natively supports stdio transport. Use this configuration with `uv`:

```json
{
  "mcpServers": {
    "weather-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "weather_mcp.mcp_server_v2"],
      "cwd": "/Users/halprez/src/weather-mcp-server"
    }
  }
}
```

### Setup Steps:

1. **Install Dependencies with uv:**
   ```bash
   cd /Users/halprez/src/weather-mcp-server
   uv sync
   ```

2. **Test the Server:**
   ```bash
   uv run python -m weather_mcp.mcp_server_v2 test
   ```

3. **Update Claude Desktop Config:**
   ```bash
   # Open the config file
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Or create it if it doesn't exist
   mkdir -p ~/Library/Application\ Support/Claude/
   echo '{}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

4. **Add the Weather MCP Server:**
   Replace the contents with:
   ```json
   {
     "mcpServers": {
       "weather-mcp": {
         "command": "uv",
         "args": ["run", "python", "-m", "weather_mcp.mcp_server_v2"],
         "cwd": "/Users/halprez/src/weather-mcp-server"
       }
     }
   }
   ```

5. **Restart Claude Desktop**

## 🌐 Method 2: HTTP Transport (For Other Applications)

While Claude Desktop doesn't natively support HTTP transport, you can run the HTTP server separately for other applications:

### Running the HTTP Server:

```bash
# Start the HTTP server with uv
uv run python -m weather_mcp.http_server --port 8000

# Test it works
curl http://localhost:8000/health
```

### For Web Applications:

```javascript
// Use the HTTP transport in web apps
const client = new MCPHTTPClient('http://localhost:8000');
await client.initialize();
const tools = await client.list_tools();
```

## 🐍 Python Environment Setup

Make sure you're using the correct Python environment:

```bash
# Check Python version (needs 3.8+)
python --version

# With uv, dependency management is automatic
uv sync  # Creates virtual environment and installs dependencies

# Check uv is working
uv run python --version
```

With `uv`, virtual environment management is automatic, so the config remains simple:

```json
{
  "mcpServers": {
    "weather-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "weather_mcp.mcp_server_v2"],
      "cwd": "/Users/halprez/src/weather-mcp-server"
    }
  }
}
```

## 🔍 Troubleshooting

### Server Not Starting

1. **Check uv Installation:**
   ```bash
   which uv
   uv --version
   ```

2. **Check Dependencies:**
   ```bash
   uv run python -c "import mcp; print('MCP installed')"
   ```

3. **Test Server Manually:**
   ```bash
   cd /Users/halprez/src/weather-mcp-server
   uv run python -m weather_mcp.mcp_server_v2 test
   ```

### Claude Desktop Not Recognizing Server

1. **Validate JSON:**
   ```bash
   # Check JSON syntax
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```

2. **Check Permissions:**
   ```bash
   # Ensure files are readable
   ls -la ~/Library/Application\ Support/Claude/
   ```

3. **Restart Claude Desktop:** Close completely and reopen

### Check Claude Desktop Logs

Claude Desktop logs can help debug MCP connection issues:

**macOS:**
```bash
# View Console app and filter for "Claude"
# Or check system logs
log stream --predicate 'subsystem contains "Claude"'
```

## 📝 Complete Example Config

Here's a complete `claude_desktop_config.json` with multiple MCP servers:

```json
{
  "mcpServers": {
    "weather-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "weather_mcp.mcp_server_v2"],
      "cwd": "/Users/halprez/src/weather-mcp-server"
    }
  },
  "globalShortcut": "Cmd+Shift+."
}
```

## ✅ Verification

After configuration, test in Claude Desktop:

1. **Start a new conversation**
2. **Ask Claude:** "What weather tools do you have available?"
3. **Test a tool:** "Get the weather forecast for New York"

You should see Claude using your Weather MCP tools!

## 🔄 Switching Between Transports

### For Development:
- Use **stdio** transport with Claude Desktop
- Use **HTTP** transport for web testing and other clients

### For Production:
- Keep **stdio** for Claude Desktop integration
- Deploy **HTTP** transport for web applications and APIs

Both transports use the same underlying MCP server, so functionality is identical!