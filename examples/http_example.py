#!/usr/bin/env python3
"""
Example: Using Weather MCP over HTTP

This example shows how to:
1. Start the Weather MCP server with HTTP transport
2. Connect to it from a client application
3. Call weather tools over HTTP
"""

import asyncio
import sys
import os

# Add parent directory to path so we can import weather_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weather_mcp.http_transport import MCPHTTPClient


async def weather_example():
    """Example of using Weather MCP over HTTP"""
    
    print("🌍 Weather MCP HTTP Example")
    print("=" * 40)
    
    # Create HTTP client (assumes server is running on localhost:8000)
    client = MCPHTTPClient("http://localhost:8000")
    
    try:
        print("\n🔌 Connecting to Weather MCP server...")
        
        # Initialize connection
        init_response = await client.initialize()
        server_info = init_response['result']['serverInfo']
        print(f"✅ Connected to {server_info['name']} v{server_info['version']}")
        
        # List available tools
        tools_response = await client.list_tools()
        tools = tools_response['result']['tools']
        print(f"\n🛠️  Available tools ({len(tools)}):")
        for tool in tools:
            print(f"   • {tool['name']}")
        
        # Example coordinates (Canary Islands)
        latitude = 28.2916
        longitude = -16.6291
        
        print(f"\n🌍 Getting weather for {latitude}°N, {longitude}°W (Canary Islands)")
        
        # Get GraphCast AI forecast
        print("\n🧠 Getting GraphCast AI forecast...")
        forecast_response = await client.call_tool(
            "get_graphcast_forecast",
            {
                "latitude": latitude,
                "longitude": longitude,
                "days": 5
            }
        )
        
        forecast_text = forecast_response['result']['content'][0]['text']
        print("✅ Forecast received!")
        print(f"📊 {forecast_text[:200]}...")
        
        # Get historical weather
        print("\n📚 Getting historical weather data...")
        historical_response = await client.call_tool(
            "get_historical_weather",
            {
                "latitude": latitude,
                "longitude": longitude,
                "days_back": 7
            }
        )
        
        historical_text = historical_response['result']['content'][0]['text']
        print("✅ Historical data received!")
        print(f"📊 {historical_text[:200]}...")
        
        # Get complete timeline
        print("\n📈 Getting complete weather timeline...")
        timeline_response = await client.call_tool(
            "get_complete_weather_timeline",
            {
                "latitude": latitude,
                "longitude": longitude,
                "days_back": 3,
                "days_forward": 5
            }
        )
        
        timeline_text = timeline_response['result']['content'][0]['text']
        print("✅ Complete timeline received!")
        print(f"📊 {timeline_text[:300]}...")
        
        print("\n🎉 Example completed successfully!")
        print("\n💡 Next steps:")
        print("   • Integrate this into your web application")
        print("   • Build a weather dashboard using the HTTP API")
        print("   • Create mobile apps that connect to your MCP server")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure the server is running:")
        print("   python -m weather_mcp.http_server")


if __name__ == "__main__":
    asyncio.run(weather_example())