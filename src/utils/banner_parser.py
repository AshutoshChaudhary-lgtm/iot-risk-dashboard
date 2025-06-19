"""
Add a method to fetch and display device banners from Shodan API
"""

def get_device_banners(host_info):
    """Extract banner information from device data"""
    banners = []
    
    # Extract banners from data modules
    if "data" in host_info:
        for service in host_info["data"]:
            # Get the banner data
            banner = service.get("data", "")
            if banner:
                # Create a banner object with relevant info
                banner_obj = {
                    "port": service.get("port", "unknown"),
                    "protocol": service.get("transport", "unknown"),
                    "service": service.get("_shodan", {}).get("module", "unknown"),
                    "banner": banner[:500],  # Limit size for display
                    "timestamp": service.get("timestamp", "unknown")
                }
                banners.append(banner_obj)
    
    return banners
