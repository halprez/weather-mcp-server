"""
HTTP Transport for MCP Protocol

This module provides an HTTP wrapper around the MCP protocol, allowing
MCP servers to be accessed via HTTP while maintaining full protocol compliance.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from aiohttp import web, web_request
from aiohttp.web_response import Response
import aiohttp_cors
from datetime import datetime

from .mcp_server_v2 import EnhancedWeatherMCPServer

logger = logging.getLogger(__name__)


class MCPHTTPTransport:
    """
    HTTP Transport wrapper for MCP protocol.
    
    Translates HTTP requests to MCP JSON-RPC calls and back,
    maintaining full protocol compliance.
    """
    
    def __init__(self, mcp_server: EnhancedWeatherMCPServer, host: str = "0.0.0.0", port: int = 8000):
        self.mcp_server = mcp_server
        self.host = host
        self.port = port
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
        self._request_counter = 0
        
    def _setup_routes(self):
        """Setup HTTP routes for MCP endpoints"""
        # Main MCP endpoint
        self.app.router.add_post('/mcp', self.handle_mcp_request)
        
        # Health check endpoint
        self.app.router.add_get('/health', self.health_check)
        
        # Server info endpoint
        self.app.router.add_get('/info', self.server_info)
        
    def _setup_cors(self):
        """Setup CORS for web clients"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
            
    async def handle_options(self, request: web_request.Request) -> Response:
        """Handle CORS preflight requests"""
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400'
            }
        )
        
    async def handle_mcp_request(self, request: web_request.Request) -> Response:
        """
        Handle MCP requests over HTTP.
        
        Accepts JSON-RPC requests and forwards them to the MCP server,
        returning the response as HTTP JSON.
        """
        try:
            # Parse JSON request
            request_data = await request.json()
            
            # Validate JSON-RPC structure
            if not self._validate_jsonrpc_request(request_data):
                return self._error_response(
                    -32600, "Invalid Request", 
                    "Invalid JSON-RPC request structure"
                )
            
            # Generate request ID if not provided
            if 'id' not in request_data:
                self._request_counter += 1
                request_data['id'] = self._request_counter
                
            # Add JSON-RPC version if missing
            if 'jsonrpc' not in request_data:
                request_data['jsonrpc'] = '2.0'
                
            logger.info(f"HTTP->MCP: {request_data.get('method', 'unknown')} (id: {request_data.get('id')})")
            
            # Forward to MCP server
            mcp_response = await self.mcp_server.handle_request(request_data)
            
            # Handle notification (no response expected)
            if mcp_response is None:
                return web.Response(status=204)  # No Content
                
            # Return MCP response as HTTP JSON
            return web.json_response(mcp_response, status=200)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._error_response(-32700, "Parse error", str(e))
            
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return self._error_response(-32603, "Internal error", str(e))
            
    def _validate_jsonrpc_request(self, data: Any) -> bool:
        """Validate JSON-RPC request structure"""
        if not isinstance(data, dict):
            return False
            
        # Must have method
        if 'method' not in data or not isinstance(data['method'], str):
            return False
            
        # Params must be object or array if present
        if 'params' in data:
            if not isinstance(data['params'], (dict, list)):
                return False
                
        return True
        
    def _error_response(self, code: int, message: str, data: Optional[str] = None) -> Response:
        """Create JSON-RPC error response"""
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if data:
            error_response["error"]["data"] = data
            
        return web.json_response(error_response, status=400)
        
    async def health_check(self, request: web_request.Request) -> Response:
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "weather-mcp-http-transport",
            "timestamp": datetime.now().isoformat(),
            "mcp_server": {
                "name": self.mcp_server.name,
                "version": self.mcp_server.version
            }
        })
        
    async def server_info(self, request: web_request.Request) -> Response:
        """Server information endpoint"""
        return web.json_response({
            "name": "Weather MCP HTTP Transport",
            "version": "1.0.0",
            "description": "HTTP transport wrapper for Weather MCP Server",
            "mcp_protocol_version": "2025-06-18",
            "endpoints": {
                "mcp": "/mcp - Main MCP JSON-RPC endpoint",
                "health": "/health - Health check",
                "info": "/info - Server information"
            },
            "mcp_server": {
                "name": self.mcp_server.name,
                "version": self.mcp_server.version
            },
            "transport": {
                "protocol": "http",
                "host": self.host,
                "port": self.port
            }
        })
        
    async def start_server(self):
        """Start the HTTP server"""
        logger.info(f"🚀 Starting MCP HTTP Transport on {self.host}:{self.port}")
        logger.info(f"🌐 MCP endpoint: http://{self.host}:{self.port}/mcp")
        logger.info(f"❤️  Health check: http://{self.host}:{self.port}/health")
        logger.info(f"ℹ️  Server info: http://{self.host}:{self.port}/info")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"✅ HTTP Transport ready and listening!")
        return runner
        
    async def stop_server(self, runner):
        """Stop the HTTP server"""
        logger.info("🛑 Stopping HTTP Transport...")
        await runner.cleanup()
        logger.info("✅ HTTP Transport stopped")


class MCPHTTPClient:
    """
    HTTP client for MCP servers.
    
    Allows connecting to MCP servers over HTTP instead of stdio.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.mcp_url = f"{self.base_url}/mcp"
        self._request_counter = 0
        
    async def send_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Send MCP request over HTTP"""
        import aiohttp
        
        self._request_counter += 1
        request_data = {
            "jsonrpc": "2.0",
            "id": self._request_counter,
            "method": method
        }
        
        if params:
            request_data["params"] = params
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_url,
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 204:  # No content for notifications
                    return None
                    
                response_data = await response.json()
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response_data}")
                    
                return response_data
                
    async def initialize(self) -> Dict:
        """Initialize MCP connection"""
        return await self.send_request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "weather-mcp-http-client",
                "version": "1.0.0"
            }
        })
        
    async def list_tools(self) -> Dict:
        """List available tools"""
        return await self.send_request("tools/list")
        
    async def call_tool(self, name: str, arguments: Dict) -> Dict:
        """Call a tool"""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
    async def health_check(self) -> Dict:
        """Check server health"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                return await response.json()