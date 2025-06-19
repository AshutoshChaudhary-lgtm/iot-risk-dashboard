// IoT Risk Dashboard JavaScript

// Initialize Leaflet map
const map = L.map('map').setView([20, 0], 2); // World view
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Clear existing markers when scanning new data
let markersLayer = L.layerGroup().addTo(map);

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
  // Main scan button
  document.getElementById('scanBtn').addEventListener('click', function() {
    scanDevices();
  });

  // Event listeners for Advanced Shodan Actions
  // On-Demand Scan
  document.getElementById('requestScanBtn').addEventListener('click', requestOnDemandScan);
  // Domain Info
  document.getElementById('getDomainInfoBtn').addEventListener('click', fetchDomainInfo);
  // Network Alerts
  document.getElementById('createAlertBtn').addEventListener('click', createNetworkAlert);
  document.getElementById('listAlertsBtn').addEventListener('click', listNetworkAlerts);
  // Exposure Report
  document.getElementById('generateExposureReportBtn').addEventListener('click', generateExposureReport);

  // Allow pressing Enter in the input field to trigger the scan
  document.getElementById('ipRangeInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      scanDevices();
    }
  });
});

// Main Functions
function scanDevices() {
  const ipRange = document.getElementById('ipRangeInput').value;
  if (!ipRange) {
    showError("Please enter an IP address, range, or search query");
    return;
  }
  
  // Reset UI elements
  resetUI();
  
  // Show loading spinner
  document.getElementById('loadingSpinner').classList.remove('d-none');

  axios.get('/devices', { params: { ip_range: ipRange } })
    .then((response) => {
      // Remove loading spinner
      document.getElementById('loadingSpinner').classList.add('d-none');
      console.log("API response:", response.data);

      const devices = response.data.devices || [];
      const risks = response.data.risks || [];
      
      // Show warning if present
      if (response.data.warning) {
        const warningAlert = document.getElementById('warningAlert');
        warningAlert.classList.remove('d-none');
        warningAlert.innerText = response.data.warning;
      }

      // Update device count
      document.getElementById('deviceCount').textContent = devices.length + " devices";
      
      if (devices.length === 0) {
        // No results found
        showWarning("No devices found for your query.");
        return;
      }
      
      // Populate table
      populateDevicesTable(devices, risks);
      
      // Add markers to map
      addDeviceMarkers(devices);
    })
    .catch((error) => {
      // Remove loading spinner and show error message
      document.getElementById('loadingSpinner').classList.add('d-none');
      if (error.response && error.response.data && error.response.data.detail) {
        showError(`Error: ${error.response.data.detail}`);
      } else if (error.response && error.response.data && error.response.data.error) {
        showError(`Error: ${error.response.data.error}`);
      } else {
        showError('Error scanning devices. Check your connection and try again.');
      }
      console.error(error);
    });
}

function resetUI() {
  // Clear previous results
  document.getElementById('errorAlert').classList.add('d-none');
  document.getElementById('warningAlert').classList.add('d-none');
  document.getElementById('devicesTableBody').innerHTML = '';
  markersLayer.clearLayers();
}

function showError(message) {
  const errorAlert = document.getElementById('errorAlert');
  errorAlert.classList.remove('d-none');
  errorAlert.innerText = message;
}

function showWarning(message) {
  const warningAlert = document.getElementById('warningAlert');
  warningAlert.classList.remove('d-none');
  warningAlert.innerText = message;
}

