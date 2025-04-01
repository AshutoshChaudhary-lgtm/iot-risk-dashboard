from fastapi import APIRouter, HTTPException
from src.shodan_client import ShodanClient
from src.utils.geo_mapper import map_devices
from src.models.risk import Risk
import os
import requests
import json
import traceback

# Uncomment the alert import now that things are working
from src.utils.alert_system import send_email_alert

router = APIRouter()
shodan_client = ShodanClient(api_key=os.getenv("SHODAN_API_KEY"))



@router.get("/devices")
async def get_devices(ip_range: str):
    try:
        # Get devices with better error handling
        print(f"Searching for devices with query: {ip_range}")
        devices = shodan_client.search_devices(ip_range)
        
        # Handle empty results gracefully
        if not devices:
            print(f"No devices found for query: {ip_range}")
            return {
                "devices": [],
                "mapped": [],
                "risks": [],
                "warning": "No devices found or API connection issue. Try checking /test-connection endpoint."
            }
        
        print(f"Found {len(devices)} devices")
        mapped_devices = map_devices(devices)
        risks = []
        
        for device in devices:
            # Extract ports and services
            ports = device.get("ports", [])
            services = []
            for module in device.get("data", []):
                if module.get("_shodan", {}).get("module"):
                    services.append(module.get("_shodan", {}).get("module"))
            
            # Calculate risk
            vulns = device.get("vulns", {})
            if isinstance(vulns, dict):
                # Convert dict to list of dicts with the CVE ID included
                vulns_list = []
                for cve_id, vuln_info in vulns.items():
                    vuln_dict = vuln_info.copy() if isinstance(vuln_info, dict) else {'description': str(vuln_info)}
                    vuln_dict['id'] = cve_id
                    vulns_list.append(vuln_dict)
                vulns = vulns_list
            
            risk = Risk(device_id=device.get("id", device.get("ip_str", "unknown")), 
                      risk_score=0, vulnerabilities=vulns, ports=ports)
            risk_score = risk.calculate_risk_score()
            
            # Add OS and services to risk model
            risk_data = risk.__repr__()
            risk_data["os"] = device.get("os", "Unknown")
            risk_data["services"] = services
            risks.append(risk_data)
            
            # Enable alert for high-risk devices
            try:
                if risk_score > 75:
                    recipient = os.getenv("ALERT_EMAIL", "admin@example.com")
                    print(f"Sending alert for high-risk device: {device.get('ip_str')} (score: {risk_score})")
                    send_email_alert(recipient, device, risk_score)
            except Exception as alert_err:
                print(f"Failed to send alert: {alert_err}")
            
        return {"devices": devices, "mapped": mapped_devices, "risks": risks}
    except Exception as e:
        print(f"Error in get_devices: {str(e)}")
        traceback.print_exc()
        return {
            "error": str(e),
            "devices": [],
            "mapped": [],
            "risks": []
        }