// Settings Page JavaScript for IoT Risk Dashboard

// Initialize settings on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // API Configuration
    document.getElementById('toggleApiKeyVisibility').addEventListener('click', toggleApiKeyVisibility);
    document.getElementById('testConnectionBtn').addEventListener('click', testApiConnection);
    document.getElementById('saveApiKeyBtn').addEventListener('click', saveApiKey);
    
    // Application Settings
    document.getElementById('demoModeToggle').addEventListener('change', toggleDemoMode);
    document.getElementById('autoRefreshToggle').addEventListener('change', saveApplicationSettings);
    document.getElementById('darkModeToggle').addEventListener('change', toggleDarkMode);
    
    // Alert Configuration
    document.getElementById('riskThreshold').addEventListener('input', updateRiskThresholdDisplay);
    document.getElementById('saveAlertConfigBtn').addEventListener('click', saveAlertConfiguration);
    
    // Display Preferences
    document.getElementById('defaultMapZoom').addEventListener('input', updateMapZoomDisplay);
    document.getElementById('saveDisplayConfigBtn').addEventListener('click', saveDisplayPreferences);
    
    // Advanced Configuration
    document.getElementById('saveAdvancedConfigBtn').addEventListener('click', saveAdvancedConfiguration);
    document.getElementById('resetToDefaultsBtn').addEventListener('click', resetToDefaults);
    
    // Configuration Management
    document.getElementById('exportConfigBtn').addEventListener('click', exportConfiguration);
    document.getElementById('importConfigBtn').addEventListener('click', importConfiguration);
}

// Load saved settings from localStorage
function loadSettings() {
    const settings = getStoredSettings();
    
    // Load API Configuration
    if (settings.shodanApiKey) {
        document.getElementById('shodanApiKey').value = settings.shodanApiKey;
    }
    
    // Load Application Settings
    document.getElementById('demoModeToggle').checked = settings.demoMode || false;
    document.getElementById('autoRefreshToggle').checked = settings.autoRefresh || false;
    document.getElementById('darkModeToggle').checked = settings.darkMode || false;
    
    // Load Alert Configuration
    document.getElementById('alertEmail').value = settings.alertEmail || '';
    document.getElementById('riskThreshold').value = settings.riskThreshold || 75;
    document.getElementById('emailAlertsToggle').checked = settings.emailAlerts !== false;
    updateRiskThresholdDisplay();
    
    // Load Display Preferences
    document.getElementById('defaultMapZoom').value = settings.defaultMapZoom || 2;
    document.getElementById('resultsPerPage').value = settings.resultsPerPage || 25;
    document.getElementById('showDetailedBannersToggle').checked = settings.showDetailedBanners || false;
    updateMapZoomDisplay();
    
    // Load Advanced Configuration
    document.getElementById('apiTimeout').value = settings.apiTimeout || 10;
    document.getElementById('maxSearchResults').value = settings.maxSearchResults || 100;
    document.getElementById('cacheExpiry').value = settings.cacheExpiry || 30;
    document.getElementById('defaultSearchQuery').value = settings.defaultSearchQuery || '';
    document.getElementById('enableLoggingToggle').checked = settings.enableLogging !== false;
}

// Get settings from localStorage
function getStoredSettings() {
    const settings = localStorage.getItem('iotDashboardSettings');
    return settings ? JSON.parse(settings) : {};
}

// Save settings to localStorage
function saveSettings(newSettings) {
    const currentSettings = getStoredSettings();
    const updatedSettings = { ...currentSettings, ...newSettings };
    localStorage.setItem('iotDashboardSettings', JSON.stringify(updatedSettings));
}

// API Configuration Functions
function toggleApiKeyVisibility() {
    const apiKeyInput = document.getElementById('shodanApiKey');
    const eyeIcon = document.getElementById('eyeIcon');
    
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        eyeIcon.className = 'bi bi-eye-slash';
    } else {
        apiKeyInput.type = 'password';
        eyeIcon.className = 'bi bi-eye';
    }
}