function populateDevicesTable(devices, risks) {
  const tableBody = document.getElementById('devicesTableBody');
  tableBody.innerHTML = '';
  
  if (devices.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="5" class="text-center p-4">No devices found for this query.</td></tr>';
      return;
  }
  
  devices.forEach((device, index) => {
    // Find the risk data for this device
    const risk = risks[index] || {};
    const riskScore = risk.risk_score !== undefined && risk.risk_score !== null ? risk.risk_score : 'N/A';
    
    // Format ports as a comma-separated list
    const ports = Array.isArray(device.ports) && device.ports.length > 0 ? device.ports.join(', ') : 'N/A';
    
    // IMPROVED LOCATION HANDLING
    // First check location object, then check root level properties
    let countryName = 'N/A';
    let cityName = 'N/A';
    
    // Try to get location from both possible locations in the API response
    if (device.location) {
      countryName = device.location.country_name || countryName;
      cityName = device.location.city || cityName;
    } else { // Fallback if device.location itself is missing
       countryName = device.country_name || 'Unknown';
       cityName = device.city || 'Unknown';
    }
    
    // If still unknown, try root level (already partially handled, but good to be robust)
    if (countryName === 'Unknown' && device.country_name) countryName = device.country_name;
    if (cityName === 'Unknown' && device.city) cityName = device.city;

    // Create the main device row
    const row = document.createElement('tr');
    row.className = 'clickable-row';
    row.dataset.deviceId = index;
    
    row.innerHTML = `
      <td>${device.ip_str || 'N/A'}</td>
      <td><i class="bi bi-geo-alt-fill me-1"></i> ${countryName} / ${cityName}</td>
      <td>${device.os || 'Unknown'}</td>
      <td>${ports}</td>
      <td><span class="badge ${getRiskBadgeClass(riskScore)} p-2">${riskScore}</span></td>
    `;
    tableBody.appendChild(row);
    
    // Create the detail row
    const detailRow = document.createElement('tr');
    detailRow.className = 'detail-row';
    detailRow.id = `detail-${index}`;
    
    // Create detail content
    const hostnames = device.hostnames?.join(', ') || 'None';
    const domains = device.domains?.join(', ') || 'None';
    
    // Get vulnerabilities from device or risk data
    const vulns = device.vulns || {};
    const vulnList = Object.entries(vulns).map(([id, info]) => {
      return {
        id,
        ...info,
        severity: info.severity || 'unknown'
      };
    });
    
    // Format vulnerability display
    let vulnHtml = '<p>No known vulnerabilities</p>';
    if (vulnList.length > 0) {
      vulnHtml = '<div class="vulnerabilities-list">';
      vulnList.forEach(vuln => {
        const vulnClass = `vulnerability-${vuln.severity.toLowerCase()}`;
        vulnHtml += `
          <div class="vulnerability-item ${vulnClass}">
            <strong>${vuln.id}</strong> 
            <span class="badge bg-${getSeverityBadgeClass(vuln.severity)}">${vuln.severity}</span>
            <div>${vuln.summary || 'No details available'}</div>
          </div>
        `;
      });
      vulnHtml += '</div>';
    }
    
    // Services list
    const services = risk.services || [];
    const servicesHtml = services.length ? 
      services.map(s => `<span class="badge bg-info me-1 mb-1">${s}</span>`).join(' ') : 
      '<span class="text-muted">No detailed service information</span>';
    
    detailRow.innerHTML = `
      <td colspan="5">
        <div class="device-detail p-3">
          <div class="row">
            <div class="col-md-6">
              <h5 class="mb-3">Device Information</h5>
              <p><strong>Hostnames:</strong> ${hostnames}</p>
              <p><strong>Domains:</strong> ${domains}</p>
              <p class="mb-0"><strong>Services:</strong> ${servicesHtml}</p>
            </div>
            <div class="col-md-6">
              <h5 class="mb-3">Vulnerabilities</h5>
              ${vulnHtml}
            </div>
          </div>
        </div>
      </td>
    `;
    tableBody.appendChild(detailRow);
    
    // Add click event to show/hide details
    row.addEventListener('click', function() {
      const detailElement = document.getElementById(`detail-${this.dataset.deviceId}`);
      const allDetails = document.querySelectorAll('.detail-row');
      
      // Hide all other details
      allDetails.forEach(el => {
        if (el !== detailElement) {
          el.style.display = 'none';
        }
      });
      
      // Toggle current detail
      detailElement.style.display = detailElement.style.display === 'table-row' ? 'none' : 'table-row';
    });
  });
}

