# Weather Station Telemetry System for ThingsBoard

This system creates a virtual weather station device that fetches meteorological data from the Open-Meteo API and treats it as telemetry data in ThingsBoard. It demonstrates how external API data can be integrated into an IoT platform as if it were coming from physical sensors.

## 🌤️ Overview

The weather station system consists of three main components:

1. **Device Creator** (`create_weather_station.py`) - Creates the weather station device in ThingsBoard
2. **Telemetry Sender** (`weather_station_telemetry.py`) - Sends weather data as one-time telemetry
3. **Continuous Monitor** (`weather_station_monitor.py`) - Continuously monitors and reports weather conditions

## 📊 Telemetry Data

The system reports the following meteorological parameters:

- **Temperature** (`temperature_2m`) - Air temperature at 2 meters height (°C)
- **Rainfall** (`rain`) - Precipitation amount (mm)
- **Cloud Cover** (`cloud_cover`) - Cloud coverage percentage (%)
- **Solar Radiation** (`direct_radiation`) - Direct solar radiation (W/m²)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r exp/weather_station_requirements.txt
```

### 2. Create Weather Station Device

```bash
python exp/create_weather_station.py
```

This will:
- Authenticate with ThingsBoard
- Create a "Weather Station - Open-Meteo" device
- Generate access credentials
- Save configuration to `exp/weather_station.txt`

### 3. Send Weather Data

#### Option A: One-time Data Send
```bash
python exp/weather_station_telemetry.py
```

Choose between:
- Current weather conditions only
- Full 7-day forecast data

#### Option B: Continuous Monitoring
```bash
python exp/weather_station_monitor.py
```

Choose monitoring interval:
- Every 5 minutes (frequent updates)
- Every 15 minutes (standard)
- Every 30 minutes (conservative)
- Every hour (minimal)
- Custom interval

## 📋 Prerequisites

1. **ThingsBoard Instance**
   - Running on `localhost:8081` (default)
   - Login credentials: `tenant@mobilis.dz` / `tenant`

2. **Python Dependencies**
   - Python 3.7+
   - See `weather_station_requirements.txt` for full list

3. **Internet Connection**
   - Required for Open-Meteo API access

## 🔧 Configuration

### Location Settings

The default location is set to **Algiers, Algeria**:
- Latitude: 36.7576523413059
- Longitude: 3.0605869645037327
- Timezone: Europe/London

To change the location, modify the `params` dictionary in the telemetry scripts:

```python
self.params = {
    "latitude": YOUR_LATITUDE,
    "longitude": YOUR_LONGITUDE,
    "hourly": ["temperature_2m", "rain", "cloud_cover", "direct_radiation"],
    "timezone": "YOUR_TIMEZONE",
    "forecast_days": 7,
}
```

### ThingsBoard Settings

To use a different ThingsBoard instance, modify the `base_url` parameter:

```python
# Default
base_url = "http://localhost:8081"

# Custom instance
base_url = "https://your-thingsboard-instance.com"
```

## 📊 Data Flow

```
Open-Meteo API → Python Script → ThingsBoard Device → Dashboard
```

1. **API Fetch**: Script fetches weather data from Open-Meteo API
2. **Data Transform**: Raw API data is converted to ThingsBoard telemetry format
3. **Telemetry Send**: Data is sent via HTTP POST to ThingsBoard telemetry endpoint
4. **Dashboard Display**: Data appears in ThingsBoard dashboard as device telemetry

## 🔍 Monitoring Features

### Real-time Display
- Current weather conditions
- Transmission status
- Success/failure rates
- Timestamps

### Error Handling
- API request retries
- Connection timeout handling
- Graceful shutdown (Ctrl+C)
- Session statistics

### Caching
- 30-minute API response cache (monitoring mode)
- 1-hour cache (batch mode)
- Reduces API calls and improves reliability

## 📈 Use Cases

1. **Weather Monitoring Dashboard**
   - Real-time weather conditions
   - Historical weather trends
   - Weather-based alerts and rules

2. **IoT System Integration**
   - Combine with physical sensors
   - Weather-dependent automation
   - Environmental monitoring

3. **Data Analytics**
   - Weather pattern analysis
   - Correlation with other metrics
   - Predictive modeling

4. **API Integration Demo**
   - Show how external APIs can be treated as IoT devices
   - Demonstrate telemetry data ingestion
   - Prototype weather-dependent applications

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check ThingsBoard credentials
   - Verify ThingsBoard is running
   - Check network connectivity

2. **Device Creation Failed**
   - Verify user permissions
   - Check if device already exists
   - Review ThingsBoard logs

3. **Telemetry Send Failed**
   - Verify device token
   - Check ThingsBoard API endpoint
   - Review network connectivity

4. **API Fetch Failed**
   - Check internet connection
   - Verify Open-Meteo API status
   - Review API parameters

### Debug Mode

Add debug logging to scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Notes

- Device access tokens are stored in plain text files
- Use environment variables for production deployments
- Implement proper authentication for production systems
- Consider API rate limiting for high-frequency monitoring

## 📝 File Structure

```
exp/
├── create_weather_station.py      # Device creator
├── weather_station_telemetry.py   # One-time telemetry sender
├── weather_station_monitor.py     # Continuous monitor
├── weather_station_requirements.txt # Python dependencies
├── weather_station.txt            # Device configuration (generated)
└── README_weather_station.md      # This documentation
```

## 🌐 API Reference

- **Open-Meteo API**: https://open-meteo.com/
- **ThingsBoard REST API**: https://thingsboard.io/docs/reference/rest-api/
- **Device Telemetry API**: `/api/v1/{deviceToken}/telemetry`

## 🎯 Next Steps

1. **Dashboard Creation**: Create custom dashboards in ThingsBoard UI
2. **Rule Chains**: Set up weather-based automation rules
3. **Alerts**: Configure weather condition alerts
4. **Integration**: Combine with other IoT devices
5. **Scaling**: Deploy multiple weather stations for different locations