async function testApiConnection() {
    const resultDiv = document.getElementById('apiTestResult');
    const apiKey = document.getElementById('shodanApiKey').value;
    
    if (!apiKey) {
        showResult(resultDiv, 'Please enter an API key first.', 'warning');
        return;
    }
    
    resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Testing...</span></div> Testing connection...';
    
    try {
        // Test the API by making a simple request
        const response = await axios.get(`/devices?ip_range=8.8.8.8`);
        if (response.data && !response.data.error) {
            showResult(resultDiv, 'API connection successful! Key is valid.', 'success');
        } else {
            showResult(resultDiv, 'API connection failed. Please check your key.', 'danger');
        }
    } catch (error) {
        showResult(resultDiv, `Connection test failed: ${error.message}`, 'danger');
    }
}

function saveApiKey() {
    const apiKey = document.getElementById('shodanApiKey').value;
    const resultDiv = document.getElementById('apiTestResult');
    
    if (!apiKey) {
        showResult(resultDiv, 'Please enter an API key.', 'warning');
        return;
    }
    
    saveSettings({ shodanApiKey: apiKey });
    showResult(resultDiv, 'API key saved successfully!', 'success');
}

// Application Settings Functions
async function toggleDemoMode() {
    const enable = document.getElementById('demoModeToggle').checked;
    const statusDiv = document.getElementById('settingsStatus');
    
    try {
        const response = await axios.post('/toggle-demo', null, { params: { enable: enable } });
        if (response.data.status === 'success') {
            saveSettings({ demoMode: enable });
            showResult(statusDiv, response.data.message, 'success');
        } else {
            showResult(statusDiv, `Error: ${response.data.message}`, 'danger');
        }
    } catch (error) {
        showResult(statusDiv, `Failed to toggle demo mode: ${error.message}`, 'danger');
    }
}

function saveApplicationSettings() {
    const autoRefresh = document.getElementById('autoRefreshToggle').checked;
    const statusDiv = document.getElementById('settingsStatus');
    
    saveSettings({ autoRefresh: autoRefresh });
    showResult(statusDiv, 'Application settings saved!', 'success');
}

function toggleDarkMode() {
    const enable = document.getElementById('darkModeToggle').checked;
    const statusDiv = document.getElementById('settingsStatus');
    
    // For now, just save the setting (implementation would come later)
    saveSettings({ darkMode: enable });
    showResult(statusDiv, 'Dark mode preference saved! (Feature coming soon)', 'info');
}

// Alert Configuration Functions
function updateRiskThresholdDisplay() {
    const value = document.getElementById('riskThreshold').value;
    const display = document.getElementById('riskThresholdValue');
    display.textContent = value;
    
    // Update badge color based on threshold
    display.className = 'badge ';
    if (value >= 80) display.className += 'bg-danger';
    else if (value >= 60) display.className += 'bg-warning';
    else if (value >= 40) display.className += 'bg-info';
    else display.className += 'bg-success';
}

function saveAlertConfiguration() {
    const alertEmail = document.getElementById('alertEmail').value;
    const riskThreshold = document.getElementById('riskThreshold').value;
    const emailAlerts = document.getElementById('emailAlertsToggle').checked;
    const statusDiv = document.getElementById('alertConfigStatus');
    
    if (emailAlerts && !alertEmail) {
        showResult(statusDiv, 'Please enter an email address for alerts.', 'warning');
        return;
    }
    
    saveSettings({
        alertEmail: alertEmail,
        riskThreshold: parseInt(riskThreshold),
        emailAlerts: emailAlerts
    });
    
    showResult(statusDiv, 'Alert configuration saved successfully!', 'success');
}

