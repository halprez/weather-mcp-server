"""
Prediction Ensemble and Comparison Module
Combines AIFS, GraphCast, and EUMETSAT data for enhanced forecasts
"""

import asyncio
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import statistics

@dataclass
class WeatherPrediction:
    """Standardized weather prediction data structure"""
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    precipitation: Optional[float]
    source: str
    confidence: float = 1.0
    forecast_hour: int = 0

class PredictionEnsemble:
    """
    Advanced prediction ensemble that combines multiple weather models
    """
    
    def __init__(self):
        self.model_weights = {
            "aifs": 0.4,        # ECMWF's newest AI model
            "graphcast": 0.35,  # Google's proven AI model
            "eumetsat": 0.25    # Historical/observational data
        }
        self.ensemble_methods = ["weighted_average", "median", "confidence_weighted"]
        print("🧮 Prediction Ensemble initialized", file=sys.stderr)
    
    async def create_ensemble_forecast(self, 
                                     aifs_data: Dict, 
                                     graphcast_data: Dict, 
                                     eumetsat_data: Optional[Dict] = None) -> Dict:
        """
        Create ensemble forecast combining multiple models
        
        Args:
            aifs_data: AIFS model predictions
            graphcast_data: GraphCast model predictions  
            eumetsat_data: Historical/observational data (optional)
            
        Returns:
            Enhanced ensemble forecast
        """
        print("🔮 Creating ensemble forecast...", file=sys.stderr)
        
        try:
            # Standardize data formats
            aifs_predictions = self._standardize_aifs_data(aifs_data)
            graphcast_predictions = self._standardize_graphcast_data(graphcast_data)
            eumetsat_predictions = self._standardize_eumetsat_data(eumetsat_data) if eumetsat_data else []
            
            # Temporal alignment
            aligned_predictions = self._align_temporal_data(
                aifs_predictions, graphcast_predictions, eumetsat_predictions
            )
            
            # Create ensemble predictions
            ensemble_forecast = []
            for timestamp_group in aligned_predictions:
                ensemble_point = self._create_ensemble_point(timestamp_group)
                ensemble_forecast.append(ensemble_point)
            
            # Calculate ensemble statistics
            ensemble_stats = self._calculate_ensemble_statistics(
                aifs_predictions, graphcast_predictions, eumetsat_predictions
            )
            
            return {
                "ensemble_forecast": ensemble_forecast,
                "model_comparison": self._compare_models(aifs_data, graphcast_data),
                "ensemble_statistics": ensemble_stats,
                "metadata": {
                    "ensemble_method": "multi_model_weighted",
                    "models_used": ["AIFS", "GraphCast"] + (["EUMETSAT"] if eumetsat_data else []),
                    "weights": self.model_weights,
                    "generated_at": datetime.now().isoformat(),
                    "forecast_points": len(ensemble_forecast)
                }
            }
            
        except Exception as e:
            print(f"❌ Ensemble creation failed: {e}", file=sys.stderr)
            return await self._fallback_ensemble(aifs_data, graphcast_data)
    
    def _standardize_aifs_data(self, aifs_data: Dict) -> List[WeatherPrediction]:
        """Convert AIFS data to standardized format"""
        predictions = []
        
        forecast_data = aifs_data.get("forecast_data", [])
        
        for point in forecast_data:
            try:
                timestamp = datetime.fromisoformat(point["time"].replace("Z", "+00:00"))
                
                prediction = WeatherPrediction(
                    timestamp=timestamp,
                    temperature=point.get("temperature_2m"),
                    humidity=point.get("relative_humidity_2m"),
                    pressure=point.get("surface_pressure"),
                    wind_speed=point.get("wind_speed_10m"),
                    wind_direction=point.get("wind_direction_10m"),
                    precipitation=point.get("precipitation"),
                    source="AIFS",
                    confidence=0.9,  # High confidence for AIFS
                    forecast_hour=point.get("forecast_hour", 0)
                )
                predictions.append(prediction)
                
            except Exception as e:
                print(f"⚠️ Error processing AIFS point: {e}", file=sys.stderr)
                continue
        
        return predictions
    
    def _standardize_graphcast_data(self, graphcast_data: Dict) -> List[WeatherPrediction]:
        """Convert GraphCast data to standardized format"""
        predictions = []
        
        hourly_data = graphcast_data.get("hourly_data", [])
        
        for i, point in enumerate(hourly_data):
            try:
                timestamp = datetime.fromisoformat(point["time"].replace("Z", "+00:00"))
                
                prediction = WeatherPrediction(
                    timestamp=timestamp,
                    temperature=point.get("temperature"),
                    humidity=point.get("humidity"),
                    pressure=point.get("pressure"),
                    wind_speed=point.get("wind_speed"),
                    wind_direction=point.get("wind_direction"),
                    precipitation=point.get("precipitation"),
                    source="GraphCast",
                    confidence=0.85,  # High confidence for GraphCast
                    forecast_hour=i
                )
                predictions.append(prediction)
                
            except Exception as e:
                print(f"⚠️ Error processing GraphCast point: {e}", file=sys.stderr)
                continue
        
        return predictions
    
    def _standardize_eumetsat_data(self, eumetsat_data: Dict) -> List[WeatherPrediction]:
        """Convert EUMETSAT historical data to standardized format"""
        predictions = []
        
        # EUMETSAT data would typically be historical observations
        # This provides a reality check for recent forecasts
        
        historical_data = eumetsat_data.get("observations", [])
        
        for point in historical_data:
            try:
                timestamp = datetime.fromisoformat(point["time"])
                
                prediction = WeatherPrediction(
                    timestamp=timestamp,
                    temperature=point.get("temperature"),
                    humidity=point.get("humidity"),
                    pressure=point.get("pressure"),
                    wind_speed=point.get("wind_speed"),
                    wind_direction=point.get("wind_direction"),
                    precipitation=point.get("precipitation"),
                    source="EUMETSAT",
                    confidence=1.0,  # Highest confidence for observations
                    forecast_hour=-1  # Historical data
                )
                predictions.append(prediction)
                
            except Exception as e:
                print(f"⚠️ Error processing EUMETSAT point: {e}", file=sys.stderr)
                continue
        
        return predictions
    
    def _align_temporal_data(self, 
                           aifs_pred: List[WeatherPrediction],
                           graphcast_pred: List[WeatherPrediction],
                           eumetsat_pred: List[WeatherPrediction]) -> List[List[WeatherPrediction]]:
        """Align predictions by timestamp"""
        
        # Group predictions by hour (rounding to nearest hour)
        time_groups = {}
        
        for pred in aifs_pred + graphcast_pred + eumetsat_pred:
            # Round to nearest hour for alignment
            hour_key = pred.timestamp.replace(minute=0, second=0, microsecond=0)
            
            if hour_key not in time_groups:
                time_groups[hour_key] = []
            time_groups[hour_key].append(pred)
        
        # Sort by timestamp and return grouped predictions
        sorted_times = sorted(time_groups.keys())
        return [time_groups[time] for time in sorted_times]
    
    def _create_ensemble_point(self, predictions: List[WeatherPrediction]) -> Dict:
        """Create ensemble prediction from multiple model predictions"""
        
        if not predictions:
            return {}
        
        # Use the first timestamp as reference
        timestamp = predictions[0].timestamp
        
        # Calculate weighted averages for each variable
        variables = ["temperature", "humidity", "pressure", "wind_speed", "precipitation"]
        ensemble_values = {}
        
        for var in variables:
            values = []
            weights = []
            
            for pred in predictions:
                value = getattr(pred, var)
                if value is not None:
                    values.append(value)
                    weight = self.model_weights.get(pred.source.lower(), 0.33) * pred.confidence
                    weights.append(weight)
            
            if values:
                # Weighted average
                if weights:
                    weighted_avg = np.average(values, weights=weights)
                else:
                    weighted_avg = np.mean(values)
                
                ensemble_values[var] = round(weighted_avg, 2)
                
                # Calculate uncertainty (standard deviation)
                if len(values) > 1:
                    uncertainty = np.std(values)
                    ensemble_values[f"{var}_uncertainty"] = round(uncertainty, 2)
        
        # Calculate ensemble confidence
        confidence_scores = [pred.confidence for pred in predictions]
        ensemble_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
        
        # Determine source breakdown
        sources = [pred.source for pred in predictions]
        source_counts = {source: sources.count(source) for source in set(sources)}
        
        return {
            "time": timestamp.isoformat(),
            "ensemble_temperature": ensemble_values.get("temperature"),
            "ensemble_humidity": ensemble_values.get("humidity"),
            "ensemble_pressure": ensemble_values.get("pressure"),
            "ensemble_wind_speed": ensemble_values.get("wind_speed"),
            "ensemble_precipitation": ensemble_values.get("precipitation"),
            "confidence": round(ensemble_confidence, 3),
            "uncertainty": {
                "temperature": ensemble_values.get("temperature_uncertainty"),
                "humidity": ensemble_values.get("humidity_uncertainty"),
                "pressure": ensemble_values.get("pressure_uncertainty")
            },
            "contributing_models": source_counts,
            "prediction_count": len(predictions)
        }
    
    def _compare_models(self, aifs_data: Dict, graphcast_data: Dict) -> Dict:
        """Compare AIFS and GraphCast model characteristics"""
        
        comparison = {
            "model_characteristics": {
                "aifs": {
                    "provider": "ECMWF",
                    "type": "AI Forecasting System",
                    "resolution": "~31km (0.25°)",
                    "strength": "Latest ECMWF AI technology",
                    "update_frequency": "4x daily",
                    "forecast_horizon": "10+ days"
                },
                "graphcast": {
                    "provider": "Google DeepMind",
                    "type": "Graph Neural Network",
                    "resolution": "~28km (0.25°)",
                    "strength": "Proven global performance",
                    "update_frequency": "4x daily",
                    "forecast_horizon": "10+ days"
                }
            },
            "performance_comparison": {
                "accuracy": {
                    "aifs": "State-of-the-art ECMWF AI",
                    "graphcast": "90% more accurate than traditional NWP"
                },
                "speed": {
                    "aifs": "Fast GPU inference",
                    "graphcast": "<1 minute for 10-day forecast"
                },
                "coverage": {
                    "aifs": "Global",
                    "graphcast": "Global"
                }
            },
            "recommendations": self._generate_model_recommendations(aifs_data, graphcast_data)
        }
        
        return comparison
    
    def _generate_model_recommendations(self, aifs_data: Dict, graphcast_data: Dict) -> List[str]:
        """Generate recommendations based on model availability and characteristics"""
        recommendations = []
        
        aifs_available = not aifs_data.get("metadata", {}).get("is_mock", True)
        graphcast_available = not graphcast_data.get("metadata", {}).get("is_mock", True)
        
        if aifs_available and graphcast_available:
            recommendations.append("Both models available - ensemble prediction provides highest accuracy")
            recommendations.append("Use AIFS for European focus, GraphCast for global perspective")
        elif aifs_available:
            recommendations.append("AIFS available - use for high-quality ECMWF predictions")
        elif graphcast_available:
            recommendations.append("GraphCast available - use for proven global AI forecasting")
        else:
            recommendations.append("Using mock data - deploy models for production forecasts")
        
        recommendations.append("Combine with EUMETSAT observations for complete analysis")
        
        return recommendations
    
    def _calculate_ensemble_statistics(self, 
                                     aifs_pred: List[WeatherPrediction],
                                     graphcast_pred: List[WeatherPrediction],
                                     eumetsat_pred: List[WeatherPrediction]) -> Dict:
        """Calculate ensemble statistics and quality metrics"""
        
        stats = {
            "model_coverage": {
                "aifs_points": len(aifs_pred),
                "graphcast_points": len(graphcast_pred),
                "eumetsat_points": len(eumetsat_pred)
            },
            "temporal_range": {},
            "ensemble_quality": {}
        }
        
        # Calculate temporal coverage
        all_predictions = aifs_pred + graphcast_pred + eumetsat_pred
        if all_predictions:
            timestamps = [pred.timestamp for pred in all_predictions]
            stats["temporal_range"] = {
                "start": min(timestamps).isoformat(),
                "end": max(timestamps).isoformat(),
                "total_hours": (max(timestamps) - min(timestamps)).total_seconds() / 3600
            }
        
        # Calculate model agreement (when both models have data)
        agreement_scores = []
        for aifs_point in aifs_pred:
            for gc_point in graphcast_pred:
                # Find matching timestamps (within 1 hour)
                time_diff = abs((aifs_point.timestamp - gc_point.timestamp).total_seconds())
                if time_diff <= 3600:  # Within 1 hour
                    if aifs_point.temperature and gc_point.temperature:
                        temp_diff = abs(aifs_point.temperature - gc_point.temperature)
                        agreement = max(0, 1 - temp_diff / 10)  # Agreement score
                        agreement_scores.append(agreement)
        
        if agreement_scores:
            stats["ensemble_quality"]["model_agreement"] = round(np.mean(agreement_scores), 3)
            stats["ensemble_quality"]["agreement_consistency"] = round(np.std(agreement_scores), 3)
        
        return stats
    
    async def _fallback_ensemble(self, aifs_data: Dict, graphcast_data: Dict) -> Dict:
        """Fallback ensemble when main ensemble creation fails"""
        print("🔄 Using fallback ensemble method", file=sys.stderr)
        
        return {
            "ensemble_forecast": [],
            "model_comparison": self._compare_models(aifs_data, graphcast_data),
            "ensemble_statistics": {"status": "fallback_mode"},
            "metadata": {
                "ensemble_method": "fallback",
                "models_used": ["AIFS", "GraphCast"],
                "generated_at": datetime.now().isoformat(),
                "note": "Fallback mode - check individual model outputs"
            }
        }

