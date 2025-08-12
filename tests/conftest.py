"""
Pytest configuration and fixtures for Weather MCP Server tests
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def canary_islands_coords():
    """Standard test coordinates for Canary Islands"""
    return {"lat": 28.2916, "lon": -16.6291, "name": "Canary Islands"}

@pytest.fixture
def test_forecast_hours():
    """Standard test forecast hours"""
    return 72  # 3 days

@pytest.fixture
def test_forecast_days():
    """Standard test forecast days"""
    return 7

@pytest.fixture
def weather_server():
    """Weather MCP Server instance for testing"""
    from weather_mcp.mcp_server import WeatherMCPServer
    return WeatherMCPServer()

@pytest.fixture
def aifs_client():
    """AIFS client for testing"""
    from weather_mcp.aifs_client import AIFSClient
    return AIFSClient()

@pytest.fixture
def graphcast_client():
    """GraphCast client for testing"""
    from weather_mcp.graphcast_client import GraphCastClient
    return GraphCastClient()

@pytest.fixture
def prediction_ensemble():
    """Prediction ensemble for testing"""
    from weather_mcp.prediction_ensemble import PredictionEnsemble
    return PredictionEnsemble()