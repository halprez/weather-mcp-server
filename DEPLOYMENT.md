# AIFS Integration Deployment Guide

This guide covers deploying the enhanced Weather MCP Server with AIFS (AI Forecasting System) support.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (optional, for real AIFS inference)
- Python 3.10+
- EUMETSAT API credentials (optional)

### 1. Deploy AIFS + Weather MCP Stack

```bash
# Clone and navigate to project
git clone <your-repo-url>
cd weather-mcp-server

# Start the complete stack
docker-compose up --build

# Or start specific services
docker-compose up aifs-server weather-mcp
```

### 2. Verify Deployment

```bash
# Check AIFS server health
curl http://localhost:8080/health

# Check available models
curl http://localhost:8080/models

# Test AIFS forecast
curl -X POST http://localhost:8080/forecast \
  -H "Content-Type: application/json" \
  -d '{"latitude": 28.29, "longitude": -16.63, "forecast_hours": 72}'
```

### 3. Test Integration

```bash
# Run comprehensive integration tests
python test_integration.py

# Test individual components
python -m weather_mcp.aifs_client
python -m weather_mcp.prediction_ensemble
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Desktop / MCP Client                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────────────┐
│                Weather MCP Server (Port 3000)                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ AIFS Forecast   │ │ GraphCast       │ │ EUMETSAT        │   │
│  │ Tool            │ │ Forecast Tool   │ │ Historical Tool │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Model Compare   │ │ Ensemble        │ │ Timeline        │   │
│  │ Tool            │ │ Forecast Tool   │ │ Tool            │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                 Data Integration Layer                          │
│  • Prediction Ensemble • Model Comparison • Data Harmonization │
└─────────────────────┬───────────────────────────────────────────┘
                      │
      ┌───────────────▼────────┬─────────────────┐
      │                        │                 │
┌─────▼─────┐            ┌─────▼─────┐     ┌─────▼─────┐
│AIFS Server│            │GraphCast  │     │ EUMETSAT  │
│(Port 8080)│            │(Open-Meteo│     │ Satellite │
│           │            │    API)   │     │   Data    │
│• ECMWF AI │            │• Google AI│     │• Historical│
│• 31km res │            │• 28km res │     │• Real-time│
│• 720h max │            │• 16d max  │     │• Validated│
└───────────┘            └───────────┘     └───────────┘
```

## 🐳 Docker Services

### AIFS Server (`aifs-server`)
- **Purpose**: Serves ECMWF AIFS model predictions
- **Port**: 8080
- **GPU**: Required for real inference
- **API**: REST API for forecast requests

### Weather MCP Server (`weather-mcp`)
- **Purpose**: Main MCP server with all weather tools
- **Port**: 3000
- **Dependencies**: aifs-server, external APIs
- **Protocol**: MCP over stdin/stdout

### Redis Cache (`redis`) [Optional]
- **Purpose**: Caching for improved performance
- **Port**: 6379

### Monitoring Stack [Optional]
- **Grafana**: Port 3001 (admin/admin)
- **Prometheus**: Port 9090

## ⚙️ Configuration

### Environment Variables

```bash
# EUMETSAT API (optional)
EUMETSAT_CONSUMER_KEY=your_key_here
EUMETSAT_CONSUMER_SECRET=your_secret_here

# AIFS Configuration
AIFS_SERVER_URL=http://aifs-server:8080
AIFS_ENABLED=true

# Feature Toggles
GRAPHCAST_ENABLED=true
ENSEMBLE_ENABLED=true
LOG_LEVEL=INFO
```

### Configuration File

Edit `config/weather_config.yaml`:

```yaml
data_sources:
  aifs:
    enabled: true
    deployment_mode: "docker"
    docker_url: "http://localhost:8080"
    max_forecast_hours: 720
  
  graphcast:
    enabled: true
    max_forecast_days: 16
  
  eumetsat:
    enabled: true
    max_historical_days: 30

ensemble:
  enabled: true
  model_weights:
    aifs: 0.4
    graphcast: 0.35
    eumetsat: 0.25
```

## 🔧 Development Setup

### Local Development

```bash
# Install dependencies
uv pip install -r requirements.txt

# Install AIFS dependencies (optional)
pip install anemoi-inference

# Run MCP server locally
python -m weather_mcp.mcp_server_v2

# Run with test mode
python -m weather_mcp.mcp_server_v2 test
```

