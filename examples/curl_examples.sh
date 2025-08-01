#!/bin/bash
#
# Curl Examples for Weather MCP HTTP Transport
#
# These examples show how to interact with the Weather MCP server
# using standard HTTP tools like curl.
#

BASE_URL="http://localhost:8000"

echo "🌍 Weather MCP HTTP Transport - Curl Examples"
echo "=============================================="

# Check if server is running
echo -e "\n1️⃣ Health Check"
echo "curl -X GET $BASE_URL/health"
curl -X GET "$BASE_URL/health" | jq '.' 2>/dev/null || curl -X GET "$BASE_URL/health"

echo -e "\n\n2️⃣ Server Information"
echo "curl -X GET $BASE_URL/info"
curl -X GET "$BASE_URL/info" | jq '.' 2>/dev/null || curl -X GET "$BASE_URL/info"

echo -e "\n\n3️⃣ Initialize MCP Connection"
echo "curl -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {"tools": {}},
      "clientInfo": {"name": "curl-client", "version": "1.0.0"}
    }
  }' | jq '.' 2>/dev/null || curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {"tools": {}},
      "clientInfo": {"name": "curl-client", "version": "1.0.0"}
    }
  }'

echo -e "\n\n4️⃣ List Available Tools"
echo "curl -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }' | jq '.' 2>/dev/null || curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'

echo -e "\n\n5️⃣ Get GraphCast Weather Forecast"
echo "curl -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_graphcast_forecast",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days": 3
      }
    }
  }' | jq '.' 2>/dev/null || curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_graphcast_forecast",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days": 3
      }
    }
  }'

echo -e "\n\n6️⃣ Get Historical Weather Data"
echo "curl -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_historical_weather",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days_back": 5
      }
    }
  }' | jq '.' 2>/dev/null || curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_historical_weather",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days_back": 5
      }
    }
  }'

echo -e "\n\n7️⃣ Get Complete Weather Timeline"
echo "curl -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "get_complete_weather_timeline",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days_back": 3,
        "days_forward": 5
      }
    }
  }' | jq '.' 2>/dev/null || curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "get_complete_weather_timeline",
      "arguments": {
        "latitude": 28.2916,
        "longitude": -16.6291,
        "days_back": 3,
        "days_forward": 5
      }
    }
  }'

echo -e "\n\n✅ All examples completed!"
echo -e "\n💡 Usage:"
echo "  1. Start the server: python -m weather_mcp.http_server"
echo "  2. Run these examples: chmod +x curl_examples.sh && ./curl_examples.sh"
echo "  3. Use jq for pretty JSON formatting: sudo apt install jq  # or brew install jq"