function getRiskBadgeClass(score) {
  if (score === 'N/A') return 'bg-secondary';
  if (score > 75) return 'bg-danger';
  if (score > 50) return 'bg-warning';
  if (score > 25) return 'bg-info';
  return 'bg-success';
}

function getSeverityBadgeClass(severity) {
  const sev = severity ? severity.toLowerCase() : 'unknown';
  if (sev === 'critical') return 'danger';
  if (sev === 'high') return 'warning text-dark'; // Ensure text is readable
  if (sev === 'medium') return 'info'; // Removed text-dark, info is light enough
  if (sev === 'low') return 'success';
  return 'secondary'; // Default for unknown
}

function addDeviceMarkers(devices) {
  markersLayer.clearLayers(); // Clear existing markers

  if (!devices || devices.length === 0) {
    console.log("No devices to add to map.");
    return;
  }

  const validDevices = devices.filter(device => {
      // Check root level first
      let lat = device.latitude;
      let lon = device.longitude;

      // If not at root, check inside device.location
      if ((lat === undefined || lon === undefined) && device.location) {
          lat = device.location.latitude;
          lon = device.location.longitude;
      }
      return lat !== undefined && lon !== undefined && lat !== null && lon !== null;
  });

  if (validDevices.length === 0) {
      console.log("No devices with valid coordinates to display on map.");
      return;
  }

  const bounds = L.latLngBounds();

  validDevices.forEach((device) => {
    // Determine latitude and longitude, checking both root and device.location
    let latitude = device.latitude;
    let longitude = device.longitude;
    if ((latitude === undefined || longitude === undefined) && device.location) {
        latitude = device.location.latitude;
        longitude = device.location.longitude;
    }

    // Create marker with a popup
    const marker = L.marker([latitude, longitude]);
    marker.bindPopup(`<b>${device.ip_str || 'N/A'}</b><br>Location: ${device.location ? (device.location.city || 'Unknown') : (device.city || 'Unknown')}, ${device.location ? (device.location.country_name || 'Unknown') : (device.country_name || 'Unknown')}`);
    markersLayer.addLayer(marker);
    bounds.extend([latitude, longitude]);
  });

  // Fit map to bounds if there are markers
  if (markersLayer.getLayers().length > 0) {
    map.fitBounds(bounds, { padding: [50, 50] }); // Add some padding
  } else {
    // If no markers were added (e.g. all devices lacked coordinates)
    // you might want to reset the map to a default view.
    map.setView([20, 0], 2); // Reset to world view
  }
}

// Advanced Shodan Actions Functions

// Function to handle on-demand scan request
async function requestOnDemandScan() {
  const ipAddress = document.getElementById('onDemandScanIpInput').value;
  const resultDiv = document.getElementById('onDemandScanResult');
  resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Requesting scan...';

  if (!ipAddress) {
    resultDiv.innerHTML = '<div class="alert alert-warning">Please enter an IP address.</div>';
    return;
  }

  try {
    const response = await axios.post('/scan', null, { params: { ip_address: ipAddress } });
    if (response.data.status === 'success') {
      resultDiv.innerHTML = `<div class="alert alert-success">${response.data.message}</div><pre>${JSON.stringify(response.data.details, null, 2)}</pre>`;
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${response.data.message}</div>`;
    }
  } catch (error) {
    console.error('On-demand scan error:', error);
    resultDiv.innerHTML = `<div class="alert alert-danger">Failed to request scan: ${error.message}</div>`;
  }
}

// Function to fetch domain information
async function fetchDomainInfo() {
  const domain = document.getElementById('domainInfoInput').value;
  const resultDiv = document.getElementById('domainInfoResult');
  resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Fetching domain info...';

  if (!domain) {
    resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a domain name.</div>';
    return;
  }

  try {
    const response = await axios.get(`/domain/${domain}`);
    if (response.data.status === 'success') {
      resultDiv.innerHTML = `<div class="alert alert-success">Domain: ${response.data.domain}</div><pre>${JSON.stringify(response.data.info, null, 2)}</pre>`;
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${response.data.message}</div>`;
    }
  } catch (error) {
    console.error('Domain info error:', error);
    resultDiv.innerHTML = `<div class="alert alert-danger">Failed to fetch domain info: ${error.message}</div>`;
  }
}

