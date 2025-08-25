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
import seaborn as sns
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set up beautiful plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Custom color schemes for different data types
COLOR_SCHEMES = {
    'battery': {
        'primary': '#2ECC71',      # Emerald green
        'secondary': '#27AE60',    # Darker green
        'gradient': ['#E8F8F5', '#2ECC71', '#1E8449'],
        'critical': '#E74C3C'      # Red for low battery
    },
    'temperature': {
        'primary': '#E74C3C',      # Red
        'secondary': '#C0392B',    # Darker red
        'gradient': ['#FDF2E9', '#E74C3C', '#922B21'],
        'cold': '#3498DB',         # Blue for cold
        'hot': '#E74C3C'          # Red for hot
    },
    'humidity': {
        'primary': '#3498DB',      # Blue
        'secondary': '#2980B9',    # Darker blue
        'gradient': ['#EBF5FB', '#3498DB', '#1B4F72'],
        'dry': '#F39C12',         # Orange for dry
        'wet': '#3498DB'          # Blue for wet
    },
    'default': {
        'primary': '#9B59B6',      # Purple
        'secondary': '#8E44AD',    # Darker purple
        'gradient': ['#F4ECF7', '#9B59B6', '#5B2C6F']
    }
}

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

def get_device_name(device_id):
    """Get device name from device ID using the list_devices functionality"""
    try:
        # Import the list_devices function
        from list_devices import list_devices
        devices = list_devices()

        for device in devices:
            if device.get('id', {}).get('id') == device_id:
                return device.get('name', f'Device {device_id[:8]}...')

        # If not found, return a shortened device ID
        return f'Device {device_id[:8]}...'
    except Exception as e:
        print(f"⚠️  Could not fetch device name: {e}")
        return f'Device {device_id[:8]}...'

def get_color_scheme(key_name):
    """Get appropriate color scheme based on data type"""
    key_lower = key_name.lower()
    if 'battery' in key_lower:
        return COLOR_SCHEMES['battery']
    elif 'temp' in key_lower:
        return COLOR_SCHEMES['temperature']
    elif 'humid' in key_lower:
        return COLOR_SCHEMES['humidity']
    else:
        return COLOR_SCHEMES['default']

def get_unit_and_range(key_name):
    """Get appropriate unit and value range for different data types"""
    key_lower = key_name.lower()
    if 'battery' in key_lower:
        return '%', (0, 100)
    elif 'temp' in key_lower:
        return '°C', None  # Dynamic range for temperature
    elif 'humid' in key_lower:
        return '%', (0, 100)
    else:
        return '', None  # No unit, dynamic range

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

def create_line_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit):
    """Create an enhanced line chart"""
    # Main line with gradient effect
    ax.plot(timestamps, values, linewidth=3, color=color_scheme['primary'],
            marker='o', markersize=6, markerfacecolor=color_scheme['secondary'],
            markeredgecolor='white', markeredgewidth=2, alpha=0.9, label=f'{key_name.title()}')

    # Add trend line if enough data points
    if len(values) > 5:
        z = np.polyfit(range(len(values)), values, 1)
        p = np.poly1d(z)
        trend_values = p(range(len(values)))
        ax.plot(timestamps, trend_values, '--', color=color_scheme['secondary'],
                alpha=0.7, linewidth=2, label='Trend')

    # Format x-axis beautifully
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(timestamps)//8)))

    return ax

def create_area_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit):
    """Create a beautiful area chart with gradient"""
    # Create gradient fill
    ax.fill_between(timestamps, values, alpha=0.3, color=color_scheme['primary'])
    ax.plot(timestamps, values, linewidth=3, color=color_scheme['primary'],
            marker='o', markersize=5, markerfacecolor=color_scheme['secondary'],
            markeredgecolor='white', markeredgewidth=1.5)

    # Add average line
    avg_value = np.mean(values)
    ax.axhline(y=avg_value, color=color_scheme['secondary'], linestyle='--',
               alpha=0.8, linewidth=2, label=f'Average: {avg_value:.1f}{unit}')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(timestamps)//8)))

    return ax

def create_bar_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit):
    """Create an enhanced bar chart with color coding"""
    # Color bars based on value ranges
    colors = []
    for value in values:
        if 'battery' in key_name.lower():
            if value < 20:
                colors.append(color_scheme.get('critical', '#E74C3C'))
            elif value < 50:
                colors.append('#F39C12')  # Orange for medium
            else:
                colors.append(color_scheme['primary'])
        else:
            colors.append(color_scheme['primary'])

    bars = ax.bar(range(len(values)), values, color=colors, alpha=0.8,
                  edgecolor='white', linewidth=1)

    # Add value labels on top of bars (for smaller datasets)
    if len(values) <= 20:
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Format x-axis
    step = max(1, len(timestamps) // 10)
    tick_positions = range(0, len(timestamps), step)
    tick_labels = [timestamps[i].strftime('%H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)

    return ax

def create_scatter_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit):
    """Create an enhanced scatter plot with size variation"""
    # Vary point sizes based on values
    sizes = [50 + (v - min(values)) / (max(values) - min(values) + 0.001) * 100 for v in values]

    scatter = ax.scatter(timestamps, values, c=values, s=sizes,
                        cmap='viridis', alpha=0.7, edgecolors='white', linewidth=1)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
    cbar.set_label(f'{key_name.title()} ({unit})', rotation=270, labelpad=20)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(timestamps)//8)))

    return ax

def enhance_plot_styling(ax, values, key_name, device_name, unit, value_range, color_scheme):
    """Apply enhanced styling to the plot"""
    # Beautiful title with device name
    title = f'{key_name.title()} - {device_name}'
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20,
                color='#2C3E50')

    # Enhanced axis labels
    ax.set_xlabel('Time', fontsize=14, fontweight='bold', color='#34495E')
    ylabel = f'{key_name.title()} ({unit})' if unit else key_name.title()
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold', color='#34495E')

    # Set appropriate y-axis limits
    if value_range:
        ax.set_ylim(value_range)
    elif values:
        min_val, max_val = min(values), max(values)
        padding = (max_val - min_val) * 0.1 if max_val != min_val else 1
        ax.set_ylim(min_val - padding, max_val + padding)

    # Beautiful grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)

    # Enhanced spines
    for spine in ax.spines.values():
        spine.set_color('#BDC3C7')
        spine.set_linewidth(1)

    # Rotate x-axis labels for better readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Add legend if multiple elements
    if ax.get_legend_handles_labels()[0]:
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)

