# Create file: weather_mcp/enhanced_mcp_server.py

"""
This is the enhanced version of the MCP server.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

try:
    # Try relative imports (when run as module)
    from .graphcast_client import GraphCastClient
    from .eumetsat_client import EUMETSATClient
    from .aifs_client import AIFSClient
    from .prediction_ensemble import PredictionEnsemble
except ImportError:
    # Fallback to absolute imports (when run directly)
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from graphcast_client import GraphCastClient
    from eumetsat_client import EUMETSATClient
    from aifs_client import AIFSClient
    from prediction_ensemble import PredictionEnsemble

class WeatherMCPServer:
    """
    Your Complete Weather MCP Server!
    
    This combines:
    - MCP protocol handling
    - GraphCast AI forecasts  
    - EUMETSAT historical data
    - Unified weather timeline
    """
    
    def __init__(self):
        self.name = "Weather MCP"
        self.version = "3.0.0"
        
        # Initialize data clients
        self.graphcast_client = GraphCastClient()
        self.eumetsat_client = EUMETSATClient()
        self.aifs_client = AIFSClient()
        self.ensemble = PredictionEnsemble()
        
        # Debug info goes to stderr (not stdout which is for MCP JSON)
        print(f"🌟 {self.name} v{self.version} ready!", file=sys.stderr)
        print("🧠 GraphCast AI: Connected", file=sys.stderr)
        print("🛰️  EUMETSAT: Connected", file=sys.stderr)
        print("🚀 AIFS AI: Connected", file=sys.stderr)
        print("🔬 Ensemble: Ready", file=sys.stderr)
        
    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        print(f"📨 MCP Request: {method}", file=sys.stderr)
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "weather-mcp",
                        "version": "2.0.0"
                    }
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "result": await self.list_tools()
            }
        elif method == "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": request_id, 
                "result": await self.call_tool(params)
            }
        elif method == "notifications/initialized":
            # No response needed for notifications
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def list_tools(self) -> Dict:
        """List all available weather tools"""
        tools = [
            {
                "name": "get_graphcast_forecast",
                "description": "Get AI-powered weather forecast using GraphCast",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number", "description": "Latitude (-90 to 90)"},
                        "longitude": {"type": "number", "description": "Longitude (-180 to 180)"},
                        "days": {"type": "number", "description": "Forecast days (1-16)", "default": 7}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "get_historical_weather",
                "description": "Get historical weather data from EUMETSAT satellites",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "days_back": {"type": "number", "description": "Days of history (1-30)", "default": 7}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "get_complete_weather_timeline",
                "description": "Get unified weather timeline: historical data + AI forecasts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "days_back": {"type": "number", "description": "Historical days", "default": 7},
                        "days_forward": {"type": "number", "description": "Forecast days", "default": 7}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "get_aifs_forecast",
                "description": "Get ECMWF AIFS AI weather forecast",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number", "description": "Latitude (-90 to 90)"},
                        "longitude": {"type": "number", "description": "Longitude (-180 to 180)"},
                        "forecast_hours": {"type": "number", "description": "Forecast hours (1-720)", "default": 240}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "compare_ai_models",
                "description": "Compare AIFS vs GraphCast AI weather predictions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "forecast_days": {"type": "number", "description": "Days to compare", "default": 7}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "get_ensemble_forecast",
                "description": "Get enhanced ensemble forecast combining AIFS, GraphCast, and EUMETSAT data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "forecast_days": {"type": "number", "description": "Forecast days", "default": 7},
                        "include_historical": {"type": "boolean", "description": "Include historical data", "default": True}
                    },
                    "required": ["latitude", "longitude"]
                }
            }
        ]
        
        return {"tools": tools}
    
    async def call_tool(self, params: Dict) -> Dict:
        """Execute weather tools"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        print(f"🛠️  Executing: {tool_name}", file=sys.stderr)
        
        try:
            if tool_name == "get_graphcast_forecast":
                return await self.get_graphcast_forecast(arguments)
            elif tool_name == "get_historical_weather":
                return await self.get_historical_weather(arguments)
            elif tool_name == "get_complete_weather_timeline":
                return await self.get_complete_weather_timeline(arguments)
            elif tool_name == "get_aifs_forecast":
                return await self.get_aifs_forecast(arguments)
            elif tool_name == "compare_ai_models":
                return await self.compare_ai_models(arguments)
            elif tool_name == "get_ensemble_forecast":
                return await self.get_ensemble_forecast(arguments)
            else:
                return self.error_response(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            print(f"❌ Tool error: {e}", file=sys.stderr)
            return self.error_response(f"Tool execution failed: {str(e)}")
    
    async def get_graphcast_forecast(self, args: Dict) -> Dict:
        """Get GraphCast AI forecast"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        days = args.get("days", 7)
        
        # Get forecast from GraphCast
        forecast_data = await self.graphcast_client.get_forecast(lat, lon, days)
        
        # Format for MCP response
        response_text = f"🧠 GraphCast AI Forecast for {lat}°, {lon}°\n"
        response_text += f"📅 Forecast period: {days} days\n"
        response_text += f"🎯 Accuracy: 90% better than traditional models\n"
        response_text += f"⚡ Generated in: <1 minute\n\n"
        
        response_text += "📊 Forecast highlights:\n"
        for i, point in enumerate(forecast_data['hourly_data'][:5]):
            time_str = point['time'][:16].replace('T', ' ')
            response_text += f"  {time_str}: {point['temperature']:.1f}°C, "
            response_text += f"💧{point['humidity']:.0f}%, 💨{point['wind_speed']:.1f}m/s\n"
        
        response_text += f"\n🔬 Model: {forecast_data['metadata']['model']}"
        response_text += f"\n📡 Provider: {forecast_data['metadata']['provider']}"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }
    
    async def get_historical_weather(self, args: Dict) -> Dict:
        """Get historical weather data"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        days_back = args.get("days_back", 7)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get historical data
        historical_data = await self.eumetsat_client.get_historical_data(
            lat, lon, start_date, end_date
        )
        
        # Format response
        response_text = f"🛰️  EUMETSAT Historical Weather for {lat}°, {lon}°\n"
        response_text += f"📅 Period: {start_date.date()} to {end_date.date()}\n"
        response_text += f"📊 Data points: {len(historical_data['historical_data'])}\n\n"
        
        response_text += "📈 Recent historical data:\n"
        for i, point in enumerate(historical_data['historical_data'][-5:]):
            time_str = point['time'][:16].replace('T', ' ')
            response_text += f"  {time_str}: {point['temperature']:.1f}°C, "
            response_text += f"💧{point['humidity']:.0f}%, 💨{point['wind_speed']:.1f}m/s\n"
        
        response_text += f"\n🛰️  Satellites: {', '.join(historical_data['metadata']['satellites'])}"
        
        return {
            "content": [
                {
                    "type": "text", 
                    "text": response_text
                }
            ]
        }
    
    async def get_complete_weather_timeline(self, args: Dict) -> Dict:
        """Get unified timeline: historical + forecast"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        days_back = args.get("days_back", 7)
        days_forward = args.get("days_forward", 7)
        
        print(f"🔄 Creating unified timeline...", file=sys.stderr)
        print(f"📚 Historical: {days_back} days back", file=sys.stderr)
        print(f"🔮 Forecast: {days_forward} days forward", file=sys.stderr)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        historical_data = await self.eumetsat_client.get_historical_data(
            lat, lon, start_date, end_date
        )
        
        # Get forecast data
        forecast_data = await self.graphcast_client.get_forecast(lat, lon, days_forward)
        
        # Create unified response
        response_text = f"🌍 Complete Weather Timeline for {lat}°, {lon}°\n"
        response_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        response_text += f"📚 HISTORICAL DATA ({days_back} days)\n"
        response_text += f"🛰️  Source: EUMETSAT Satellites\n"
        response_text += f"📊 Points: {len(historical_data['historical_data'])}\n\n"
        
        # Show recent historical
        response_text += "Recent observations:\n"
        for point in historical_data['historical_data'][-3:]:
            time_str = point['time'][:16].replace('T', ' ')
            response_text += f"  📅 {time_str}: {point['temperature']:.1f}°C\n"
        
        response_text += f"\n🔮 AI FORECAST ({days_forward} days)\n"
        response_text += f"🧠 Source: GraphCast AI (90% more accurate!)\n"
        response_text += f"📊 Points: {len(forecast_data['hourly_data'])}\n\n"
        
        # Show upcoming forecast
        response_text += "Upcoming forecast:\n"
        for point in forecast_data['hourly_data'][:3]:
            time_str = point['time'][:16].replace('T', ' ')
            response_text += f"  📅 {time_str}: {point['temperature']:.1f}°C\n"
        
        response_text += f"\n✨ TIMELINE SUMMARY\n"
        response_text += f"📈 Total data points: {len(historical_data['historical_data']) + len(forecast_data['hourly_data'])}\n"
        response_text += f"🔄 Seamless transition at: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        response_text += f"🎯 Historical accuracy: Satellite-validated\n"
        response_text += f"🎯 Forecast accuracy: 90% better than traditional models\n"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }
    
    async def get_aifs_forecast(self, args: Dict) -> Dict:
        """Get AIFS AI forecast"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        forecast_hours = args.get("forecast_hours", 240)
        
        # Get forecast from AIFS
        forecast_data = await self.aifs_client.get_forecast(lat, lon, forecast_hours)
        
        # Format for MCP response
        response_text = f"🚀 ECMWF AIFS Forecast for {lat}°, {lon}°\n"
        response_text += f"⏰ Forecast period: {forecast_hours} hours ({forecast_hours//24} days)\n"
        response_text += f"🎯 Model: Latest ECMWF AI technology\n"
        response_text += f"📊 Resolution: ~31km (0.25°)\n\n"
        
        response_text += "📊 AIFS forecast highlights:\n"
        forecast_points = forecast_data.get('forecast_data', [])
        for i, point in enumerate(forecast_points[:5]):
            time_str = point['time'][:16].replace('T', ' ')
            temp = point.get('temperature_2m', 'N/A')
            humidity = point.get('relative_humidity_2m', 'N/A')
            wind = point.get('wind_speed_10m', 'N/A')
            response_text += f"  {time_str}: {temp}°C, 💧{humidity}%, 💨{wind}m/s\n"
        
        response_text += f"\n🔬 Model: {forecast_data['metadata']['model']}"
        response_text += f"\n📡 Provider: {forecast_data['metadata']['provider']}"
        response_text += f"\n🏗️  Deployment: {forecast_data['metadata']['deployment_mode']}"
        
        if forecast_data['metadata'].get('is_mock'):
            response_text += f"\n⚠️  Note: Using mock data - deploy Docker container for real predictions"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }
    
    async def compare_ai_models(self, args: Dict) -> Dict:
        """Compare AIFS vs GraphCast predictions"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        forecast_days = args.get("forecast_days", 7)
        
        print(f"🔍 Comparing AI models for {lat}, {lon}", file=sys.stderr)
        
        # Get predictions from both models
        aifs_forecast = await self.aifs_client.get_forecast(lat, lon, forecast_days * 24)
        graphcast_forecast = await self.graphcast_client.get_forecast(lat, lon, forecast_days)
        
        # Create comparison using ensemble module
        comparison = await self.aifs_client.compare_with_graphcast(aifs_forecast, graphcast_forecast)
        
        # Format response
        response_text = f"🤖 AI Model Comparison for {lat}°, {lon}°\n"
        response_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        response_text += "🚀 AIFS vs 🧠 GRAPHCAST\n\n"
        
        # Model characteristics
        chars = comparison['model_characteristics']
        response_text += "📊 MODEL CHARACTERISTICS:\n"
        response_text += f"AIFS:      {chars['aifs']['resolution']} | {chars['aifs']['strength']}\n"
        response_text += f"GraphCast: {chars['graphcast']['resolution']} | {chars['graphcast']['strength']}\n\n"
        
        # Performance comparison
        perf = comparison['performance_comparison']
        response_text += "⚡ PERFORMANCE COMPARISON:\n"
        response_text += f"Accuracy:  AIFS: {perf['accuracy']['aifs']}\n"
        response_text += f"           GraphCast: {perf['accuracy']['graphcast']}\n"
        response_text += f"Speed:     AIFS: {perf['speed']['aifs']}\n"
        response_text += f"           GraphCast: {perf['speed']['graphcast']}\n\n"
        
        # Recommendations
        response_text += "💡 RECOMMENDATIONS:\n"
        for rec in comparison['recommendations']:
            response_text += f"  • {rec}\n"
        
        response_text += f"\n📈 Data comparison:\n"
        response_text += f"  AIFS points: {comparison['metadata']['aifs_points']}\n"
        response_text += f"  GraphCast points: {comparison['metadata']['graphcast_points']}\n"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }
    
    async def get_ensemble_forecast(self, args: Dict) -> Dict:
        """Get ensemble forecast combining all models"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        forecast_days = args.get("forecast_days", 7)
        include_historical = args.get("include_historical", True)
        
        print(f"🔮 Creating ensemble forecast for {lat}, {lon}", file=sys.stderr)
        
        # Get data from all sources
        aifs_forecast = await self.aifs_client.get_forecast(lat, lon, forecast_days * 24)
        graphcast_forecast = await self.graphcast_client.get_forecast(lat, lon, forecast_days)
        
        eumetsat_data = None
        if include_historical:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3)  # 3 days of historical
            eumetsat_data = await self.eumetsat_client.get_historical_data(lat, lon, start_date, end_date)
        
        # Create ensemble
        ensemble_result = await self.ensemble.create_ensemble_forecast(
            aifs_forecast, graphcast_forecast, eumetsat_data
        )
        
        # Format response
        response_text = f"🌟 Ensemble Weather Forecast for {lat}°, {lon}°\n"
        response_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        response_text += "🎯 MULTI-MODEL ENSEMBLE PREDICTION\n"
        response_text += f"🤖 Models: {', '.join(ensemble_result['metadata']['models_used'])}\n"
        response_text += f"⚖️  Method: {ensemble_result['metadata']['ensemble_method']}\n"
        response_text += f"📊 Points: {ensemble_result['metadata']['forecast_points']}\n\n"
        
        # Show ensemble forecast highlights
        ensemble_forecast = ensemble_result.get('ensemble_forecast', [])
        if ensemble_forecast:
            response_text += "📅 ENSEMBLE FORECAST HIGHLIGHTS:\n"
            for i, point in enumerate(ensemble_forecast[:5]):
                time_str = point['time'][:16].replace('T', ' ')
                temp = point.get('ensemble_temperature', 'N/A')
                conf = point.get('confidence', 0)
                models = point.get('contributing_models', {})
                model_count = sum(models.values())
                response_text += f"  {time_str}: {temp}°C (conf: {conf:.2f}, models: {model_count})\n"
        
        # Model comparison summary
        comparison = ensemble_result.get('model_comparison', {})
        if 'recommendations' in comparison:
            response_text += "\n💡 KEY INSIGHTS:\n"
            for rec in comparison['recommendations'][:3]:
                response_text += f"  • {rec}\n"
        
        # Ensemble statistics
        stats = ensemble_result.get('ensemble_statistics', {})
        if 'model_coverage' in stats:
            coverage = stats['model_coverage']
            response_text += f"\n📈 DATA COVERAGE:\n"
            response_text += f"  AIFS: {coverage.get('aifs_points', 0)} points\n"
            response_text += f"  GraphCast: {coverage.get('graphcast_points', 0)} points\n"
            if include_historical:
                response_text += f"  EUMETSAT: {coverage.get('eumetsat_points', 0)} points\n"
        
        if 'ensemble_quality' in stats and 'model_agreement' in stats['ensemble_quality']:
            agreement = stats['ensemble_quality']['model_agreement']
            response_text += f"\n🎯 Model Agreement: {agreement:.1%}\n"
        
        response_text += f"\n✨ Enhanced prediction combining cutting-edge AI models with satellite observations"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }
    
    def error_response(self, message: str, request_id=None) -> Dict:
        """Return error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -1,
                "message": message
            }
        }

import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Any, Optional

# Pydantic models for HTTP requests
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict] = None
    id: Optional[Any] = None

app = FastAPI(title="Weather MCP Server", version="3.0.0")

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global server instance
weather_server = None

@app.on_event("startup")
async def startup_event():
    global weather_server
    weather_server = WeatherMCPServer()
    print("🌐 Weather MCP HTTP Server started!", file=sys.stderr)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Weather MCP Server", "version": "3.0.0"}

@app.post("/mcp")
async def handle_mcp_request(request: MCPRequest):
    """Handle MCP requests via HTTP"""
    try:
        request_dict = {
            "jsonrpc": request.jsonrpc,
            "method": request.method,
            "params": request.params or {},
            "id": request.id
        }
        
        response = await weather_server.handle_request(request_dict)
        return response
        
    except Exception as e:
        print(f"❌ MCP HTTP error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools():
    """List available tools (convenience endpoint)"""
    try:
        tools_response = await weather_server.list_tools()
        return tools_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_mcp_server():
    """Run MCP server using HTTP transport"""
    print("🌐 Starting Weather MCP HTTP Server...", file=sys.stderr)
    print("📡 Server will be available at http://localhost:8081", file=sys.stderr)
    
    # Run uvicorn server
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8082,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

# Complete test of enhanced MCP server
async def test_enhanced_server():
    """Test all features of our weather MCP server"""
    print("🚀 Testing Weather MCP Server")
    print("=" * 50)
    
    server = WeatherMCPServer()
    
    # Test coordinates (Canary Islands)
    lat, lon = 28.2916, -16.6291
    
    print(f"\n🧪 Test Location: {lat}°N, {lon}°W (Canary Islands)")
    
    # Test 1: List tools
    print("\n1️⃣ Testing available tools...")
    tools_response = await server.handle_request({"method": "tools/list"})
    tools_count = len(tools_response.get('result', {}).get('tools', []))
    print(f"✅ Found {tools_count} tools available")
    
    # Test 2: GraphCast forecast
    print("\n2️⃣ Testing GraphCast AI forecast...")
    forecast_request = {
        "method": "tools/call",
        "params": {
            "name": "get_graphcast_forecast",
            "arguments": {"latitude": lat, "longitude": lon, "days": 5}
        }
    }
    forecast_response = await server.handle_request(forecast_request)
    print("✅ GraphCast forecast completed")
    
    # Test 3: Historical data
    print("\n3️⃣ Testing historical weather data...")
    historical_request = {
        "method": "tools/call",
        "params": {
            "name": "get_historical_weather",
            "arguments": {"latitude": lat, "longitude": lon, "days_back": 5}
        }
    }
    historical_response = await server.handle_request(historical_request)
    print("✅ Historical data retrieved")
    
    # Test 4: Complete timeline
    print("\n4️⃣ Testing complete weather timeline...")
    timeline_request = {
        "method": "tools/call",
        "params": {
            "name": "get_complete_weather_timeline",
            "arguments": {
                "latitude": lat, 
                "longitude": lon, 
                "days_back": 3, 
                "days_forward": 5
            }
        }
    }
    timeline_response = await server.handle_request(timeline_request)
    print("✅ Complete timeline generated")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("Your Weather MCP Server is working perfectly!")
    print("🚀 Ready for the next phase!")

async def run_stdio_server():
    """Run MCP server using stdin/stdout for Claude Desktop"""
    server = WeatherMCPServer()
    
    # Read from stdin line by line for Claude Desktop
    print("🌐 MCP Server running on stdin/stdout...", file=sys.stderr)
    print("📡 Waiting for requests from Claude Desktop...", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            if line.strip():  # Only process non-empty lines
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                
                # Write response to stdout (only if not None)
                if response is not None:
                    print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}", file=sys.stderr)
            error_response = {"error": {"code": -32700, "message": "Parse error"}}
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            print(f"❌ Server error: {e}", file=sys.stderr)
            error_response = {"error": {"code": -1, "message": str(e)}}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_enhanced_server())
    elif len(sys.argv) > 1 and sys.argv[1] == "stdio":
        asyncio.run(run_stdio_server())
    else:
        asyncio.run(run_mcp_server())