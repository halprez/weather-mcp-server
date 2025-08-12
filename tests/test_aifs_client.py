"""
Unit tests for AIFS Client
"""

import pytest
import asyncio
from datetime import datetime

@pytest.mark.asyncio
async def test_aifs_client_initialization(aifs_client):
    """Test AIFS client initialization"""
    assert aifs_client.deployment_mode in ["docker", "local"]
    assert aifs_client.docker_url == "http://localhost:8080"
    assert aifs_client.model_name == "ecmwf/aifs-single-1.0"

@pytest.mark.asyncio
async def test_aifs_forecast_request(aifs_client, canary_islands_coords, test_forecast_hours):
    """Test AIFS forecast request"""
    forecast = await aifs_client.get_forecast(
        canary_islands_coords["lat"],
        canary_islands_coords["lon"],
        test_forecast_hours
    )
    
    # Check response structure
    assert "location" in forecast
    assert "forecast_data" in forecast
    assert "metadata" in forecast
    
    # Check location data
    assert forecast["location"]["latitude"] == canary_islands_coords["lat"]
    assert forecast["location"]["longitude"] == canary_islands_coords["lon"]
    
    # Check metadata
    assert forecast["metadata"]["model"] == "AIFS Single v1.0"
    assert forecast["metadata"]["provider"] == "ECMWF"
    assert "deployment_mode" in forecast["metadata"]
    
    # Check forecast data
    assert len(forecast["forecast_data"]) > 0
    
    # Check first forecast point structure
    first_point = forecast["forecast_data"][0]
    assert "time" in first_point
    assert "forecast_hour" in first_point
    
    # Verify timestamp format
    datetime.fromisoformat(first_point["time"].replace("Z", "+00:00"))

@pytest.mark.asyncio
async def test_aifs_mock_data_generation(aifs_client, canary_islands_coords):
    """Test AIFS mock data generation"""
    # This will use mock data since Docker container likely isn't running
    forecast = await aifs_client.get_forecast(
        canary_islands_coords["lat"],
        canary_islands_coords["lon"],
        72  # 3 days
    )
    
    # Should generate reasonable number of forecast points (every 6 hours)
    expected_points = (72 // 6) + 1  # +1 for hour 0
    assert len(forecast["forecast_data"]) == expected_points
    
    # Check that forecast values are realistic
    for point in forecast["forecast_data"]:
        if point.get("temperature_2m") is not None:
            # Temperature should be reasonable for Canary Islands
            assert -10 <= point["temperature_2m"] <= 50
        
        if point.get("relative_humidity_2m") is not None:
            # Humidity should be 0-100%
            assert 0 <= point["relative_humidity_2m"] <= 100
        
        if point.get("surface_pressure") is not None:
            # Pressure should be reasonable (hPa)
            assert 950 <= point["surface_pressure"] <= 1050