# Test the ensemble system
async def test_prediction_ensemble():
    """Test the prediction ensemble system"""
    print("🧪 Testing Prediction Ensemble")
    print("=" * 40)
    
    ensemble = PredictionEnsemble()
    
    # Mock AIFS data
    aifs_data = {
        "forecast_data": [
            {
                "time": "2025-01-15T12:00:00Z",
                "temperature_2m": 22.5,
                "relative_humidity_2m": 65,
                "surface_pressure": 1013.2,
                "wind_speed_10m": 8.5,
                "precipitation": 0.0,
                "forecast_hour": 0
            },
            {
                "time": "2025-01-15T18:00:00Z", 
                "temperature_2m": 20.1,
                "relative_humidity_2m": 70,
                "surface_pressure": 1012.8,
                "wind_speed_10m": 9.2,
                "precipitation": 0.2,
                "forecast_hour": 6
            }
        ],
        "metadata": {"is_mock": False}
    }
    
    # Mock GraphCast data
    graphcast_data = {
        "hourly_data": [
            {
                "time": "2025-01-15T12:00:00Z",
                "temperature": 23.1,
                "humidity": 63,
                "pressure": 1013.5,
                "wind_speed": 8.8,
                "precipitation": 0.0
            },
            {
                "time": "2025-01-15T18:00:00Z",
                "temperature": 19.8,
                "humidity": 72,
                "pressure": 1012.5,
                "wind_speed": 9.5,
                "precipitation": 0.1
            }
        ],
        "metadata": {"is_mock": False}
    }
    
    try:
        # Create ensemble forecast
        ensemble_result = await ensemble.create_ensemble_forecast(
            aifs_data, graphcast_data
        )
        
        print("✅ Ensemble forecast created!")
        print(f"📊 Forecast points: {len(ensemble_result['ensemble_forecast'])}")
        print(f"🤖 Models used: {ensemble_result['metadata']['models_used']}")
        
        # Show sample ensemble point
        if ensemble_result['ensemble_forecast']:
            sample_point = ensemble_result['ensemble_forecast'][0]
            print("\n📅 Sample ensemble prediction:")
            print(f"  Time: {sample_point['time']}")
            print(f"  🌡️  Temperature: {sample_point.get('ensemble_temperature')}°C")
            print(f"  💧 Humidity: {sample_point.get('ensemble_humidity')}%")
            print(f"  🔍 Confidence: {sample_point.get('confidence')}")
            print(f"  🎯 Contributing models: {sample_point.get('contributing_models')}")
        
        print("\n🔍 Model comparison:")
        comparison = ensemble_result['model_comparison']
        for rec in comparison['recommendations']:
            print(f"  • {rec}")
            
    except Exception as e:
        print(f"❌ Ensemble test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_prediction_ensemble())