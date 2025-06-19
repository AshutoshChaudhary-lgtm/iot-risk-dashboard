"""
Integration with Shodan's Monitor API to track network changes over time
"""
import os
import requests
import json
import time
from datetime import datetime

class NetworkMonitor:
    def __init__(self, api_key=None):
        """Initialize the NetworkMonitor with Shodan API key"""
        self.api_key = api_key or os.getenv("SHODAN_API_KEY")
        
        if not self.api_key:
            raise ValueError("No Shodan API key provided for network monitor")
            
    def create_network_alert(self, name, ip_range, triggers=None):
        """
        Create a network alert to monitor changes in an IP range
        
        Parameters:
        - name: Alert name
        - ip_range: IP range to monitor (CIDR notation)
        - triggers: List of trigger names, default: ["malware", "vulnerable", "open_database", "iot"]
        
        Returns: Alert ID if successful
        """
        # Default triggers if none provided
        if triggers is None:
            triggers = ["malware", "vulnerable", "open_database", "iot"]
            
        try:
            url = f"https://api.shodan.io/shodan/alert?key={self.api_key}"
            data = {
                "name": name,
                "filters": {
                    "ip": ip_range
                },
                "triggers": triggers
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Created alert {name} with ID: {result.get('id')}")
                return result.get('id')
            else:
                print(f"Failed to create alert. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating network alert: {e}")
            return None
            
    def list_alerts(self):
        """List all configured network alerts"""
        try:
            url = f"https://api.shodan.io/shodan/alert/info?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to list alerts. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error listing network alerts: {e}")
            return []
            
    def get_alert_details(self, alert_id):
        """Get details about a specific alert"""
        try:
            url = f"https://api.shodan.io/shodan/alert/{alert_id}/info?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get alert details. Status code: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Error getting alert details: {e}")
            return {}
            
    def get_triggered_notifications(self, alert_id):
        """Get notifications for triggered alerts"""
        try:
            url = f"https://api.shodan.io/shodan/alert/{alert_id}/notifier?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get notifications. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting alert notifications: {e}")
            return []