### AIFS Local Mode

For local AIFS inference (requires significant resources):

```bash
# Install anemoi packages
pip install anemoi-inference anemoi-models

# Configure AIFS client for local mode
export AIFS_DEPLOYMENT_MODE=local

# Download AIFS model (large download)
# This would be done automatically by anemoi-inference
```

## 📊 Available MCP Tools

### Core Weather Tools
1. **`get_graphcast_forecast`** - Google GraphCast AI predictions
2. **`get_historical_weather`** - EUMETSAT satellite observations  
3. **`get_complete_weather_timeline`** - Combined historical + forecast

### New AIFS Tools
4. **`get_aifs_forecast`** - ECMWF AIFS AI predictions
5. **`compare_ai_models`** - AIFS vs GraphCast comparison
6. **`get_ensemble_forecast`** - Multi-model ensemble predictions

### Usage Examples

```python
# Claude Desktop usage:
"Get an AIFS forecast for the Canary Islands"
"Compare AIFS and GraphCast models for latitude 28.29, longitude -16.63"
"Create an ensemble forecast combining all models for Las Palmas"
```

## 🔍 Monitoring and Debugging

### Health Checks

```bash
# AIFS server health
curl http://localhost:8080/health

# Weather MCP server (if running HTTP mode)
curl http://localhost:3000/health
```

### Logs

```bash
# View AIFS server logs
docker-compose logs -f aifs-server

# View MCP server logs
docker-compose logs -f weather-mcp

# View all logs
docker-compose logs -f
```

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG docker-compose up

# Test individual components
python -m weather_mcp.aifs_client
python -m weather_mcp.prediction_ensemble
python test_integration.py
```

## 🚨 Troubleshooting

### Common Issues

**AIFS Server Not Starting**
- Check GPU availability: `nvidia-smi`
- Verify Docker GPU support: `docker run --gpus all nvidia/cuda:11.8-base nvidia-smi`
- Check port 8080 availability: `netstat -tlnp | grep 8080`

**MCP Connection Issues**
- Verify Claude Desktop configuration
- Check file paths in `claude_desktop_config.json`
- Ensure virtual environment is activated

**Performance Issues**
- Enable Redis caching
- Adjust `max_concurrent_requests` in config
- Monitor memory usage: `docker stats`

**Mock Data Being Used**
- Ensure AIFS server is running and accessible
- Check `AIFS_SERVER_URL` environment variable
- Verify network connectivity between containers

### Performance Optimization

```yaml
# In weather_config.yaml
cache:
  enabled: true
  ttl_hours:
    aifs: 6
    graphcast: 6
    eumetsat: 24

performance:
  max_concurrent_requests: 5
  request_timeout: 300
```

## 🚀 Production Deployment

### Scaling

```bash
# Scale MCP servers
docker-compose up --scale weather-mcp=3

# Use load balancer (nginx/traefik)
# Configure health checks
# Set up monitoring (Prometheus/Grafana)
```

### Security

```bash
# Use environment file for secrets
echo "EUMETSAT_CONSUMER_KEY=xxx" > .env
echo "EUMETSAT_CONSUMER_SECRET=xxx" >> .env

# Restrict network access
# Use proper HTTPS certificates
# Enable authentication if needed
```

### Monitoring

```bash
# Start with monitoring stack
docker-compose --profile monitoring up

# Access Grafana: http://localhost:3001
# Access Prometheus: http://localhost:9090
```

## 📈 Performance Metrics

### Expected Performance
- **AIFS Forecast**: ~30-60 seconds for 240-hour forecast
- **GraphCast Forecast**: ~5-10 seconds for 7-day forecast
- **Ensemble Creation**: ~1-3 seconds additional processing
- **MCP Response Time**: <2 seconds for typical requests

### Resource Requirements
- **AIFS Server**: 8GB+ RAM, NVIDIA GPU (optional)
- **Weather MCP**: 2GB+ RAM, 2+ CPU cores
- **Total Storage**: ~10GB for models and cache

## 🎯 Next Steps

1. **Deploy to production** with proper monitoring
2. **Integrate with Claude Desktop** for AI agent access
3. **Add custom weather models** via the extension framework
4. **Implement real-time alerting** for severe weather events
5. **Scale horizontally** with multiple AIFS containers

---

For questions or issues, check the GitHub repository or create an issue.