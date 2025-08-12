"""
AIFS Client for ECMWF AI Forecasting System
Connect to AIFS model via anemoi-inference or Docker container
"""

import asyncio
import sys
import aiohttp
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
import tempfile
import os
from pathlib import Path

class AIFSClient:
    """
    AIFS (AI Forecasting System) Client
    
    Supports two deployment modes:
    1. Local anemoi-inference package
    2. Docker container with AIFS model
    """
    
    def __init__(self, deployment_mode: str = "docker", docker_url: str = "http://localhost:8080"):
        self.deployment_mode = deployment_mode
        self.docker_url = docker_url
        self.model_name = "ecmwf/aifs-single-1.0"
        print(f"🧠 AIFS Client initialized (mode: {deployment_mode})", file=sys.stderr)
        
        # Check if anemoi-inference is available for local mode
        if deployment_mode == "local":
            try:
                import anemoi.inference
                self.anemoi_available = True
                print("✅ anemoi-inference package found", file=sys.stderr)
            except ImportError:
                print("⚠️  anemoi-inference not available, switching to docker mode", file=sys.stderr)
                self.deployment_mode = "docker"
                self.anemoi_available = False
        
    async def get_forecast(self, 
                          latitude: float, 
                          longitude: float, 
                          forecast_hours: int = 240) -> Dict:
        """
        Get AIFS forecast
        
        Args:
            latitude: Location latitude
            longitude: Location longitude  
            forecast_hours: Forecast horizon in hours (default: 240h = 10 days)
            
        Returns:
            Dictionary with AIFS forecast data
        """
        print(f"🔍 Getting AIFS forecast for {latitude}, {longitude}", file=sys.stderr)
        
        if self.deployment_mode == "docker":
            return await self._get_docker_forecast(latitude, longitude, forecast_hours)
        else:
            return await self._get_local_forecast(latitude, longitude, forecast_hours)
    
    async def _get_docker_forecast(self, lat: float, lon: float, hours: int) -> Dict:
        """Get forecast from Docker container"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "latitude": lat,
                    "longitude": lon,
                    "forecast_hours": hours,
                    "model": "aifs-single-1.0"
                }
                
                async with session.post(
                    f"{self.docker_url}/forecast",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 min timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_aifs_response(data, lat, lon)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Docker API error {response.status}: {error_text}")
                        
        except aiohttp.ClientConnectorError:
            print("❌ Docker container not reachable, returning mock data", file=sys.stderr)
            return await self._get_mock_forecast(lat, lon, hours)
        except Exception as e:
            print(f"❌ AIFS Docker error: {e}", file=sys.stderr)
            return await self._get_mock_forecast(lat, lon, hours)
    
    async def _get_local_forecast(self, lat: float, lon: float, hours: int) -> Dict:
        """Get forecast using local anemoi-inference"""
        try:
            # This would use anemoi-inference directly
            # For now, we'll use a subprocess call to anemoi-inference CLI
            
            # Create temporary config file
            config = {
                "input": {
                    "source": "opendata",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "time": "00:00:00"
                },
                "output": {
                    "location": {"latitude": lat, "longitude": lon},
                    "forecast_hours": hours
                },
                "model": {
                    "checkpoint": self.model_name
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                import yaml
                yaml.dump(config, f)
                config_path = f.name
            
            try:
                # Run anemoi-inference CLI
                result = subprocess.run([
                    "anemoi-inference", "run", 
                    "--config", config_path,
                    "--output", "/tmp/aifs_forecast.nc"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Process NetCDF output
                    return await self._process_netcdf_output("/tmp/aifs_forecast.nc", lat, lon)
                else:
                    print(f"❌ anemoi-inference error: {result.stderr}", file=sys.stderr)
                    return await self._get_mock_forecast(lat, lon, hours)
                    
            finally:
                os.unlink(config_path)
                
        except Exception as e:
            print(f"❌ Local AIFS error: {e}", file=sys.stderr)
            return await self._get_mock_forecast(lat, lon, hours)
    
    async def _get_mock_forecast(self, lat: float, lon: float, hours: int) -> Dict:
        """Generate mock AIFS forecast for testing"""
        print("🧪 Generating mock AIFS forecast", file=sys.stderr)
        
        # Generate realistic mock data with hourly resolution
        start_time = datetime.utcnow()
        forecast_data = []
        
        for hour in range(0, hours + 1, 6):  # 6-hourly output like real AIFS
            timestamp = start_time + timedelta(hours=hour)
            
            # Generate realistic weather values with some variation
            base_temp = 20 + 5 * np.sin(hour * np.pi / 24)  # Daily temperature cycle
            temp_noise = np.random.normal(0, 2)  # Some randomness
            
            forecast_point = {
                "time": timestamp.isoformat(),
                "temperature_2m": round(base_temp + temp_noise, 1),
                "relative_humidity_2m": round(65 + np.random.normal(0, 10), 1),
                "surface_pressure": round(1013 + np.random.normal(0, 5), 1),
                "wind_speed_10m": round(abs(np.random.normal(10, 3)), 1),
                "wind_direction_10m": round(np.random.uniform(0, 360), 1),
                "precipitation": round(max(0, np.random.exponential(0.5)), 2),
                "forecast_hour": hour
            }
            
            forecast_data.append(forecast_point)
        
        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "elevation": 0  # Would be derived from model
            },
            "forecast_data": forecast_data,
            "metadata": {
                "model": "AIFS Single v1.0",
                "provider": "ECMWF",
                "resolution": "~31km (0.25°)",
                "forecast_horizon_hours": hours,
                "accuracy": "Advanced AI model from ECMWF",
                "generated_at": datetime.now().isoformat(),
                "is_mock": True,
                "deployment_mode": self.deployment_mode
            }
        }
    
    def _process_aifs_response(self, data: Dict, lat: float, lon: float) -> Dict:
        """Process response from AIFS Docker container"""
        # Transform Docker API response to consistent format
        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "elevation": data.get("elevation", 0)
            },
            "forecast_data": data.get("forecast", []),
            "metadata": {
                "model": "AIFS Single v1.0",
                "provider": "ECMWF",
                "resolution": "~31km (0.25°)",
                "accuracy": "Advanced AI model from ECMWF",
                "generated_at": datetime.now().isoformat(),
                "deployment_mode": self.deployment_mode,
                "is_mock": False
            }
        }
    
    async def _process_netcdf_output(self, filepath: str, lat: float, lon: float) -> Dict:
        """Process NetCDF output from anemoi-inference"""
        try:
            import xarray as xr
            
            # Load NetCDF file
            ds = xr.open_dataset(filepath)
            
            # Extract forecast data (this would need to match AIFS output format)
            forecast_data = []
            
            for time_idx in range(len(ds.time)):
                timestamp = ds.time[time_idx].values
                
                forecast_point = {
                    "time": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
                    "temperature_2m": float(ds.t2m[time_idx].values) if 't2m' in ds else None,
                    "surface_pressure": float(ds.sp[time_idx].values) if 'sp' in ds else None,
                    "wind_speed_10m": float(ds.si10[time_idx].values) if 'si10' in ds else None,
                    # Add more variables as available in AIFS output
                    "forecast_hour": time_idx * 6  # AIFS typically outputs 6-hourly
                }
                
                forecast_data.append(forecast_point)
            
            ds.close()
            
            return {
                "location": {"latitude": lat, "longitude": lon},
                "forecast_data": forecast_data,
                "metadata": {
                    "model": "AIFS Single v1.0",
                    "provider": "ECMWF",
                    "deployment_mode": "local",
                    "generated_at": datetime.now().isoformat(),
                    "is_mock": False
                }
            }
            
        except Exception as e:
            print(f"❌ NetCDF processing error: {e}", file=sys.stderr)
            return await self._get_mock_forecast(lat, lon, 240)
    
    async def compare_with_graphcast(self, 
                                   aifs_forecast: Dict, 
                                   graphcast_forecast: Dict) -> Dict:
        """
        Compare AIFS and GraphCast predictions
        
        Args:
            aifs_forecast: AIFS forecast data
            graphcast_forecast: GraphCast forecast data
            
        Returns:
            Comparison analysis
        """
        print("🔍 Comparing AIFS vs GraphCast forecasts", file=sys.stderr)
        
        comparison = {
            "models_compared": ["AIFS Single v1.0", "GraphCast"],
            "comparison_metrics": {},
            "recommendations": [],
            "metadata": {
                "compared_at": datetime.now().isoformat(),
                "aifs_points": len(aifs_forecast.get("forecast_data", [])),
                "graphcast_points": len(graphcast_forecast.get("hourly_data", []))
            }
        }
        
        # Basic comparison logic
        if aifs_forecast.get("metadata", {}).get("is_mock") and not graphcast_forecast.get("metadata", {}).get("is_mock", True):
            comparison["recommendations"].append("GraphCast data is live, AIFS is mock - prefer GraphCast")
        elif not aifs_forecast.get("metadata", {}).get("is_mock") and graphcast_forecast.get("metadata", {}).get("is_mock", True):
            comparison["recommendations"].append("AIFS data is live, GraphCast is mock - prefer AIFS")
        else:
            comparison["recommendations"].append("Both models available - ensemble prediction recommended")
        
        # Add specific model characteristics
        comparison["model_characteristics"] = {
            "aifs": {
                "resolution": "~31km",
                "update_frequency": "4x daily",
                "forecast_horizon": "10+ days",
                "strength": "ECMWF AI technology",
                "strengths": ["High accuracy", "Fast inference", "ECMWF developed"]
            },
            "graphcast": {
                "resolution": "~28km (0.25°)",
                "update_frequency": "4x daily", 
                "forecast_horizon": "10+ days",
                "strength": "Google DeepMind AI",
                "strengths": ["Google AI", "Open source", "Proven performance"]
            }
        }
        
        # Add performance comparison
        comparison["performance_comparison"] = {
            "accuracy": {
                "aifs": "State-of-the-art ECMWF",
                "graphcast": "90% better than traditional"
            },
            "speed": {
                "aifs": "30-60 seconds",
                "graphcast": "<1 minute"
            }
        }
        
        return comparison

# Test the AIFS client
async def test_aifs_client():
    """Test our AIFS client"""
    print("🧪 Testing AIFS Client")
    print("=" * 40)
    
    # Test both deployment modes
    for mode in ["docker", "local"]:
        print(f"\n🔧 Testing {mode} mode...")
        print("-" * 30)
        
        client = AIFSClient(deployment_mode=mode)
        
        # Canary Islands test location
        lat, lon = 28.2916, -16.6291
        
        try:
            # Get AIFS forecast
            forecast = await client.get_forecast(lat, lon, forecast_hours=168)  # 7 days
            
            print("✅ AIFS forecast received!")
            print(f"📍 Location: {forecast['location']['latitude']}, {forecast['location']['longitude']}")
            print(f"📊 Forecast points: {len(forecast['forecast_data'])}")
            print(f"🤖 Model: {forecast['metadata']['model']}")
            print(f"🏗️  Deployment: {forecast['metadata']['deployment_mode']}")
            print(f"🧪 Mock data: {forecast['metadata'].get('is_mock', 'unknown')}")
            
            # Show first few forecast points
            print("\n📅 Sample forecast data:")
            for i, point in enumerate(forecast['forecast_data'][:3]):
                print(f"  Hour {point.get('forecast_hour', i*6)}: "
                     f"🌡️  {point.get('temperature_2m', 'N/A')}°C | "
                     f"💨 {point.get('wind_speed_10m', 'N/A')} m/s | "
                     f"💧 {point.get('precipitation', 'N/A')} mm")
                
        except Exception as e:
            print(f"❌ Test failed for {mode} mode: {e}")

if __name__ == "__main__":
    asyncio.run(test_aifs_client())