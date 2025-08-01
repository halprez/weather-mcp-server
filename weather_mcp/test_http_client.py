#!/usr/bin/env python3
"""
Test client for Weather MCP HTTP Transport

Demonstrates how to interact with the MCP server over HTTP.
"""

import asyncio
import json
import logging
from .http_transport import MCPHTTPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_http_client():
    """Test the HTTP MCP client"""
    
    # Create client
    client = MCPHTTPClient("http://localhost:8000")
    
    print("🧪 Testing Weather MCP HTTP Transport")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("\n1️⃣ Health Check...")
        health = await client.health_check()
        print(f"✅ Server status: {health['status']}")
        print(f"📅 Timestamp: {health['timestamp']}")
        
        # Test 2: Initialize connection
        print("\n2️⃣ Initializing MCP connection...")
        init_response = await client.initialize()
        print(f"✅ Protocol version: {init_response['result']['protocolVersion']}")
        print(f"🌟 Server: {init_response['result']['serverInfo']['name']} v{init_response['result']['serverInfo']['version']}")
        
        # Test 3: List available tools
        print("\n3️⃣ Listing available tools...")
        tools_response = await client.list_tools()
        tools = tools_response['result']['tools']
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   🛠️  {tool['name']}: {tool['description']}")
            
        # Test 4: Call GraphCast forecast tool
        print("\n4️⃣ Testing GraphCast forecast...")
        forecast_response = await client.call_tool(
            "get_graphcast_forecast",
            {
                "latitude": 28.2916,
                "longitude": -16.6291,
                "days": 3
            }
        )
        forecast_content = forecast_response['result']['content'][0]['text']
        print("✅ GraphCast forecast received:")
        print("📊 Preview:", forecast_content[:200] + "..." if len(forecast_content) > 200 else forecast_content)
        
        # Test 5: Call historical weather tool
        print("\n5️⃣ Testing historical weather...")
        historical_response = await client.call_tool(
            "get_historical_weather",
            {
                "latitude": 28.2916,
                "longitude": -16.6291,
                "days_back": 3
            }
        )
        historical_content = historical_response['result']['content'][0]['text']
        print("✅ Historical weather received:")
        print("📊 Preview:", historical_content[:200] + "..." if len(historical_content) > 200 else historical_content)
        
        # Test 6: Call complete timeline
        print("\n6️⃣ Testing complete weather timeline...")
        timeline_response = await client.call_tool(
            "get_complete_weather_timeline",
            {
                "latitude": 28.2916,
                "longitude": -16.6291,
                "days_back": 2,
                "days_forward": 3
            }
        )
        timeline_content = timeline_response['result']['content'][0]['text']
        print("✅ Complete timeline received:")
        print("📊 Preview:", timeline_content[:300] + "..." if len(timeline_content) > 300 else timeline_content)
        
        print("\n🎉 ALL HTTP TRANSPORT TESTS PASSED!")
        print("🌐 Your Weather MCP server is working perfectly over HTTP!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test error details:")


async def test_raw_http():
    """Test raw HTTP requests (for debugging)"""
    import aiohttp
    
    print("\n🔧 Testing raw HTTP requests...")
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        async with session.get("http://localhost:8000/health") as response:
            health_data = await response.json()
            print(f"Health check: {health_data['status']}")
            
        # Test info endpoint  
        async with session.get("http://localhost:8000/info") as response:
            info_data = await response.json()
            print(f"Server info: {info_data['name']}")
            
        # Test MCP endpoint
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        async with session.post(
            "http://localhost:8000/mcp",
            json=mcp_request
        ) as response:
            mcp_data = await response.json()
            tools_count = len(mcp_data['result']['tools'])
            print(f"MCP tools/list: {tools_count} tools available")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "raw":
        asyncio.run(test_raw_http())
    else:
        asyncio.run(test_http_client())