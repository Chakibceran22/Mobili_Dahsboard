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

def run_full_pipeline(device_id="d1089320-6acf-11f0-8d88-0f481e2e4d44", keys="batteryLevel", chart_type="line", days_back=None):
    """Run the complete data pipeline: fetch -> plot
    
    Args:
        device_id (str): Device ID to fetch data from
        keys (str): Telemetry keys to fetch (comma-separated)
        chart_type: Type of chart to create ("line" or "bar")
        days_back (int, optional): Number of days back to fetch data
    """
    print("🚀 Starting Device Data Pipeline")
    print("=" * 60)
    print(f"📱 Device: {device_id}")
    print(f"🔑 Keys: {keys}")
    print(f"📊 Chart Type: {chart_type}")
    if days_back:
        print(f"📅 Time Range: Last {days_back} days")
    else:
        print(f"📅 Time Range: Entire history")
    print()
    
    # Step 1: Fetch fresh data
    print("Step 1: Fetching telemetry data from ThingsBoard...")
    print("-" * 40)
    fetch_data(device_id, keys, days_back)
    
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
    device_id = "d1089320-6acf-11f0-8d88-0f481e2e4d44"
    keys = "batteryLevel"
    chart_type = "line"
    days_back = None
    
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
            print("  -t, --type CHART_TYPE     Chart type: line or bar")
            print("  -b, --days DAYS_BACK      Number of days back to fetch")
            print("  -h, --help                Show this help message")
            print()
            print("Examples:")
            print("  python device_pipeline.py                                    # Default: battery data, line chart")
            print("  python device_pipeline.py -t bar                             # Bar chart")
            print("  python device_pipeline.py -d MyDevice -k temperature        # Temperature data")
            print("  python device_pipeline.py -k temperature,humidity -b 7      # Multiple keys, last 7 days")
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
                if chart_type not in ["line", "bar"]:
                    print("❌ Chart type must be 'line' or 'bar'")
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
        else:
            print(f"❌ Unknown argument: {arg}")
            print("Use -h or --help for usage information")
            sys.exit(1)
    
    # Run the full pipeline automatically
    run_full_pipeline(device_id, keys, chart_type, days_back)

if __name__ == "__main__":
    main()
