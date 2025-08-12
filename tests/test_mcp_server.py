"""
Unit tests for Weather MCP Server
"""

import pytest
import asyncio

@pytest.mark.asyncio
async def test_mcp_server_initialization(weather_server):
    """Test MCP server initialization"""
    assert weather_server.name == "Weather MCP"
    assert weather_server.version == "3.0.0"
    assert hasattr(weather_server, 'aifs_client')
    assert hasattr(weather_server, 'graphcast_client')
    assert hasattr(weather_server, 'eumetsat_client')
    assert hasattr(weather_server, 'ensemble')

@pytest.mark.asyncio
async def test_tools_list(weather_server):
    """Test MCP tools list functionality"""
    request = {"method": "tools/list", "id": 1}
    response = await weather_server.handle_request(request)
    
    assert "result" in response
    assert "tools" in response["result"]
    
    tools = response["result"]["tools"]
    expected_tools = [
        "get_graphcast_forecast",
        "get_historical_weather", 
        "get_complete_weather_timeline",
        "get_aifs_forecast",
        "compare_ai_models",
        "get_ensemble_forecast"
    ]
    
    tool_names = [tool["name"] for tool in tools]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names

@pytest.mark.asyncio
async def test_aifs_forecast_tool(weather_server, canary_islands_coords):
    """Test AIFS forecast tool via MCP"""
    request = {
        "method": "tools/call",
        "id": 2,
        "params": {
            "name": "get_aifs_forecast",
            "arguments": {
                "latitude": canary_islands_coords["lat"],
                "longitude": canary_islands_coords["lon"],
                "forecast_hours": 72
            }
        }
    }
    
    response = await weather_server.handle_request(request)
    
    assert "result" in response
    assert "content" in response["result"]
    assert len(response["result"]["content"]) > 0
    
    content = response["result"]["content"][0]
    assert content["type"] == "text"
    assert "AIFS Forecast" in content["text"]
    assert str(canary_islands_coords["lat"]) in content["text"]

@pytest.mark.asyncio
async def test_model_comparison_tool(weather_server, canary_islands_coords):
    """Test AI model comparison tool"""
    request = {
        "method": "tools/call",
        "id": 3,
        "params": {
            "name": "compare_ai_models",
            "arguments": {
                "latitude": canary_islands_coords["lat"],
                "longitude": canary_islands_coords["lon"],
                "forecast_days": 3
            }
        }
    }
    
    response = await weather_server.handle_request(request)
    
    assert "result" in response
    assert "content" in response["result"]
    
    content = response["result"]["content"][0]
    assert content["type"] == "text"
    assert "AI Model Comparison" in content["text"]
    assert "AIFS" in content["text"]
    assert "GraphCast" in content["text"]

@pytest.mark.asyncio
async def test_ensemble_forecast_tool(weather_server, canary_islands_coords):
    """Test ensemble forecast tool"""
    request = {
        "method": "tools/call",
        "id": 4,
        "params": {
            "name": "get_ensemble_forecast",
            "arguments": {
                "latitude": canary_islands_coords["lat"],
                "longitude": canary_islands_coords["lon"],
                "forecast_days": 3,
                "include_historical": True
            }
        }
    }
    
    response = await weather_server.handle_request(request)
    
    assert "result" in response
    assert "content" in response["result"]
    
    content = response["result"]["content"][0]
    assert content["type"] == "text"
    assert "Ensemble Weather Forecast" in content["text"]
    assert "MULTI-MODEL" in content["text"]

@pytest.mark.asyncio
async def test_invalid_tool_call(weather_server):
    """Test handling of invalid tool calls"""
    request = {
        "method": "tools/call",
        "id": 5,
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        }
    }
    
    response = await weather_server.handle_request(request)
    
    assert "result" in response
    assert "error" in response["result"]
    assert response["result"]["error"]["code"] == -1
    assert "Unknown tool" in response["result"]["error"]["message"]

@pytest.mark.asyncio
async def test_invalid_method(weather_server):
    """Test handling of invalid methods"""
    request = {
        "method": "invalid/method",
        "id": 6
    }
    
    response = await weather_server.handle_request(request)
    
    assert "error" in response
    assert response["error"]["code"] == -32601
    assert "Method not found" in response["error"]["message"]