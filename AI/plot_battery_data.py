"""
Device Data Plotter
===================

This script loads telemetry data from JSON files and creates visualizations.
You can choose between line graphs and bar charts.
It generates PNG plots and saves them to the plots directory.
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import glob

def load_telemetry_data(json_filepath):
    """Load telemetry data from JSON file"""
    try:
        with open(json_filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {json_filepath}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {json_filepath}")
        return None

def extract_time_series(telemetry_data):
    """Extract timestamps and values from telemetry data"""
    timestamps = []
    values = []
    
    # Handle both old format (battery_data) and new format (telemetry_data)
    data_key = 'telemetry_data' if 'telemetry_data' in telemetry_data else 'battery_data'
    
    for point in telemetry_data[data_key]:
        timestamp = point['ts'] / 1000  # Convert from milliseconds
        value = float(point['value'])
        timestamps.append(datetime.fromtimestamp(timestamp))
        values.append(value)
    
    return timestamps, values

def create_telemetry_plot(timestamps, values, device_id, key_name, save_dir, chart_type="bar"):
    """Create a visualization of telemetry values over time
    
    Args:
        chart_type: Type of chart to create ("line" or "bar")
    """
    plt.figure(figsize=(12, 6))
    
    # Determine units and color based on key name
    unit = ""
    color = '#2E8B57'  # Default green
    if "battery" in key_name.lower():
        unit = "%"
        color = '#2E8B57'  # Green for battery
    elif "temp" in key_name.lower():
        unit = "°C"
        color = '#FF6B6B'  # Red for temperature
    elif "humid" in key_name.lower():
        unit = "%"
        color = '#4ECDC4'  # Cyan for humidity
    elif "pressure" in key_name.lower():
        unit = " hPa"
        color = '#45B7D1'  # Blue for pressure
    
    if chart_type == "bar":
        # Create bar chart
        plt.bar(range(len(values)), values, color=color, alpha=0.7)
        plt.title(f'{key_name.title()} Distribution - Device {device_id}', fontsize=16, fontweight='bold')
        plt.xlabel('Data Point Index', fontsize=12)
        plt.ylabel(f'{key_name.title()} ({unit})' if unit else key_name.title(), fontsize=12)
        
        # Add time labels for every few bars to avoid crowding
        step = max(1, len(timestamps) // 10)  # Show max 10 labels
        tick_positions = range(0, len(timestamps), step)
        tick_labels = [timestamps[i].strftime('%H:%M') for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45)
        
    else:  # default to line chart
        # Create line chart
        plt.plot(timestamps, values, linewidth=2, color=color, marker='o', markersize=4)
        plt.title(f'{key_name.title()} Over Time - Device {device_id}', fontsize=16, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel(f'{key_name.title()} ({unit})' if unit else key_name.title(), fontsize=12)
        
        # Format x-axis for line chart
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.xticks(rotation=45)
    
    plt.grid(True, alpha=0.3)
    
    # Set y-axis limits based on data type
    if "battery" in key_name.lower() or "humid" in key_name.lower():
        plt.ylim(0, 100)
    elif values:
        # For other data types, use dynamic range with some padding
        min_val, max_val = min(values), max(values)
        padding = (max_val - min_val) * 0.1
        plt.ylim(min_val - padding, max_val + padding)
    
    # Add statistics text
    if values:
        avg_value = np.mean(values)
        min_value = np.min(values)
        max_value = np.max(values)
        
        stats_text = f'Avg: {avg_value:.1f}{unit} | Min: {min_value:.1f}{unit} | Max: {max_value:.1f}{unit}'
        plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    
    # Save plot
    filename = f'{key_name}_{chart_type}_{device_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    # Ensure save directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    filepath = os.path.join(save_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"📊 {chart_type.title()} chart saved: {filepath}")
    plt.close()
    
    return filepath


def create_summary_stats(timestamps, values, device_id, key_name):
    """Create and print summary statistics"""
    if not values:
        print("❌ No data to analyze")
        return
    
    # Determine units based on key name
    unit = ""
    if "battery" in key_name.lower():
        unit = "%"
    elif "temp" in key_name.lower():
        unit = "°C"
    elif "humid" in key_name.lower():
        unit = "%"
    elif "pressure" in key_name.lower():
        unit = " hPa"
    
    print(f"\n📈 {key_name.title()} Statistics for Device {device_id}")
    print("=" * 50)
    print(f"📊 Total data points: {len(values)}")
    print(f"🕐 Time span: {timestamps[0].strftime('%Y-%m-%d %H:%M:%S')} to {timestamps[-1].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚡ Average {key_name}: {np.mean(values):.1f}{unit}")
    print(f"📉 Minimum {key_name}: {np.min(values):.1f}{unit}")
    print(f"📈 Maximum {key_name}: {np.max(values):.1f}{unit}")
    print(f"📊 Standard deviation: {np.std(values):.1f}{unit}")
    
    # Create data distribution categories based on data type
    if "battery" in key_name.lower():
        critical = sum(1 for v in values if v < 20)
        low = sum(1 for v in values if 20 <= v < 40)
        medium = sum(1 for v in values if 40 <= v < 70)
        high = sum(1 for v in values if v >= 70)
        
        print(f"\n🔋 {key_name.title()} Level Distribution:")
        print(f"   Critical (<20{unit}): {critical} readings ({critical/len(values)*100:.1f}%)")
        print(f"   Low (20-40{unit}): {low} readings ({low/len(values)*100:.1f}%)")
        print(f"   Medium (40-70{unit}): {medium} readings ({medium/len(values)*100:.1f}%)")
        print(f"   High (≥70{unit}): {high} readings ({high/len(values)*100:.1f}%)")
    else:
        # For other data types, show quartiles
        q1 = np.percentile(values, 25)
        q2 = np.percentile(values, 50)  # median
        q3 = np.percentile(values, 75)
        
        print(f"\n📊 {key_name.title()} Distribution:")
        print(f"   25th percentile: {q1:.1f}{unit}")
        print(f"   Median (50th percentile): {q2:.1f}{unit}")
        print(f"   75th percentile: {q3:.1f}{unit}")

def plot_latest_data(chart_type="bar"):
    """Find and plot the latest telemetry data file, then remove it
    
    Args:
        chart_type: Type of chart to create ("line" or "bar")
    """
    data_dir = "AI/data"
    plots_dir = "AI/plots"
    
    # Find all JSON files in data directory (both old and new formats)
    json_files = glob.glob(os.path.join(data_dir, "*_data_*.json"))
    
    if not json_files:
        print("❌ No telemetry data files found in AI/data directory")
        print("💡 Run fetch_battery_data.py first to collect data")
        return
    
    # Sort by modification time and get the latest
    latest_file = max(json_files, key=os.path.getmtime)
    print(f"📂 Using latest data file: {os.path.basename(latest_file)}")
    
    # Load and plot data (this will also remove the file)
    plot_data_file(latest_file, plots_dir, chart_type)

def plot_data_file(json_filepath, plots_dir, chart_type="line"):
    """Plot data from a specific JSON file and remove the data file after plotting
    
    Args:
        json_filepath: Path to the JSON data file
        plots_dir: Directory to save plots
        chart_type: Type of chart to create ("line" or "bar")
    """
    # Load data
    telemetry_data = load_telemetry_data(json_filepath)
    if not telemetry_data:
        return
    
    device_id = telemetry_data.get('device_id', 'unknown')
    data_points = telemetry_data.get('data_points', 0)
    key_name = telemetry_data.get('key_name', 'telemetry')
    
    print(f"📊 Creating {chart_type} chart for {key_name} from device {device_id} ({data_points} points)")
    
    # Extract time series data
    timestamps, values = extract_time_series(telemetry_data)
    
    if not timestamps or not values:
        print("❌ No valid data points found")
        return
    
    # Create the plot
    create_telemetry_plot(timestamps, values, device_id, key_name, plots_dir, chart_type)
    
    # Print summary statistics
    create_summary_stats(timestamps, values, device_id, key_name)
    
    # Remove the data file after successful plotting
    try:
        os.remove(json_filepath)
        print(f"🗑️  Removed data file: {os.path.basename(json_filepath)}")
    except OSError as e:
        print(f"⚠️  Could not remove data file: {e}")

def plot_all_data(chart_type="line"):
    """Plot all available telemetry data files and remove them after plotting
    
    Args:
        chart_type: Type of chart to create ("line" or "bar")
    """
    data_dir = "data"
    plots_dir = "plots"
    
    # Find all JSON files in data directory (both old and new formats)
    json_files = glob.glob(os.path.join(data_dir, "*_data_*.json"))
    
    if not json_files:
        print("❌ No telemetry data files found in AI/data directory")
        print("💡 Run fetch_battery_data.py first to collect data")
        return
    
    print(f"📊 Found {len(json_files)} data files to plot as {chart_type} charts")
    
    for json_file in sorted(json_files):
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(json_file)}")
        plot_data_file(json_file, plots_dir, chart_type)
    
    # Check if data directory is empty and remove it if so
    try:
        remaining_files = os.listdir(data_dir)
        if not remaining_files:
            os.rmdir(data_dir)
            print(f"\n🗑️  Removed empty data directory: {data_dir}")
        else:
            print(f"\n📁 Data directory still contains {len(remaining_files)} files")
    except OSError:
        pass  # Directory might not be empty or have permissions issues

def main(chart_type="line"):
    """Main function - create plots from telemetry data
    
    Args:
        chart_type: Type of chart to create ("line" or "bar")
    """
    print("📊 Device Data Plotter")
    print("=" * 50)
    print(f"Creating {chart_type} chart from collected telemetry data")
    print()
    
    # Create plots directory if it doesn't exist
    os.makedirs("plots", exist_ok=True)
    
    # Check if we have any data files
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("❌ Data directory not found. Run fetch_battery_data.py first!")
        return
    
    # Plot the latest data by default
    plot_latest_data(chart_type)
    
    print(f"\n🎯 Check the plots directory for your {chart_type} chart!")


if __name__ == "__main__":
    import sys
    chart_type = "line"  # Default chart type
    
    # Check for chart type argument
    if len(sys.argv) > 1:
        if sys.argv[1] in ["line", "bar"]:
            chart_type = sys.argv[1]
        else:
            print("❌ Invalid chart type. Use 'line' or 'bar'")
            print("Usage: python plot_battery_data.py [line|bar]")
            sys.exit(1)
    
    main(chart_type)
