"""
AIFS Model Server
FastAPI server that serves AIFS model predictions via HTTP API
Runs inside Docker container for scalable deployment
"""

import asyncio
import os
import sys
import json
import tempfile
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import numpy as np
import xarray as xr
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

class ForecastRequest(BaseModel):
    latitude: float
    longitude: float
    forecast_hours: int = 240
    model: str = "aifs-single-1.0"

class ForecastResponse(BaseModel):
    latitude: float
    longitude: float
    forecast: List[Dict]
    metadata: Dict

app = FastAPI(
    title="AIFS Model Server",
    description="ECMWF AI Forecasting System API",
    version="1.0.0"
)

class AIFSModelServer:
    """AIFS model server implementation"""
    
    def __init__(self):
        self.model_cache = {}
        self.inference_engine = None
        self.model_ready = False
        logger.info("🚀 AIFS Model Server initializing...")
        
    async def initialize_model(self):
        """Initialize the AIFS model"""
        try:
            logger.info("🔄 Loading AIFS model...")
            
            # Check if anemoi-inference is available
            try:
                import anemoi.inference
                self.has_anemoi = True
                logger.info("✅ anemoi-inference package found")
            except ImportError:
                self.has_anemoi = False
                logger.warning("⚠️ anemoi-inference not available, using mock mode")
                
            # In production, you would initialize the actual model here
            # For now, we'll set up the infrastructure
            
            self.model_ready = True
            logger.info("✅ AIFS model server ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AIFS model: {e}")
            self.model_ready = False
    
    async def generate_forecast(self, request: ForecastRequest) -> Dict:
        """Generate AIFS forecast"""
        if not self.model_ready:
            raise HTTPException(status_code=503, detail="Model not ready")
            
        logger.info(f"🔮 Generating forecast for {request.latitude}, {request.longitude}")
        
        if self.has_anemoi:
            return await self._generate_real_forecast(request)
        else:
            return await self._generate_mock_forecast(request)
    
    async def _generate_real_forecast(self, request: ForecastRequest) -> Dict:
        """Generate forecast using real AIFS model"""
        try:
            # Create configuration for anemoi-inference
            config = {
                "input": {
                    "source": "opendata",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "time": "00:00:00"
                },
                "output": {
                    "path": "/tmp/aifs_forecast.nc",
                    "location": {
                        "latitude": request.latitude,
                        "longitude": request.longitude
                    }
                },
                "model": {
                    "checkpoint": f"ecmwf/{request.model}"
                },
                "forecast": {
                    "horizon_hours": request.forecast_hours
                }
            }
            
            # Save config to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f)
                config_path = f.name
            
            try:
                # Run inference
                import subprocess
                result = subprocess.run([
                    "anemoi-inference", "run",
                    "--config", config_path
                ], capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    # Process NetCDF output
                    forecast_data = await self._process_netcdf_output("/tmp/aifs_forecast.nc")
                    return {
                        "latitude": request.latitude,
                        "longitude": request.longitude,
                        "forecast": forecast_data,
                        "metadata": {
                            "model": request.model,
                            "provider": "ECMWF",
                            "generated_at": datetime.now().isoformat(),
                            "forecast_hours": request.forecast_hours,
                            "is_real": True
                        }
                    }
                else:
                    logger.error(f"anemoi-inference failed: {result.stderr}")
                    return await self._generate_mock_forecast(request)
                    
            finally:
                os.unlink(config_path)
                
        except Exception as e:
            logger.error(f"Real forecast generation failed: {e}")
            return await self._generate_mock_forecast(request)
    
    async def _generate_mock_forecast(self, request: ForecastRequest) -> Dict:
        """Generate mock forecast for testing"""
        logger.info("🧪 Generating mock AIFS forecast")
        
        start_time = datetime.utcnow()
        forecast_data = []
        
        # Generate forecast points every 6 hours (typical AIFS output)
        for hour in range(0, request.forecast_hours + 1, 6):
            timestamp = start_time + timedelta(hours=hour)
            
            # Generate realistic weather values
            base_temp = 20 + 8 * np.sin(hour * np.pi / 24)  # Daily cycle
            temp_variation = np.random.normal(0, 2)
            
            forecast_point = {
                "time": timestamp.isoformat(),
                "forecast_hour": hour,
                "temperature_2m": round(base_temp + temp_variation, 1),
                "relative_humidity_2m": round(max(20, min(95, 65 + np.random.normal(0, 15))), 1),
                "surface_pressure": round(1013 + np.random.normal(0, 8), 1),
                "wind_speed_10m": round(abs(np.random.normal(8, 4)), 1),
                "wind_direction_10m": round(np.random.uniform(0, 360), 1),
                "precipitation": round(max(0, np.random.exponential(0.3)), 2),
                "geopotential_500": round(5500 + np.random.normal(0, 50), 1),
                "temperature_850": round(base_temp - 12 + temp_variation, 1)
            }
            
            forecast_data.append(forecast_point)
        
        return {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "forecast": forecast_data,
            "metadata": {
                "model": request.model,
                "provider": "ECMWF",
                "generated_at": datetime.now().isoformat(),
                "forecast_hours": request.forecast_hours,
                "is_real": False,
                "note": "Mock data for testing"
            }
        }
    
    async def _process_netcdf_output(self, filepath: str) -> List[Dict]:
        """Process NetCDF output from AIFS model"""
        try:
            ds = xr.open_dataset(filepath)
            forecast_data = []
            
            # Extract variables (adjust based on actual AIFS output)
            for time_idx in range(len(ds.time)):
                timestamp = ds.time[time_idx].values
                
                point = {
                    "time": pd.Timestamp(timestamp).isoformat(),
                    "forecast_hour": time_idx * 6,  # Assuming 6-hourly output
                }
                
                # Extract available variables
                if 't2m' in ds:
                    point["temperature_2m"] = float(ds.t2m[time_idx].values)
                if 'sp' in ds:
                    point["surface_pressure"] = float(ds.sp[time_idx].values)
                if 'si10' in ds:
                    point["wind_speed_10m"] = float(ds.si10[time_idx].values)
                if 'tp' in ds:
                    point["precipitation"] = float(ds.tp[time_idx].values)
                    
                forecast_data.append(point)
            
            ds.close()
            return forecast_data
            
        except Exception as e:
            logger.error(f"NetCDF processing error: {e}")
            return []

# Global server instance
aifs_server = AIFSModelServer()

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    await aifs_server.initialize_model()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if aifs_server.model_ready else "not_ready",
        "model_ready": aifs_server.model_ready,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "AIFS Model Server",
        "version": "1.0.0",
        "model": "ECMWF AIFS Single v1.0",
        "endpoints": {
            "/forecast": "POST - Generate weather forecast",
            "/health": "GET - Health check",
            "/models": "GET - List available models"
        }
    }

