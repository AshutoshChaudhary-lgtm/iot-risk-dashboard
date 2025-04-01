def map_devices(devices):
    geo_data = []
    for device in devices:
        location = {
            "device_id": device.get("id"),
            "ip": device.get("ip_str"),
            "latitude": device.get("location", {}).get("latitude"),
            "longitude": device.get("location", {}).get("longitude"),
            "country": device.get("location", {}).get("country_name"),
            "city": device.get("location", {}).get("city"),
        }
        geo_data.append(location)
    return geo_data