def add_data_insights(fig, values, unit, color_scheme):
    """Add statistical insights to the plot"""
    if not values:
        return

    avg_value = np.mean(values)
    min_value = np.min(values)
    max_value = np.max(values)
    std_value = np.std(values)

    # Create insights text box
    insights_text = (
        f'📊 Data Insights:\n'
        f'Average: {avg_value:.1f}{unit}\n'
        f'Range: {min_value:.1f}{unit} - {max_value:.1f}{unit}\n'
        f'Std Dev: {std_value:.1f}{unit}\n'
        f'Data Points: {len(values)}'
    )

    # Add text box with insights
    fig.text(0.02, 0.02, insights_text, fontsize=10,
             bbox=dict(boxstyle="round,pad=0.5", facecolor=color_scheme['primary'],
                      alpha=0.1, edgecolor=color_scheme['secondary']),
             verticalalignment='bottom')

def create_telemetry_plot(timestamps, values, device_id, key_name, save_dir, chart_type="bar"):
    """Create a beautiful, enhanced visualization of telemetry values over time

    Args:
        timestamps: List of datetime objects
        values: List of numeric values
        device_id: Device identifier
        key_name: Name of the telemetry key being plotted
        save_dir: Directory to save the plot
        chart_type: Type of chart to create ("line", "bar", "area", "scatter")

    Returns:
        str: Path to the saved plot file
    """
    # Get enhanced styling information
    device_name = get_device_name(device_id)
    color_scheme = get_color_scheme(key_name)
    unit, value_range = get_unit_and_range(key_name)

    # Create figure with enhanced styling
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FFFFFF')

    # Create the appropriate chart type
    if chart_type == "area":
        create_area_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit)
    elif chart_type == "scatter":
        create_scatter_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit)
    elif chart_type == "line":
        create_line_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit)
    else:  # default to enhanced bar chart
        create_bar_chart(ax, timestamps, values, color_scheme, key_name, device_name, unit)

    # Apply enhanced styling
    enhance_plot_styling(ax, values, key_name, device_name, unit, value_range, color_scheme)

    # Add data insights
    add_data_insights(fig, values, unit, color_scheme)

    # Add timestamp info
    if timestamps:
        time_range = f"From {timestamps[0].strftime('%Y-%m-%d %H:%M')} to {timestamps[-1].strftime('%Y-%m-%d %H:%M')}"
        fig.text(0.98, 0.02, time_range, fontsize=9, ha='right', va='bottom',
                style='italic', color='#7F8C8D')

    plt.tight_layout()

    # Save with high quality and beautiful filename
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'{key_name}_{chart_type}_{device_name.replace(" ", "_")}_{timestamp_str}.png'

    # Ensure save directory exists
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#FAFAFA',
                edgecolor='none', pad_inches=0.2)

    print(f"🎨 Beautiful {chart_type.title()} chart saved: {filepath}")
    print(f"📊 Device: {device_name}")
    print(f"📈 Data: {len(values)} points of {key_name} data")

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
    # Use relative paths that work regardless of working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in container environment where files are in /app directly
    if os.path.exists(os.path.join(script_dir, "AI", "data")):
        # Host environment - data is in AI/data
        data_dir = os.path.join(script_dir, "AI", "data")
        plots_dir = os.path.join(script_dir, "AI", "plots")
    else:
        # Container environment - we are already in the AI directory context
        data_dir = os.path.join(script_dir, "data")
        plots_dir = os.path.join(script_dir, "plots")
    
    # Ensure plots directory exists
    os.makedirs(plots_dir, exist_ok=True)
    
    print(f"🔧 DEBUG: Looking for data files in: {data_dir}")
    print(f"🔧 DEBUG: Will save plots to: {plots_dir}")
    
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
    # Use relative paths that work regardless of working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in container environment where files are in /app directly
    if os.path.exists(os.path.join(script_dir, "AI", "data")):
        # Host environment - data is in AI/data
        data_dir = os.path.join(script_dir, "AI", "data")
        plots_dir = os.path.join(script_dir, "AI", "plots")
    else:
        # Container environment - we are already in the AI directory context
        data_dir = os.path.join(script_dir, "data")
        plots_dir = os.path.join(script_dir, "plots")
    
    # Ensure plots directory exists
    os.makedirs(plots_dir, exist_ok=True)
    
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in container environment where files are in /app directly
    if os.path.exists(os.path.join(script_dir, "AI", "data")):
        # Host environment - data is in AI/data
        data_dir = os.path.join(script_dir, "AI", "data")
        plots_dir = os.path.join(script_dir, "AI", "plots")
    else:
        # Container environment - we are already in the AI directory context
        data_dir = os.path.join(script_dir, "data")
        plots_dir = os.path.join(script_dir, "plots")
    
    os.makedirs(plots_dir, exist_ok=True)

    # Check if we have any data files
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