@app.get("/models")
async def list_models():
    """List available AIFS models"""
    return {
        "available_models": [
            {
                "id": "aifs-single-1.0",
                "name": "AIFS Single v1.0",
                "description": "ECMWF AI Forecasting System - Single model",
                "resolution": "~31km (0.25°)",
                "forecast_horizon": "10+ days",
                "update_frequency": "4x daily"
            }
        ]
    }

@app.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest, background_tasks: BackgroundTasks):
    """Generate AIFS weather forecast"""
    try:
        logger.info(f"📥 Forecast request: {request.latitude}, {request.longitude}")
        
        # Validate coordinates
        if not (-90 <= request.latitude <= 90):
            raise HTTPException(status_code=400, detail="Invalid latitude")
        if not (-180 <= request.longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid longitude")
        if not (1 <= request.forecast_hours <= 720):  # Max 30 days
            raise HTTPException(status_code=400, detail="Invalid forecast hours")
        
        # Generate forecast
        result = await aifs_server.generate_forecast(request)
        
        logger.info(f"✅ Forecast generated: {len(result['forecast'])} points")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Forecast generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@app.get("/forecast/{latitude}/{longitude}")
async def get_forecast_get(latitude: float, longitude: float, hours: int = 240):
    """GET endpoint for quick forecasts"""
    request = ForecastRequest(latitude=latitude, longitude=longitude, forecast_hours=hours)
    return await generate_forecast(request, BackgroundTasks())

if __name__ == "__main__":
    logger.info("🌟 Starting AIFS Model Server...")
    uvicorn.run(
        "aifs_server:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False
    )