// Function to create a network alert
async function createNetworkAlert() {
  const name = document.getElementById('alertNameInput').value;
  const network = document.getElementById('alertNetworkInput').value;
  const triggers = document.getElementById('alertTriggersInput').value;
  const resultDiv = document.getElementById('createAlertResult');
  resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Creating alert...';

  if (!name || !network) {
    resultDiv.innerHTML = '<div class="alert alert-warning">Please enter alert name and network.</div>';
    return;
  }

  try {
    const params = new URLSearchParams();
    params.append('name', name);
    params.append('network', network);
    if (triggers) {
      params.append('triggers', triggers);
    }
    const response = await axios.post('/alerts', params);
    if (response.data.status === 'success') {
      resultDiv.innerHTML = `<div class="alert alert-success">${response.data.message}</div><pre>${JSON.stringify(response.data.alert, null, 2)}</pre>`;
      listNetworkAlerts(); // Refresh list
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${response.data.message}</div>`;
    }
  } catch (error) {
    console.error('Create alert error:', error);
    resultDiv.innerHTML = `<div class="alert alert-danger">Failed to create alert: ${error.message}</div>`;
  }
}

// Function to list network alerts
async function listNetworkAlerts() {
  const tableBody = document.getElementById('alertsTableBody');
  const resultDiv = document.getElementById('listAlertsResult'); // For general messages
  tableBody.innerHTML = '<tr><td colspan="5"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Loading alerts...</td></tr>';

  try {
    const response = await axios.get('/alerts');
    if (response.data.status === 'success' && response.data.alerts) {
      tableBody.innerHTML = ''; // Clear loading message
      if (response.data.alerts.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No network alerts found.</td></tr>';
        return;
      }
      response.data.alerts.forEach(alert => {
        const row = tableBody.insertRow();
        row.innerHTML = `
          <td>${alert.id}</td>
          <td>${alert.name}</td>
          <td>${alert.filters.ip ? alert.filters.ip.join(', ') : 'N/A'}</td>
          <td>${alert.triggers ? Object.keys(alert.triggers).join(', ') : 'N/A'}</td>
          <td>${new Date(alert.created).toLocaleDateString()}</td>
        `;
      });
    } else {
      tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error listing alerts.</td></tr>';
      resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${response.data.message || 'Could not load alerts.'}</div>`;
    }
  } catch (error) {
    console.error('List alerts error:', error);
    tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Failed to load alerts.</td></tr>';
    resultDiv.innerHTML = `<div class="alert alert-danger">Failed to list alerts: ${error.message}</div>`;
  }
}

// Function to generate exposure report
async function generateExposureReport() {
  const domain = document.getElementById('exposureReportDomainInput').value;
  const resultDiv = document.getElementById('exposureReportResult');
  resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Generating report...';

  if (!domain) {
    resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a domain name.</div>';
    return;
  }

  try {
    const response = await axios.get(`/exposure/${domain}`);
    if (response.data.status === 'success') {
      resultDiv.innerHTML = `<div class="alert alert-success">Report for ${response.data.domain}</div><pre>${JSON.stringify(response.data.report, null, 2)}</pre>`;
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${response.data.message}</div>`;
    }
  } catch (error) {
    console.error('Exposure report error:', error);
    resultDiv.innerHTML = `<div class="alert alert-danger">Failed to generate report: ${error.message}</div>`;
  }
}
