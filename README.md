# IoT Risk Dashboard

## Overview
The IoT Risk Dashboard is a web-based application that helps security professionals identify and assess risks associated with internet-connected devices. Built with Python and FastAPI, this tool leverages the Shodan API to scan and analyze IoT devices across specified IP ranges or search criteria. The dashboard provides real-time risk assessments, geographical mapping, and detailed vulnerability information in an intuitive interface.

## Key Features
- **Device Discovery**: Search for IoT devices by IP address, range, or custom Shodan query
- **Interactive Map**: Visualize global device distribution with an interactive Leaflet.js map
- **Risk Assessment**: Automatically calculate risk scores based on open ports, services, and vulnerabilities
- **Detailed Device Information**: View comprehensive device details including OS, hostnames, domains, and services
- **Vulnerability Analysis**: Identify and categorize security vulnerabilities with severity ratings
- **Alert System**: Receive email notifications for high-risk devices
- **Responsive Design**: Mobile-friendly Bootstrap interface for monitoring on any device


## Technology Stack
- **Backend**: Python, FastAPI
- **Frontend**: HTML, JavaScript, Bootstrap 5
- **Mapping**: Leaflet.js
- **API Integration**: Shodan API
- **HTTP Client**: Axios

## Project Structure
```
iot-risk-dashboard
├── src
│   ├── app.py               # Entry point for the FastAPI application
│   ├── shodan_client.py     # Interacts with the Shodan API
│   ├── routes
│   │   └── dashboard.py     # API routes for the dashboard
│   ├── models
│   │   └── risk.py          # Risk model definition
│   └── utils
│       └── geo_mapper.py    # Utility functions for geographical mapping
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd iot-risk-dashboard
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your Shodan API key:
- Create a `key.env` file in the `src` directory with:
  ```
  SHODAN_API_KEY=your_api_key_here
  ALERT_EMAIL=your_email@example.com
  ```

4. Start the application:
   ```
   uvicorn src.app:app --reload
   ```


5. Access the dashboard at http://localhost:8000/dashboard

## Usage Guide
1. **Search for Devices**:
- Enter an IP address (e.g., `8.8.8.8`), IP range, or Shodan search query (e.g., `port:22 country:US` or `webcam`)
- Click the "Scan" button or press Enter

2. **Interpret Results**:
- View device locations on the interactive map
- Browse the devices table showing IPs, locations, OS, ports, and risk scores
- Click on any device row to view detailed information including vulnerabilities

3. **Risk Assessment**:
- Risk scores are calculated based on:
  - Presence and severity of known vulnerabilities
  - Number and type of open ports (high-risk ports include 21, 22, 23, 2323, and 8080)
  - Services running on the device

## API Endpoints
- `GET /dashboard` - View the dashboard UI
- `GET /devices?ip_range={query}` - Search for devices with the specified query

## License
This project is licensed under the MIT License.