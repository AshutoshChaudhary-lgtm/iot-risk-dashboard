from fastapi import APIRouter, HTTPException
from src.shodan_client import ShodanClient
from src.utils.geo_mapper import map_devices
from src.utils.banner_parser import get_device_banners
from src.utils.exploit_finder import enrich_vulnerability_data
from src.models.risk import Risk
import os
import requests
import json
import traceback

# Uncomment the alert import now that things are working
from src.utils.alert_system import send_email_alert

router = APIRouter()
shodan_client = ShodanClient(api_key=os.getenv("SHODAN_API_KEY"))



@router.post("/scan")
async def request_scan(ip_address: str):
    """Request Shodan to scan a specific IP address"""
    try:
        result = shodan_client.scan_ip(ip_address)
        return {
            "status": "success",
            "message": f"Scan requested for {ip_address}",
            "details": result
        }
    except Exception as e:
        print(f"Error requesting scan: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to request scan: {str(e)}"
        }

@router.get("/domain/{domain}")
async def get_domain_info(domain: str):
    """Get information about a domain from Shodan"""
    try:
        domain_info = shodan_client.get_domain_info(domain)
        return {
            "status": "success",
            "domain": domain,
            "info": domain_info
        }
    except Exception as e:
        print(f"Error getting domain info: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to retrieve domain information: {str(e)}"
        }

@router.get("/alerts")
async def list_network_alerts():
    """List all configured network alerts"""
    try:
        alerts = shodan_client.list_alerts()
        return {
            "status": "success",
            "alerts": alerts
        }
    except Exception as e:
        print(f"Error listing alerts: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to list alerts: {str(e)}"
        }

@router.post("/alerts")
async def create_network_alert(name: str, network: str, triggers: str = None):
    """Create a new network alert
    
    Args:
        name: Name of the alert
        network: Network range in CIDR notation (e.g., "192.168.1.0/24")
        triggers: Comma-separated list of trigger names (optional)
    """
    try:
        # Parse triggers if provided
        trigger_list = None
        if triggers:
            trigger_list = [t.strip() for t in triggers.split(",")]
            
        result = shodan_client.create_network_alert(name, network, trigger_list)
        return {
            "status": "success",
            "message": f"Alert '{name}' created for network {network}",
            "alert": result
        }
    except Exception as e:
        print(f"Error creating alert: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create alert: {str(e)}"
        }

@router.get("/exposure/{domain}")
async def get_exposure_report(domain: str):
    """Get an internet exposure report for an organization domain"""
    try:
        report = shodan_client.get_exposure_report(domain)
        return {
            "status": "success",
            "domain": domain,
            "report": report
        }
    except Exception as e:
        print(f"Error generating exposure report: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate exposure report: {str(e)}"
        }

@router.post("/toggle-demo")
async def toggle_demo_mode(enable: bool = True):
    """Toggle demo mode for testing without a valid API key"""
    try:
        # Set demo mode on the shodan client instance
        shodan_client.demo_mode = enable
        
        return {
            "status": "success",
            "message": f"Demo mode {'enabled' if enable else 'disabled'}",
            "demo_mode": enable
        }
    except Exception as e:
        print(f"Error toggling demo mode: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to toggle demo mode: {str(e)}"
        }

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
                
                # Enrich vulnerabilities with exploit data
                vulns_list = enrich_vulnerability_data(vulns_list)
                vulns = vulns_list
            
            # Extract banners
            banners = get_device_banners(host_info=device)
            
            risk = Risk(device_id=device.get("id", device.get("ip_str", "unknown")), 
                      risk_score=0, vulnerabilities=vulns, ports=ports)
            risk_score = risk.calculate_risk_score()
            
            # Add OS, services and banners to risk model
            risk_data = risk.__repr__()
            risk_data["os"] = device.get("os", "Unknown")
            risk_data["services"] = services
            risk_data["banners"] = banners
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