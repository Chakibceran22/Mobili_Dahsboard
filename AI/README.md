# Battery Data Analysis Pipeline

This directory contains a complete pipeline for fetching, analyzing, and visualizing battery data from ThingsBoard.

## 📁 Directory Structure

```
AI/
├── fetch_battery_data.py    # Fetches battery data from ThingsBoard API
├── plot_battery_data.py     # Creates various visualizations from data
├── battery_pipeline.py      # Main coordinator script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── data/                   # JSON data files (auto-created)
│   └── battery_data_*.json
└── plots/                  # Generated PNG plots (auto-created)
    ├── battery_basic_*.png
    └── battery_detailed_*.png
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r AI/requirements.txt
```

### 2. Run the Pipeline
```bash
# Interactive mode with menu
python AI/battery_pipeline.py

# Or run specific commands
python AI/battery_pipeline.py fetch      # Fetch data only
python AI/battery_pipeline.py plot       # Plot latest data
python AI/battery_pipeline.py pipeline   # Fetch + plot
```

### 3. Run Individual Scripts
```bash
# Fetch battery data from ThingsBoard
python AI/fetch_battery_data.py

# Create plots from existing data
python AI/plot_battery_data.py
```

## 📊 What You Get

### Data Files (`data/` directory)
- **battery_data_[device_id]_[timestamp].json**: Raw time series data with metadata

### Visualizations (`plots/` directory)
- **Basic Plot**: Simple line chart of battery level over time
- **Detailed Plot**: 4-panel dashboard with:
  - Time series plot
  - Battery level distribution histogram
  - Battery drain rate analysis
  - Battery level categories (Critical/Low/Medium/High)

## 🔧 Configuration

The scripts use these default settings:
- **ThingsBoard URL**: `http://localhost:8081`
- **Credentials**: `tenant@thingsboard.org` / `tenant`
- **Time Range**: Last 24 hours
- **Data Limit**: 1000 points

To modify these, edit the parameters in `fetch_battery_data.py`.

## 📈 Features

### Data Fetching
- ✅ Authenticates with ThingsBoard API
- ✅ Fetches device information
- ✅ Downloads time series data (same as widgets see)
- ✅ Saves data as JSON for analysis
- ✅ Error handling and status reporting

### Data Visualization
- ✅ Multiple plot types (line, histogram, bar charts)
- ✅ Statistical analysis (avg, min, max, std dev)
- ✅ Battery drain rate calculation
- ✅ Battery level categorization
- ✅ High-quality PNG outputs (300 DPI)
- ✅ Professional styling and formatting

### Pipeline Management
- ✅ Interactive menu system
- ✅ Command-line interface
- ✅ File listing and management
- ✅ Full pipeline automation

## 📋 Requirements

- Python 3.7+
- ThingsBoard running locally (or modify URL)
- Device with battery data in ThingsBoard
- `exp/battery.txt` file with device credentials

## 🔍 Troubleshooting

### "battery.txt not found"
- Ensure `exp/battery.txt` exists with device token and ID
- Format: 
  ```
  token=your_device_token_here
  id=your_device_id_here
  ```

### "Failed to login"
- Check ThingsBoard is running on `http://localhost:8081`
- Verify credentials in `fetch_battery_data.py`
- Check network connectivity

### "No data found"
- Verify device is sending battery data
- Check time range (default: last 24 hours)
- Ensure device has `batteryLevel` telemetry

### Import errors
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct directory

## 🎯 Next Steps

1. **Run the pipeline**: `python AI/battery_pipeline.py`
2. **Check your data**: Look in `AI/data/` for JSON files
3. **View your plots**: Open PNG files in `AI/plots/`
4. **Customize**: Modify scripts for different time ranges or visualizations
5. **Automate**: Set up cron jobs for regular data collection

Enjoy analyzing your battery data! 🔋📊
