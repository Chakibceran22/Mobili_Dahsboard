"""
ThingsBoard Device Data Fetcher
===============================

This script demonstrates how ThingsBoard time series widgets fetch data.
It can fetch any telemetry data from any device using device ID and keys.
"""

import requests
import time
import json
import os
from datetime import datetime, timedelta

def calculate_time_range(end_time, days_back=None, hours_back=None, time_range=None):
    """Calculate start_time, description, and custom_end_time based on various time range parameters"""

    # Handle new time_range format first
    if time_range:
        return calculate_advanced_time_range(end_time, time_range)

    # Handle hours_back
    if hours_back is not None:
        start_time = end_time - (hours_back * 60 * 60 * 1000)
        description = f"last {hours_back} hour(s)"
        return start_time, description, None

    # Handle days_back (legacy)
    if days_back is not None:
        start_time = end_time - (days_back * 24 * 60 * 60 * 1000)
        description = f"last {days_back} day(s)"
        return start_time, description, None

    # Default: entire history
    start_time = 0
    description = "ENTIRE telemetry history"
    return start_time, description, None

def calculate_advanced_time_range(end_time, time_range):
    """Calculate time range for advanced specifications"""
    now = datetime.fromtimestamp(end_time / 1000)

    # Handle simple hours_back or days_back
    if time_range.get('hours_back'):
        hours = time_range['hours_back']
        start_time = end_time - (hours * 60 * 60 * 1000)
        return start_time, f"last {hours} hour(s)", None

    if time_range.get('days_back'):
        days = time_range['days_back']
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        return start_time, f"last {days} day(s)", None

    # Handle specific day with optional hour range
    if time_range.get('specific_day_offset') is not None:
        day_offset = time_range['specific_day_offset']
        target_date = now - timedelta(days=day_offset)

        # Set start and end hours
        start_hour = time_range.get('start_hour', 0)
        end_hour = time_range.get('end_hour', 23)

        # Create start and end datetime objects
        start_dt = target_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_dt = target_date.replace(hour=end_hour, minute=59, second=59, microsecond=999999)

        start_time = int(start_dt.timestamp() * 1000)
        custom_end_time = int(end_dt.timestamp() * 1000)

        # Create description
        if day_offset == 0:
            day_desc = "today"
        elif day_offset == 1:
            day_desc = "yesterday"
        else:
            day_desc = f"{day_offset} days ago"

        if start_hour != 0 or end_hour != 23:
            time_desc = f"{day_desc} from {start_hour:02d}:00 to {end_hour:02d}:59"
        else:
            time_desc = day_desc

        return start_time, time_desc, custom_end_time

    # Fallback
    return 0, "entire history", None

def get_device_timeseries_by_id(device_id, jwt_token, keys="batteryLevel", base_url="http://localhost:8081",
                                days_back=None, hours_back=None, time_range=None):
    """Fetch time series data directly using device ID - same as widgets do

    Args:
        device_id: Device ID to fetch data from
        jwt_token: Authentication token
        keys: Telemetry keys to fetch (comma-separated)
        base_url: ThingsBoard base URL
        days_back: Number of days back (legacy parameter)
        hours_back: Number of hours back
        time_range: Dictionary with detailed time range specification:
            {
                'hours_back': int,
                'days_back': int,
                'specific_day_offset': int,  # 0=today, 1=yesterday, etc.
                'start_hour': int,           # 0-23
                'end_hour': int              # 0-23
            }
    """
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }

    # Calculate time range based on parameters
    current_time = int(time.time() * 1000)
    start_time, time_description, custom_end_time = calculate_time_range(current_time, days_back, hours_back, time_range)

    # Use custom end time if specified (for specific day ranges), otherwise use current time
    end_time = custom_end_time if custom_end_time else current_time

    print(f"📊 Fetching {keys} telemetry for {time_description}...")

    url = f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
    params = {
        'keys': keys,
        'startTs': start_time,
        'endTs': end_time,
        'agg': 'NONE',
        'limit': 10000  # Increased limit for more data
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"📊 {keys} Time Series Data (same as widget sees):")
        print("-" * 50)
        
        # Get the first key from the keys parameter if it contains multiple keys
        first_key = keys.split(',')[0].strip() if ',' in keys else keys
        telemetry_data = data.get(first_key, [])
        if telemetry_data:
            print(f"Found {len(telemetry_data)} data points:")
            for i, point in enumerate(telemetry_data):
                timestamp = point['ts']
                value = point['value']
                readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))
                unit = "%" if "battery" in first_key.lower() else ""
                print(f"  {i+1:2}. {readable_time}: {value}{unit}")
            
            # Save data to JSON file for plotting
            save_telemetry_data(telemetry_data, device_id, first_key)
            return telemetry_data
        else:
            print(f"No {keys} data found in the specified time range.")
            return []
    else:
        print(f"❌ Failed to fetch data: {response.status_code} - {response.text}")
        return []

