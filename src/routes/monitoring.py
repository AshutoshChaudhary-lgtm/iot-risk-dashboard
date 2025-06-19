from fastapi import APIRouter, HTTPException
from src.utils.network_monitor import NetworkMonitor
import os
import traceback

router = APIRouter()

@router.get("/network-alerts")
async def list_network_alerts():
    """List all network alerts configured in Shodan"""
    try:
        monitor = NetworkMonitor()
        alerts = monitor.list_alerts()
        return {"alerts": alerts}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listing network alerts: {str(e)}")

@router.post("/network-alerts")
async def create_network_alert(name: str, ip_range: str):
    """Create a new network alert for an IP range"""
    try:
        monitor = NetworkMonitor()
        alert_id = monitor.create_network_alert(name, ip_range)
        
        if alert_id:
            return {"alert_id": alert_id, "message": f"Alert '{name}' created successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to create alert")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating network alert: {str(e)}")

@router.get("/network-alerts/{alert_id}")
async def get_alert_details(alert_id: str):
    """Get details about a specific network alert"""
    try:
        monitor = NetworkMonitor()
        details = monitor.get_alert_details(alert_id)
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
            
        # Get notifications for this alert
        notifications = monitor.get_triggered_notifications(alert_id)
        
        return {
            "alert": details,
            "notifications": notifications
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting alert details: {str(e)}")
