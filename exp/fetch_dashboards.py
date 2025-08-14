#!/usr/bin/env python3
"""
Script to fetch available dashboards from ThingsBoard API
"""

import requests
import json
import sys
from typing import List, Dict, Optional

class ThingsBoardDashboardFetcher:
    def __init__(self, base_url: str = "http://localhost:8081", username: str = None, password: str = None):
        """
        Initialize the dashboard fetcher
        
        Args:
            base_url: ThingsBoard server URL
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
    
    def authenticate(self) -> bool:
        """
        Authenticate with ThingsBoard and get JWT token
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        auth_url = f"{self.base_url}/api/auth/login"
        auth_data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            self.token = auth_response.get('token')
            
            if self.token:
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                print("✅ Authentication successful")
                return True
            else:
                print("❌ No token received in response")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def fetch_tenant_dashboards(self, page_size: int = 100, text_search: str = None) -> List[Dict]:
        """
        Fetch tenant dashboards
        
        Args:
            page_size: Number of dashboards per page
            text_search: Optional text search filter
            
        Returns:
            List of dashboard objects
        """
        url = f"{self.base_url}/api/tenant/dashboards"
        params = {
            'pageSize': page_size,
            'page': 0
        }
        
        if text_search:
            params['textSearch'] = text_search
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            dashboards = data.get('data', [])
            
            print(f"✅ Found {len(dashboards)} dashboards")
            return dashboards
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch dashboards: {e}")
            return []
    
    def fetch_customer_dashboards(self, customer_id: str, page_size: int = 100) -> List[Dict]:
        """
        Fetch customer dashboards
        
        Args:
            customer_id: Customer ID
            page_size: Number of dashboards per page
            
        Returns:
            List of dashboard objects
        """
        url = f"{self.base_url}/api/customer/{customer_id}/dashboards"
        params = {
            'pageSize': page_size,
            'page': 0
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            dashboards = data.get('data', [])
            
            print(f"✅ Found {len(dashboards)} customer dashboards")
            return dashboards
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch customer dashboards: {e}")
            return []
    
    def get_dashboard_details(self, dashboard_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific dashboard
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            Dashboard details or None if not found
        """
        url = f"{self.base_url}/api/dashboard/{dashboard_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            dashboard = response.json()
            print(f"✅ Retrieved dashboard details for: {dashboard.get('title', 'Unknown')}")
            return dashboard
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch dashboard details: {e}")
            return None
    
    def display_dashboards(self, dashboards: List[Dict]):
        """
        Display dashboard information in a formatted way
        
        Args:
            dashboards: List of dashboard objects
        """
        if not dashboards:
            print("No dashboards found.")
            return
        
        print(f"\n📊 Dashboard List ({len(dashboards)} total):")
        print("-" * 80)
        
        for i, dashboard in enumerate(dashboards, 1):
            dashboard_id = dashboard.get('id', {}).get('id', 'Unknown ID')
            title = dashboard.get('title', 'Untitled Dashboard')
            created_time = dashboard.get('createdTime', 0)
            
            # Convert timestamp to readable date
            import datetime
            created_date = datetime.datetime.fromtimestamp(created_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if created_time else 'Unknown'
            
            print(f"{i:2d}. {title}")
            print(f"    ID: {dashboard_id}")
            print(f"    Created: {created_date}")
            print(f"    URL: {self.base_url}/dashboards/{dashboard_id}")
            print()
    
    def search_dashboards(self, search_term: str) -> List[Dict]:
        """
        Search for dashboards by title
        
        Args:
            search_term: Search term to filter dashboards
            
        Returns:
            List of matching dashboards
        """
        print(f"🔍 Searching for dashboards containing: '{search_term}'")
        return self.fetch_tenant_dashboards(text_search=search_term)


def main():
    """
    Main function to demonstrate dashboard fetching
    """
    print("🚀 ThingsBoard Dashboard Fetcher")
    print("=" * 50)
    
    # Configuration - Update these values for your ThingsBoard instance
    TB_URL = "http://localhost:8081"
    USERNAME = "tenant@thingsboard.org"  # Default tenant username
    PASSWORD = "tenant"  # Default tenant password
    
    # Create fetcher instance
    fetcher = ThingsBoardDashboardFetcher(TB_URL, USERNAME, PASSWORD)
    
    # Authenticate
    if not fetcher.authenticate():
        print("❌ Authentication failed. Please check your credentials.")
        sys.exit(1)
    
    # Fetch all dashboards
    print("\n📋 Fetching all dashboards...")
    all_dashboards = fetcher.fetch_tenant_dashboards()
    fetcher.display_dashboards(all_dashboards)
    
    # Search for Energy Management dashboard
    print("\n🔍 Searching for 'Energy Management' dashboard...")
    energy_dashboards = fetcher.search_dashboards("test")
    
    if energy_dashboards:
        print(f"\nFound {len(energy_dashboards)} Energy Management dashboard(s):")
        for dashboard in energy_dashboards:
            dashboard_id = dashboard.get('id', {}).get('id')
            print(f"- {dashboard.get('title')} (ID: {dashboard_id})")
            
            # Get detailed information
            details = fetcher.get_dashboard_details(dashboard_id)
            if details:
                config = details.get('configuration', {})
                widgets = config.get('widgets', [])
                print(f"  Widgets: {len(widgets)}")
    else:
        print("No Energy Management dashboards found.")
    
    # Save results to file
    output_file = "exp/dashboards_list.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(all_dashboards, f, indent=2)
        print(f"\n💾 Dashboard list saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save dashboard list: {e}")


if __name__ == "__main__":
    main()