def save_telemetry_data(telemetry_data, device_id, key_name):
    """Save telemetry data to JSON file for later plotting"""
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"{key_name}_data_{device_id}_{timestamp}.json"
    filepath = os.path.join("AI/data", filename)
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Prepare data for JSON serialization
    data_to_save = {
        'device_id': device_id,
        'key_name': key_name,
        'fetch_time': timestamp,
        'data_points': len(telemetry_data),
        'telemetry_data': telemetry_data
    }
    
    with open(filepath, 'w') as f:
        json.dump(data_to_save, f, indent=2)
    
    print(f"💾 Data saved to: {filepath}")
    return filepath

def login_and_get_token(username="tenant@thingsboard.org", password="tenant", base_url="http://localhost:8081"):
    """Login and get JWT token for API calls"""
    login_data = {"username": username, "password": password}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['token']
    return None

def get_device_info(device_id, jwt_token, base_url="http://localhost:8081"):
    """Get device information"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{base_url}/api/device/{device_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None



def fetch_with_pagination(device_id, jwt_token, keys="batteryLevel", base_url="http://localhost:8081", days_back=None):
    """Fetch data with pagination to get more than 10,000 points"""
    print("🔄 Fetching data with pagination for large datasets...")
    
    all_telemetry_data = []
    limit = 10000
    
    # Calculate time range
    end_time = int(time.time() * 1000)
    if days_back is None:
        start_time = 0
        print(f"📊 Fetching ENTIRE {keys} history with pagination...")
    else:
        start_time = end_time - (days_back * 24 * 60 * 60 * 1000)
        print(f"📊 Fetching {days_back} days of {keys} history with pagination...")
    
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    current_end_time = end_time
    page = 1
    first_key = keys.split(',')[0].strip() if ',' in keys else keys
    
    while True:
        print(f"📄 Fetching page {page}...")
        
        url = f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        params = {
            'keys': keys,
            'startTs': start_time,
            'endTs': current_end_time,
            'agg': 'NONE',
            'limit': limit
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page {page}: {response.status_code}")
            break
        
        data = response.json()
        telemetry_data = data.get(first_key, [])
        
        if not telemetry_data:
            print(f"✅ No more data found. Completed after {page-1} pages.")
            break
        
        print(f"   Found {len(telemetry_data)} points on page {page}")
        all_telemetry_data.extend(telemetry_data)
        
        # If we got less than the limit, we've reached the end
        if len(telemetry_data) < limit:
            print(f"✅ Reached end of data. Total pages: {page}")
            break
        
        # Update end time to the timestamp of the last record for next page
        current_end_time = telemetry_data[-1]['ts'] - 1
        page += 1
        
        # Safety check to prevent infinite loops
        if page > 100:
            print("⚠️ Reached maximum page limit (100). Stopping pagination.")
            break
    
    print(f"📊 Total data points collected: {len(all_telemetry_data)}")
    return all_telemetry_data

def main(device_id="d1089320-6acf-11f0-8d88-0f481e2e4d44", keys="batteryLevel", days_back=None,
         hours_back=None, time_range=None):
    """Main function - demonstrates how widgets fetch telemetry data

    Args:
        device_id (str): Device ID to fetch data from. Default: d1089320-6acf-11f0-8d88-0f481e2e4d44 (My Battery Sensor)
        keys (str): Telemetry keys to fetch (comma-separated). Default: batteryLevel
        days_back (int, optional): Number of days back to fetch data (legacy parameter)
        hours_back (int, optional): Number of hours back to fetch data
        time_range (dict, optional): Advanced time range specification
                                  If None, fetches entire history.
                                  Examples: 1 (last 24h), 7 (last week), 30 (last month)
    """
    print(f"� ThingsBoard Device Data Fetcher")
    print("=" * 50)
    print("This shows exactly what the time series widget sees!")
    
    if days_back is None:
        print(f"📊 Fetching ENTIRE {keys} history...")
    else:
        print(f"📊 Fetching {keys} history for last {days_back} days...")
    print()
    
    print(f"📱 Device ID: {device_id}")
    print(f"🔑 Keys: {keys}")
    print()
    
    # Step 1: Login to get JWT token
    print("🔐 Logging in...")
    jwt_token = login_and_get_token()
    if not jwt_token:
        print("❌ Failed to login. Check ThingsBoard is running and credentials are correct.")
        return
    print("✅ Login successful!")
    
    # Step 2: Get device information
    print("📋 Getting device information...")
    device_info = get_device_info(device_id, jwt_token)
    if device_info:
        print(f"✅ Device found: {device_info.get('name', 'Unknown')}")
        print(f"   Type: {device_info.get('type', 'Unknown')}")
    else:
        print("⚠️  Could not get device info, but continuing...")
    
    # Step 3: Fetch time series data
    print(f"\n📊 Fetching {keys} history...")
    telemetry_data = get_device_timeseries_by_id(device_id, jwt_token, keys,
                                                days_back=days_back, hours_back=hours_back, time_range=time_range)
    
    print("\n" + "=" * 50)
    print("🎯 This is exactly the same data that appears in your")
    print("   ThingsBoard time series widget!")
    
    if telemetry_data:
        print(f"📈 Ready for plotting! Data contains {len(telemetry_data)} points")
        
        # Show data range info
        if len(telemetry_data) > 0:
            first_point = telemetry_data[0]
            last_point = telemetry_data[-1]
            first_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(first_point['ts']/1000))
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_point['ts']/1000))
            print(f"📅 Data range: {first_time} to {last_time}")
    else:
        print(f"❌ No {keys} data found for the specified time range.")
    
    return telemetry_data

if __name__ == "__main__":
    import sys
    
    # Default values
    device_id = "75cc3ef0-7789-11f0-9adf-95dc3a2607cb"
    keys = "batteryLevel"
    days_back = None
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        # First argument could be device_id or days_back
        try:
            days_back = int(sys.argv[1])
            if days_back <= 0:
                print("❌ Days back must be a positive number")
                sys.exit(1)
        except ValueError:
            # If not a number, treat as device_id
            device_id = sys.argv[1]
            if len(sys.argv) > 2:
                keys = sys.argv[2]
            if len(sys.argv) > 3:
                try:
                    days_back = int(sys.argv[3])
                    if days_back <= 0:
                        print("❌ Days back must be a positive number")
                        sys.exit(1)
                except ValueError:
                    print("❌ Invalid days_back argument")
                    sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python fetch_battery_data.py [device_id] [keys] [days_back]")
        print("       python fetch_battery_data.py [days_back]")
        print()
        print("Examples:")
        print("  python fetch_battery_data.py                                    # Default device, batteryLevel, entire history")
        print("  python fetch_battery_data.py 7                                  # Default device, batteryLevel, last 7 days")
        print("  python fetch_battery_data.py d1089320-6acf-11f0-8d88-0f481e2e4d44 batteryLevel   # Specific device and key, entire history")
        print("  python fetch_battery_data.py MyDeviceId temperature,humidity 30 # Multiple keys, last 30 days")
        sys.exit(0)
    
    main(device_id, keys, days_back)
