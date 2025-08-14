"""
Device Data Pipeline
===================

Main script that coordinates data fetching and plotting.
Run this to fetch data and automatically create visualizations.
"""

import os
import sys
import time

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_battery_data import main as fetch_data
from plot_battery_data import plot_latest_data, plot_all_data

def format_time_range_display(time_range):
    """Format time range for display"""
    if not time_range:
        return "Not specified"

    if time_range.get('hours_back'):
        return f"Last {time_range['hours_back']} hour(s)"
    elif time_range.get('days_back'):
        return f"Last {time_range['days_back']} day(s)"
    elif time_range.get('specific_day_offset') is not None:
        offset = time_range['specific_day_offset']
        start_hour = time_range.get('start_hour', 0)
        end_hour = time_range.get('end_hour', 23)

        if offset == 0:
            day_desc = "Today"
        elif offset == 1:
            day_desc = "Yesterday"
        else:
            day_desc = f"{offset} days ago"

        if start_hour != 0 or end_hour != 23:
            return f"{day_desc} from {start_hour:02d}:00 to {end_hour:02d}:59"
        else:
            return day_desc

    return "Custom range"

def run_full_pipeline(device_id="75cc3ef0-7789-11f0-9adf-95dc3a2607cb", keys="batteryLevel",
                     chart_type="line", days_back=None, hours_back=None, time_range=None):
    """Run the complete data pipeline: fetch -> plot

    Args:
        device_id (str): Device ID to fetch data from
        keys (str): Telemetry keys to fetch (comma-separated)
        chart_type: Type of chart to create ("line", "bar", "area", "scatter")
        days_back (int, optional): Number of days back to fetch data (legacy)
        hours_back (int, optional): Number of hours back to fetch data
        time_range (dict, optional): Advanced time range specification
    """
    print("🚀 Starting Device Data Pipeline")
    print("=" * 60)
    print(f"📱 Device: {device_id}")
    print(f"🔑 Keys: {keys}")
    print(f"📊 Chart Type: {chart_type}")

    # Display time range information
    if time_range:
        time_desc = format_time_range_display(time_range)
        print(f"📅 Time Range: {time_desc}")
    elif hours_back:
        print(f"📅 Time Range: Last {hours_back} hours")
    elif days_back:
        print(f"📅 Time Range: Last {days_back} days")
    else:
        print(f"📅 Time Range: Entire history")
    print()

    # Step 1: Fetch fresh data
    print("Step 1: Fetching telemetry data from ThingsBoard...")
    print("-" * 40)
    fetch_data(device_id, keys, days_back, hours_back, time_range)
    
    # Small delay to ensure file is written
    time.sleep(1)
    
    # Step 2: Create visualizations
    print(f"\nStep 2: Creating {chart_type} chart...")
    print("-" * 40)
    plot_latest_data(chart_type)
    
    print("\n🎉 Pipeline completed successfully!")
    print("📊 Check plots/ for PNG visualizations")
    print("🗑️  Data files have been automatically cleaned up")

def main():
    """Main function - automatically runs the full pipeline"""
    import sys
    
    # Default values
    device_id = "75cc3ef0-7789-11f0-9adf-95dc3a2607cb"
    keys = "batteryLevel"
    chart_type = "line"
    days_back = None
    hours_back = None
    time_range = None
    
    # Parse command line arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ["-h", "--help"]:
            print("Usage: python device_pipeline.py [options]")
            print()
            print("Options:")
            print("  -d, --device DEVICE_ID     Device ID to fetch data from")
            print("  -k, --keys KEYS           Telemetry keys (comma-separated)")
            print("  -t, --type CHART_TYPE     Chart type: line, bar, area, scatter")
            print("  -b, --days DAYS_BACK      Number of days back to fetch")
            print("  --hours HOURS_BACK        Number of hours back to fetch")
            print("  --time-range JSON         Advanced time range (JSON format)")
            print("  -h, --help                Show this help message")
            print()
            print("Examples:")
            print("  python device_pipeline.py                                    # Default: battery data, line chart")
            print("  python device_pipeline.py -t bar                             # Bar chart")
            print("  python device_pipeline.py -d MyDevice -k temperature        # Temperature data")
            print("  python device_pipeline.py -k temperature,humidity -b 7      # Multiple keys, last 7 days")
            print("  python device_pipeline.py --hours 3                         # Last 3 hours")
            print('  python device_pipeline.py --time-range \'{"hours_back": 2}\'  # Last 2 hours (JSON)')
            print('  python device_pipeline.py --time-range \'{"specific_day_offset": 1, "start_hour": 9, "end_hour": 17}\' # Yesterday 9-17')
            sys.exit(0)
        elif arg in ["-d", "--device"]:
            if i + 1 < len(sys.argv):
                device_id = sys.argv[i + 1]
                i += 2
            else:
                print("❌ Device ID required after -d/--device")
                sys.exit(1)
        elif arg in ["-k", "--keys"]:
            if i + 1 < len(sys.argv):
                keys = sys.argv[i + 1]
                i += 2
            else:
                print("❌ Keys required after -k/--keys")
                sys.exit(1)
        elif arg in ["-t", "--type"]:
            if i + 1 < len(sys.argv):
                chart_type = sys.argv[i + 1]
                if chart_type not in ["line", "bar", "area", "scatter"]:
                    print("❌ Chart type must be 'line', 'bar', 'area', or 'scatter'")
                    sys.exit(1)
                i += 2
            else:
                print("❌ Chart type required after -t/--type")
                sys.exit(1)
        elif arg in ["-b", "--days"]:
            if i + 1 < len(sys.argv):
                try:
                    days_back = int(sys.argv[i + 1])
                    if days_back <= 0:
                        print("❌ Days back must be a positive number")
                        sys.exit(1)
                    i += 2
                except ValueError:
                    print("❌ Invalid days back value")
                    sys.exit(1)
            else:
                print("❌ Number of days required after -b/--days")
                sys.exit(1)
        elif arg == "--hours":
            if i + 1 < len(sys.argv):
                try:
                    hours_back = int(sys.argv[i + 1])
                    if hours_back <= 0:
                        print("❌ Hours back must be a positive number")
                        sys.exit(1)
                    i += 2
                except ValueError:
                    print("❌ Invalid hours back value")
                    sys.exit(1)
            else:
                print("❌ Number of hours required after --hours")
                sys.exit(1)
        elif arg == "--time-range":
            if i + 1 < len(sys.argv):
                try:
                    import json
                    time_range = json.loads(sys.argv[i + 1])
                    i += 2
                except json.JSONDecodeError:
                    print("❌ Invalid JSON format for time range")
                    sys.exit(1)
            else:
                print("❌ JSON time range required after --time-range")
                sys.exit(1)
        else:
            print(f"❌ Unknown argument: {arg}")
            print("Use -h or --help for usage information")
            sys.exit(1)
    
    # Run the full pipeline automatically
    run_full_pipeline(device_id, keys, chart_type, days_back, hours_back, time_range)

if __name__ == "__main__":
    main()
