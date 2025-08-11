"""
Battery Data Pipeline
====================

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

def run_full_pipeline(chart_type="line"):
    """Run the complete data pipeline: fetch -> plot
    
    Args:
        chart_type: Type of chart to create ("line" or "bar")
    """
    print("🚀 Starting Battery Data Pipeline")
    print("=" * 60)
    
    # Step 1: Fetch fresh data
    print("Step 1: Fetching battery data from ThingsBoard...")
    print("-" * 40)
    fetch_data()
    
    # Small delay to ensure file is written
    time.sleep(1)
    
    # Step 2: Create visualizations
    print(f"\nStep 2: Creating {chart_type} chart...")
    print("-" * 40)
    plot_latest_data(chart_type)
    
    print("\n🎉 Pipeline completed successfully!")
    print("� Check AI/plots/ for PNG visualizations")
    print("�️  Data files have been automatically cleaned up")



def main():
    """Main function - automatically runs the full pipeline"""
    import sys
    chart_type = "bar"  # Default chart type
    
    # Check for chart type argument
    if len(sys.argv) > 1:
        if sys.argv[1] in ["line", "bar"]:
            chart_type = sys.argv[1]
        else:
            print("❌ Invalid chart type. Use 'line' or 'bar'")
            print("Usage: python battery_pipeline.py [line|bar]")
            sys.exit(1)
    
    # Run the full pipeline automatically
    run_full_pipeline(chart_type)

if __name__ == "__main__":
    main()
