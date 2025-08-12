"""
Configuration management for Weather MCP Server
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AIFSConfig:
    enabled: bool = True
    deployment_mode: str = "docker"
    docker_url: str = "http://localhost:8080"
    local_config_path: str = "/app/aifs_config.yaml"
    timeout: int = 300
    max_forecast_hours: int = 720

@dataclass
class GraphCastConfig:
    enabled: bool = True
    provider: str = "Open-Meteo"
    base_url: str = "https://api.open-meteo.com/v1/forecast"
    timeout: int = 30
    cache_hours: int = 6
    max_forecast_days: int = 16

@dataclass
class EUMETSATConfig:
    enabled: bool = True
    base_url: str = "https://api.eumetsat.int"
    timeout: int = 60
    retry_attempts: int = 3
    max_historical_days: int = 30

@dataclass
class EnsembleConfig:
    enabled: bool = True
    model_weights: Dict[str, float] = None
    methods: list = None
    default_method: str = "weighted_average"
    quality_threshold: float = 0.7
    
    def __post_init__(self):
        if self.model_weights is None:
            self.model_weights = {"aifs": 0.4, "graphcast": 0.35, "eumetsat": 0.25}
        if self.methods is None:
            self.methods = ["weighted_average", "median", "confidence_weighted"]

class WeatherConfig:
    """Configuration manager for Weather MCP Server"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config_data = self._load_config()
        
        # Initialize component configs
        self.aifs = self._load_aifs_config()
        self.graphcast = self._load_graphcast_config()
        self.eumetsat = self._load_eumetsat_config()
        self.ensemble = self._load_ensemble_config()
        
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations"""
        possible_paths = [
            os.environ.get("WEATHER_CONFIG"),
            "./config/weather_config.yaml",
            "../config/weather_config.yaml",
            "./weather_config.yaml",
            "/app/config/weather_config.yaml"
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return path
        
        # Return default path if none found
        return "./config/weather_config.yaml"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Config file not found at {self.config_path}, using defaults")
                return self._default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "server": {
                "name": "Enhanced Weather MCP",
                "version": "3.0.0",
                "log_level": "INFO"
            },
            "data_sources": {
                "aifs": {
                    "enabled": True,
                    "deployment_mode": "docker",
                    "docker_url": "http://localhost:8080"
                },
                "graphcast": {
                    "enabled": True,
                    "provider": "Open-Meteo"
                },
                "eumetsat": {
                    "enabled": True
                }
            },
            "ensemble": {
                "enabled": True,
                "model_weights": {
                    "aifs": 0.4,
                    "graphcast": 0.35,
                    "eumetsat": 0.25
                }
            }
        }
    
    def _load_aifs_config(self) -> AIFSConfig:
        """Load AIFS configuration"""
        aifs_config = self.config_data.get("data_sources", {}).get("aifs", {})
        
        return AIFSConfig(
            enabled=aifs_config.get("enabled", True),
            deployment_mode=aifs_config.get("deployment_mode", "docker"),
            docker_url=aifs_config.get("docker_url", "http://localhost:8080"),
            local_config_path=aifs_config.get("local_config_path", "/app/aifs_config.yaml"),
            timeout=aifs_config.get("timeout", 300),
            max_forecast_hours=aifs_config.get("max_forecast_hours", 720)
        )
    
    def _load_graphcast_config(self) -> GraphCastConfig:
        """Load GraphCast configuration"""
        gc_config = self.config_data.get("data_sources", {}).get("graphcast", {})
        
        return GraphCastConfig(
            enabled=gc_config.get("enabled", True),
            provider=gc_config.get("provider", "Open-Meteo"),
            base_url=gc_config.get("base_url", "https://api.open-meteo.com/v1/forecast"),
            timeout=gc_config.get("timeout", 30),
            cache_hours=gc_config.get("cache_hours", 6),
            max_forecast_days=gc_config.get("max_forecast_days", 16)
        )
    
    def _load_eumetsat_config(self) -> EUMETSATConfig:
        """Load EUMETSAT configuration"""
        eumetsat_config = self.config_data.get("data_sources", {}).get("eumetsat", {})
        
        return EUMETSATConfig(
            enabled=eumetsat_config.get("enabled", True),
            base_url=eumetsat_config.get("base_url", "https://api.eumetsat.int"),
            timeout=eumetsat_config.get("timeout", 60),
            retry_attempts=eumetsat_config.get("retry_attempts", 3),
            max_historical_days=eumetsat_config.get("max_historical_days", 30)
        )
    
    def _load_ensemble_config(self) -> EnsembleConfig:
        """Load ensemble configuration"""
        ensemble_config = self.config_data.get("ensemble", {})
        
        return EnsembleConfig(
            enabled=ensemble_config.get("enabled", True),
            model_weights=ensemble_config.get("model_weights", {
                "aifs": 0.4, "graphcast": 0.35, "eumetsat": 0.25
            }),
            methods=ensemble_config.get("methods", [
                "weighted_average", "median", "confidence_weighted"
            ]),
            default_method=ensemble_config.get("default_method", "weighted_average"),
            quality_threshold=ensemble_config.get("quality_threshold", 0.7)
        )
    
    def get_server_info(self) -> Dict[str, str]:
        """Get server information"""
        server_info = self.config_data.get("server", {})
        return {
            "name": server_info.get("name", "Enhanced Weather MCP"),
            "version": server_info.get("version", "3.0.0")
        }
    
    def get_mcp_tools(self) -> list:
        """Get enabled MCP tools"""
        mcp_config = self.config_data.get("mcp", {})
        tools_config = mcp_config.get("tools", [])
        
        # Default tools if not configured
        if not tools_config:
            return [
                {"name": "get_graphcast_forecast", "enabled": True},
                {"name": "get_historical_weather", "enabled": True},
                {"name": "get_complete_weather_timeline", "enabled": True},
                {"name": "get_aifs_forecast", "enabled": True},
                {"name": "compare_ai_models", "enabled": True},
                {"name": "get_ensemble_forecast", "enabled": True}
            ]
        
        return [tool for tool in tools_config if tool.get("enabled", True)]
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        def update_nested_dict(original: dict, updates: dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                    update_nested_dict(original[key], value)
                else:
                    original[key] = value
        
        update_nested_dict(self.config_data, updates)
        
        # Reload component configs
        self.aifs = self._load_aifs_config()
        self.graphcast = self._load_graphcast_config()
        self.eumetsat = self._load_eumetsat_config()
        self.ensemble = self._load_ensemble_config()
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        save_path = path or self.config_path
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            print(f"✅ Configuration saved to {save_path}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

# Global configuration instance
config = WeatherConfig()

# Test configuration loading
def test_config():
    """Test configuration loading and functionality"""
    print("🧪 Testing Weather Configuration")
    print("=" * 40)
    
    # Test config loading
    test_config = WeatherConfig()
    
    print(f"📋 Server: {test_config.get_server_info()}")
    print(f"🚀 AIFS enabled: {test_config.aifs.enabled}")
    print(f"🧠 GraphCast enabled: {test_config.graphcast.enabled}")
    print(f"🛰️  EUMETSAT enabled: {test_config.eumetsat.enabled}")
    print(f"🔬 Ensemble enabled: {test_config.ensemble.enabled}")
    print(f"⚖️  Model weights: {test_config.ensemble.model_weights}")
    
    # Test enabled tools
    enabled_tools = test_config.get_mcp_tools()
    print(f"🛠️  Enabled tools: {[tool['name'] for tool in enabled_tools]}")
    
    print("✅ Configuration test completed!")

if __name__ == "__main__":
    test_config()