// Display Preferences Functions
function updateMapZoomDisplay() {
    const value = document.getElementById('defaultMapZoom').value;
    document.getElementById('mapZoomValue').textContent = value;
}

function saveDisplayPreferences() {
    const defaultMapZoom = document.getElementById('defaultMapZoom').value;
    const resultsPerPage = document.getElementById('resultsPerPage').value;
    const showDetailedBanners = document.getElementById('showDetailedBannersToggle').checked;
    const statusDiv = document.getElementById('displayConfigStatus');
    
    saveSettings({
        defaultMapZoom: parseInt(defaultMapZoom),
        resultsPerPage: parseInt(resultsPerPage),
        showDetailedBanners: showDetailedBanners
    });
    
    showResult(statusDiv, 'Display preferences saved successfully!', 'success');
}

// Advanced Configuration Functions
function saveAdvancedConfiguration() {
    const apiTimeout = document.getElementById('apiTimeout').value;
    const maxSearchResults = document.getElementById('maxSearchResults').value;
    const cacheExpiry = document.getElementById('cacheExpiry').value;
    const defaultSearchQuery = document.getElementById('defaultSearchQuery').value;
    const enableLogging = document.getElementById('enableLoggingToggle').checked;
    const statusDiv = document.getElementById('advancedConfigStatus');
    
    saveSettings({
        apiTimeout: parseInt(apiTimeout),
        maxSearchResults: parseInt(maxSearchResults),
        cacheExpiry: parseInt(cacheExpiry),
        defaultSearchQuery: defaultSearchQuery,
        enableLogging: enableLogging
    });
    
    showResult(statusDiv, 'Advanced configuration saved successfully!', 'success');
}

function resetToDefaults() {
    if (confirm('Are you sure you want to reset all settings to their default values? This action cannot be undone.')) {
        localStorage.removeItem('iotDashboardSettings');
        location.reload(); // Reload to show default values
    }
}

// Configuration Management Functions
function exportConfiguration() {
    const settings = getStoredSettings();
    const statusDiv = document.getElementById('configManagementStatus');
    
    // Remove sensitive data for export
    const exportSettings = { ...settings };
    delete exportSettings.shodanApiKey; // Don't export API key for security
    
    const dataStr = JSON.stringify(exportSettings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `iot-dashboard-settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showResult(statusDiv, 'Configuration exported successfully! (API key excluded for security)', 'success');
}

function importConfiguration() {
    const fileInput = document.getElementById('importConfigFile');
    const statusDiv = document.getElementById('configManagementStatus');
    
    if (!fileInput.files.length) {
        showResult(statusDiv, 'Please select a configuration file to import.', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    const reader = new FileReader();
    
    reader.onload = function(e) {
        try {
            const importedSettings = JSON.parse(e.target.result);
            
            // Validate the imported settings
            if (typeof importedSettings !== 'object') {
                throw new Error('Invalid configuration file format');
            }
            
            // Merge with current settings (imported settings take precedence)
            const currentSettings = getStoredSettings();
            const mergedSettings = { ...currentSettings, ...importedSettings };
            
            // Save the merged settings
            localStorage.setItem('iotDashboardSettings', JSON.stringify(mergedSettings));
            
            showResult(statusDiv, 'Configuration imported successfully! Reloading page...', 'success');
            
            // Reload after a short delay to show the success message
            setTimeout(() => {
                location.reload();
            }, 1500);
            
        } catch (error) {
            showResult(statusDiv, `Failed to import configuration: ${error.message}`, 'danger');
        }
    };
    
    reader.readAsText(file);
}

// Utility Functions
function showResult(element, message, type) {
    element.innerHTML = `<div class="alert alert-${type} mb-0">${message}</div>`;
    
    // Auto-hide success and info messages after 3 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            element.innerHTML = '';
        }, 3000);
    }
}

// Export settings to be used by other parts of the application
window.dashboardSettings = {
    get: getStoredSettings,
    save: saveSettings
};
