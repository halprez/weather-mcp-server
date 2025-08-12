#!/usr/bin/env python3
"""
Quick deployment test script
"""

import asyncio
import aiohttp
import json

async def test_deployment():
    """Test the deployed weather MCP system"""
    print("🧪 Testing Deployment")
    print("=" * 30)
    
    # Test AIFS server
    print("1️⃣ Testing AIFS Server...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8080/health') as response:
                if response.status == 200:
                    health = await response.json()
                    print(f"✅ AIFS Server: {health.get('status', 'unknown')}")
                else:
                    print(f"❌ AIFS Server: HTTP {response.status}")
    except Exception as e:
        print(f"❌ AIFS Server: {e}")
    
    # Test AIFS forecast
    print("\n2️⃣ Testing AIFS Forecast...")
    try:
        payload = {
            "latitude": 28.29,
            "longitude": -16.63,
            "forecast_hours": 72
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8080/forecast',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    forecast = await response.json()
                    forecast_points = len(forecast.get('forecast', []))
                    print(f"✅ AIFS Forecast: {forecast_points} points")
                else:
                    print(f"❌ AIFS Forecast: HTTP {response.status}")
    except Exception as e:
        print(f"❌ AIFS Forecast: {e}")
    
    # Test MCP server integration
    print("\n3️⃣ Testing MCP Integration...")
    try:
        # Import and test MCP server directly
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from weather_mcp.mcp_server import WeatherMCPServer
        
        server = WeatherMCPServer()
        
        # Test tools list
        tools_request = {"method": "tools/list", "id": 1}
        tools_response = await server.handle_request(tools_request)
        
        if "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            aifs_tools = [t for t in tools if "aifs" in t["name"].lower()]
            ensemble_tools = [t for t in tools if "ensemble" in t["name"].lower()]
            
            print(f"✅ MCP Tools: {len(tools)} total")
            print(f"   🚀 AIFS tools: {len(aifs_tools)}")
            print(f"   🌟 Ensemble tools: {len(ensemble_tools)}")
        else:
            print("❌ MCP Tools: No tools returned")
            
        # Test AIFS forecast tool
        aifs_request = {
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": "get_aifs_forecast",
                "arguments": {
                    "latitude": 28.29,
                    "longitude": -16.63,
                    "forecast_hours": 72
                }
            }
        }
        
        aifs_response = await server.handle_request(aifs_request)
        if "result" in aifs_response:
            print("✅ AIFS MCP Tool: Working")
        else:
            print(f"❌ AIFS MCP Tool: {aifs_response.get('error', {}).get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ MCP Integration: {e}")
    
    print("\n🏁 Deployment test completed!")
    print("\n📋 Next steps:")
    print("1. Copy claude_desktop_config.json to Claude Desktop config directory")
    print("2. Restart Claude Desktop")
    print("3. Try: 'Get an AIFS forecast for the Canary Islands'")

if __name__ == "__main__":
    asyncio.run(test_deployment())