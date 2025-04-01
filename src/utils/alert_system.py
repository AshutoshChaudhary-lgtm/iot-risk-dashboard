# src/utils/alert_system.py
import smtplib
from email.message import EmailMessage

def send_email_alert(recipient, device_info, risk_score):
    msg = EmailMessage()
    msg.set_content(f"Critical device found: {device_info['ip_str']} with risk score {risk_score}")
    msg['Subject'] = f"IoT Risk Alert: Critical Device Detected"
    msg['From'] = "dashboard@example.com"
    msg['To'] = recipient
    
    # Configure your SMTP server settings
    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login("username", "password")
    server.send_message(msg)
    server.quit()