#!/usr/bin/env python3
"""
HTTP Server for Weather MCP

Run the Weather MCP server over HTTP instead of stdio.
This allows web applications and other HTTP clients to interact
with the MCP server.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from .http_transport import MCPHTTPTransport
from .mcp_server_v2 import EnhancedWeatherMCPServer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Log to stderr so it doesn't interfere with MCP JSON
    ]
)

logger = logging.getLogger(__name__)


class HTTPServerRunner:
    """Runner for MCP HTTP Server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.transport: Optional[MCPHTTPTransport] = None
        self.runner = None
        self.shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the HTTP server"""
        try:
            # Create MCP server
            logger.info("🌟 Initializing Weather MCP Server...")
            mcp_server = EnhancedWeatherMCPServer()
            
            # Create HTTP transport
            logger.info("🔄 Setting up HTTP transport...")
            self.transport = MCPHTTPTransport(mcp_server, self.host, self.port)
            
            # Start server
            self.runner = await self.transport.start_server()
            
            logger.info("🎉 Weather MCP HTTP Server is ready!")
            logger.info(f"📡 Listening on http://{self.host}:{self.port}")
            logger.info("💡 Try these endpoints:")
            logger.info(f"   • Health: http://{self.host}:{self.port}/health")
            logger.info(f"   • Info: http://{self.host}:{self.port}/info")
            logger.info(f"   • MCP: http://{self.host}:{self.port}/mcp")
            logger.info("🛑 Press Ctrl+C to stop")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            raise
            
    async def stop(self):
        """Stop the HTTP server"""
        logger.info("🛑 Shutting down...")
        self.shutdown_event.set()
        
        if self.runner:
            await self.transport.stop_server(self.runner)
            
        logger.info("✅ Shutdown complete")
        
    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}")
        asyncio.create_task(self.stop())


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Weather MCP HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create server runner
    server_runner = HTTPServerRunner(args.host, args.port)
    
    # Setup signal handlers
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, server_runner.handle_signal)
        
    try:
        await server_runner.start()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())