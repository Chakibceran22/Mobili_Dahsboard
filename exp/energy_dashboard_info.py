#!/usr/bin/env python3
"""
Script to fetch detailed information about the Energy Management dashboard
"""

import requests
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime

class EnergyDashboardAnalyzer:
    def __init__(self, base_url: str = "http://localhost:8081", username: str = None, password: str = None):
        """
        Initialize the energy dashboard analyzer
        
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
        
        # Energy Management Dashboard ID from your dashboards_list.json
        self.energy_dashboard_id = "1325bb30-6c87-11f0-9af6-5784d6ad9acd"
    
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
    
    def get_dashboard_details(self) -> Optional[Dict]:
        """
        Get detailed information about the Energy Management dashboard
        
        Returns:
            Dashboard details or None if not found
        """
        url = f"{self.base_url}/api/dashboard/{self.energy_dashboard_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            dashboard = response.json()
            print(f"✅ Retrieved Energy Management dashboard details")
            return dashboard
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch dashboard details: {e}")
            return None
    
    def analyze_widgets(self, dashboard_config: Dict) -> List[Dict]:
        """
        Analyze all widgets in the dashboard configuration
        
        Args:
            dashboard_config: Dashboard configuration object
            
        Returns:
            List of analyzed widget information
        """
        widgets = dashboard_config.get('widgets', {})
        widget_analysis = []
        
        print(f"\n📊 Analyzing {len(widgets)} widgets:")
        print("-" * 60)
        
        for widget_id, widget_data in widgets.items():
            widget_info = {
                'id': widget_id,
                'type': widget_data.get('type', 'Unknown'),
                'title': widget_data.get('config', {}).get('title', 'Untitled Widget'),
                'size_x': widget_data.get('sizeX', 0),
                'size_y': widget_data.get('sizeY', 0),
                'position_x': widget_data.get('col', 0),
                'position_y': widget_data.get('row', 0),
                'datasources': [],
                'settings': widget_data.get('config', {}).get('settings', {}),
                'widget_type': widget_data.get('bundleAlias', 'Unknown')
            }
            
            # Analyze datasources
            datasources = widget_data.get('config', {}).get('datasources', [])
            for ds in datasources:
                ds_info = {
                    'type': ds.get('type', 'Unknown'),
                    'name': ds.get('name', 'Unnamed'),
                    'entity_type': ds.get('entityType', 'Unknown'),
                    'keys': [key.get('name', 'Unknown') for key in ds.get('dataKeys', [])]
                }
                widget_info['datasources'].append(ds_info)
            
            widget_analysis.append(widget_info)
            
            # Display widget info
            print(f"Widget: {widget_info['title']}")
            print(f"  Type: {widget_info['type']} ({widget_info['widget_type']})")
            print(f"  Size: {widget_info['size_x']}x{widget_info['size_y']}")
            print(f"  Position: ({widget_info['position_x']}, {widget_info['position_y']})")
            print(f"  Datasources: {len(widget_info['datasources'])}")
            
            for i, ds in enumerate(widget_info['datasources'], 1):
                print(f"    {i}. {ds['name']} ({ds['type']}) - Keys: {', '.join(ds['keys'])}")
            print()
        
        return widget_analysis
    
    def analyze_grid_settings(self, dashboard_config: Dict) -> Dict:
        """
        Analyze grid settings and layout
        
        Args:
            dashboard_config: Dashboard configuration object
            
        Returns:
            Grid settings information
        """
        grid_settings = dashboard_config.get('gridSettings', {})
        
        print("\n🎯 Grid Settings:")
        print("-" * 30)
        print(f"Background Color: {grid_settings.get('backgroundColor', 'Default')}")
        print(f"Background Size Mode: {grid_settings.get('backgroundSizeMode', 'Default')}")
        print(f"Auto Fill Height: {grid_settings.get('autoFillHeight', False)}")
        print(f"Columns: {grid_settings.get('columns', 'Auto')}")
        print(f"Margins: {grid_settings.get('margin', 'Default')}")
        
        return grid_settings
    
    def analyze_states(self, dashboard_config: Dict) -> List[Dict]:
        """
        Analyze dashboard states configuration
        
        Args:
            dashboard_config: Dashboard configuration object
            
        Returns:
            List of state configurations
        """
        states = dashboard_config.get('states', {})
        
        print(f"\n🔄 Dashboard States ({len(states)}):")
        print("-" * 40)
        
        state_analysis = []
        for state_id, state_data in states.items():
            state_info = {
                'id': state_id,
                'name': state_data.get('name', 'Unnamed State'),
                'root': state_data.get('root', False),
                'layouts': state_data.get('layouts', {})
            }
            
            state_analysis.append(state_info)
            
            print(f"State: {state_info['name']} ({'Root' if state_info['root'] else 'Child'})")
            print(f"  Layouts: {list(state_info['layouts'].keys())}")
            print()
        
        return state_analysis
    
    def get_entity_information(self, entity_id: str, entity_type: str) -> Optional[Dict]:
        """
        Get information about entities used in the dashboard
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type (DEVICE, ASSET, etc.)
            
        Returns:
            Entity information or None
        """
        url = f"{self.base_url}/api/{entity_type.lower()}/{entity_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def save_detailed_report(self, dashboard_data: Dict, widget_analysis: List[Dict], 
                           grid_settings: Dict, states: List[Dict]):
        """
        Save detailed analysis report to file
        
        Args:
            dashboard_data: Raw dashboard data
            widget_analysis: Analyzed widget information
            grid_settings: Grid configuration
            states: State configurations
        """
        report = {
            'dashboard_info': {
                'id': dashboard_data.get('id', {}).get('id'),
                'title': dashboard_data.get('title'),
                'created_time': dashboard_data.get('createdTime'),
                'created_date': datetime.fromtimestamp(
                    dashboard_data.get('createdTime', 0) / 1000
                ).strftime('%Y-%m-%d %H:%M:%S'),
                'version': dashboard_data.get('version'),
                'image': dashboard_data.get('image')
            },
            'summary': {
                'total_widgets': len(widget_analysis),
                'widget_types': list(set([w['type'] for w in widget_analysis])),
                'total_datasources': sum(len(w['datasources']) for w in widget_analysis),
                'total_states': len(states)
            },
            'widgets': widget_analysis,
            'grid_settings': grid_settings,
            'states': states,
            'raw_configuration': dashboard_data.get('configuration', {})
        }
        
        # Save to file
        filename = f"exp/energy_dashboard_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Detailed report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
    
    def display_summary(self, dashboard_data: Dict, widget_analysis: List[Dict]):
        """
        Display a summary of the Energy Management dashboard
        
        Args:
            dashboard_data: Dashboard data
            widget_analysis: Widget analysis results
        """
        print("\n" + "="*80)
        print("📊 ENERGY MANAGEMENT DASHBOARD SUMMARY")
        print("="*80)
        
        # Basic info
        created_date = datetime.fromtimestamp(
            dashboard_data.get('createdTime', 0) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Title: {dashboard_data.get('title')}")
        print(f"ID: {dashboard_data.get('id', {}).get('id')}")
        print(f"Created: {created_date}")
        print(f"Version: {dashboard_data.get('version')}")
        print(f"Image: {dashboard_data.get('image', 'None')}")
        
        # Widget summary
        widget_types = {}
        total_datasources = 0
        
        for widget in widget_analysis:
            widget_type = widget['type']
            widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
            total_datasources += len(widget['datasources'])
        
        print(f"\nWidgets: {len(widget_analysis)} total")
        for widget_type, count in widget_types.items():
            print(f"  - {widget_type}: {count}")
        
        print(f"Total Datasources: {total_datasources}")
        
        # URL
        print(f"\nDashboard URL: {self.base_url}/dashboards/{self.energy_dashboard_id}")


def main():
    """
    Main function to analyze the Energy Management dashboard
    """
    print("⚡ Energy Management Dashboard Analyzer")
    print("=" * 60)
    
    # Configuration - Update these values for your ThingsBoard instance
    TB_URL = "http://localhost:8081"
    USERNAME = "tenant@thingsboard.org"  # Default tenant username
    PASSWORD = "tenant"  # Default tenant password
    
    # Create analyzer instance
    analyzer = EnergyDashboardAnalyzer(TB_URL, USERNAME, PASSWORD)
    
    # Authenticate
    if not analyzer.authenticate():
        print("❌ Authentication failed. Please check your credentials.")
        sys.exit(1)
    
    # Get dashboard details
    print(f"\n📋 Fetching Energy Management dashboard details...")
    dashboard_data = analyzer.get_dashboard_details()
    
    if not dashboard_data:
        print("❌ Could not retrieve dashboard data.")
        sys.exit(1)
    
    # Analyze dashboard configuration
    config = dashboard_data.get('configuration', {})
    
    # Analyze widgets
    widget_analysis = analyzer.analyze_widgets(config)
    
    # Analyze grid settings
    grid_settings = analyzer.analyze_grid_settings(config)
    
    # Analyze states
    states = analyzer.analyze_states(config)
    
    # Display summary
    analyzer.display_summary(dashboard_data, widget_analysis)
    
    # Save detailed report
    analyzer.save_detailed_report(dashboard_data, widget_analysis, grid_settings, states)
    
    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
