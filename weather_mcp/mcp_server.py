# Create file: weather_mcp/mcp_server.py

"""
First MCP Server3: Let's build the foundation of our weather MCP server
"""

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime

class WeatherMCPServer:
    """
    Your first MCP Server!
    
    Think of this as a smart assistant that:
    1. Listens for requests from AI agents
    2. Processes weather data requests  
    3. Returns formatted weather information
    """
    
    def __init__(self):
        self.name = "WeatherMCP"
        self.version = "1.0.0"
        print(f"🌟 {self.name} v{self.version} initialized!")
        
    async def handle_request(self, request: Dict) -> Dict:
        """
        Handle incoming MCP requests
        This is like being a waiter - take the order, fulfill it, return result
        """
        print(f"📨 Received request: {request.get('method', 'unknown')}")
        
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return await self.list_tools()
        elif method == "tools/call":
            return await self.call_tool(params)
        else:
            return self.error_response(f"Unknown method: {method}")
    
    async def list_tools(self) -> Dict:
        """
        Tell AI agents what tools we have available
        Like showing a menu to a customer
        """
        tools = [
            {
                "name": "get_current_weather",
                "description": "Get current weather for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number", "description": "Latitude coordinate"},
                        "longitude": {"type": "number", "description": "Longitude coordinate"}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast using GraphCast AI",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "days": {"type": "number", "description": "Forecast days (1-10)"}
                    },
                    "required": ["latitude", "longitude"]
                }
            }
        ]
        
        return {
            "tools": tools
        }
    
    async def call_tool(self, params: Dict) -> Dict:
        """
        Execute the requested tool
        Like preparing the order in the kitchen
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        print(f"🛠️  Calling tool: {tool_name}")
        print(f"📝 Arguments: {arguments}")
        
        if tool_name == "get_current_weather":
            return await self.get_current_weather(arguments)
        elif tool_name == "get_weather_forecast":
            return await self.get_weather_forecast(arguments)
        else:
            return self.error_response(f"Unknown tool: {tool_name}")
    
    async def get_current_weather(self, args: Dict) -> Dict:
        """
        Get current weather (we'll make this real later)
        For now, let's return mock data so we can test the MCP flow
        """
        lat = args.get("latitude")
        lon = args.get("longitude")
        
        # Mock data for now - we'll replace with real API later
        mock_weather = {
            "location": {"latitude": lat, "longitude": lon},
            "temperature": 22.5,
            "humidity": 65,
            "wind_speed": 15,
            "description": "Partly cloudy",
            "timestamp": datetime.now().isoformat(),
            "source": "Mock data - will be real soon!"
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Current weather at {lat}, {lon}:\n"
                           f"🌡️  Temperature: {mock_weather['temperature']}°C\n"
                           f"💧 Humidity: {mock_weather['humidity']}%\n" 
                           f"💨 Wind: {mock_weather['wind_speed']} km/h\n"
                           f"☁️  Conditions: {mock_weather['description']}"
                }
            ]
        }
    
    async def get_weather_forecast(self, args: Dict) -> Dict:
        """
        Get GraphCast AI forecast (mock for now)
        """
        lat = args.get("latitude")
        lon = args.get("longitude") 
        days = args.get("days", 5)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"GraphCast AI Forecast for {lat}, {lon} ({days} days):\n"
                           f"🧠 AI Model: GraphCast (90% more accurate than traditional)\n"
                           f"⚡ Generation: <1 minute\n"
                           f"📅 Days: {days}\n"
                           f"📝 Note: Real GraphCast integration coming in next phase!"
                }
            ]
        }
    
    def error_response(self, message: str) -> Dict:
        """Return error response"""
        return {
            "error": {
                "code": -1,
                "message": message
            }
        }

# Test our MCP server
async def test_mcp_server():
    """Test our MCP server with sample requests"""
    print("🧪 Testing Our MCP Server")
    print("=" * 30)
    
    server = WeatherMCPServer()
    
    # Test 1: List available tools
    print("\n1️⃣ Testing tool list...")
    list_request = {"method": "tools/list"}
    response = await server.handle_request(list_request)
    print(f"✅ Found {len(response['tools'])} tools")
    
    # Test 2: Call current weather tool
    print("\n2️⃣ Testing current weather...")
    weather_request = {
        "method": "tools/call",
        "params": {
            "name": "get_current_weather",
            "arguments": {"latitude": 28.2916, "longitude": -16.6291}
        }
    }
    response = await server.handle_request(weather_request)
    print("✅ Current weather response received")
    
    # Test 3: Call forecast tool
    print("\n3️⃣ Testing forecast...")
    forecast_request = {
        "method": "tools/call",
        "params": {
            "name": "get_weather_forecast", 
            "arguments": {"latitude": 28.2916, "longitude": -16.6291, "days": 7}
        }
    }
    response = await server.handle_request(forecast_request)
    print("✅ Forecast response received")
    
    print("\n🎉 MCP Server working perfectly!")
    print("Next: We'll connect real weather APIs!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
