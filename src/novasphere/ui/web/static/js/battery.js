// Battery Monitor JavaScript
let batteryUpdateInterval;
let isAutoRefreshEnabled = false;

// Initialize battery monitor
document.addEventListener('DOMContentLoaded', function() {
    refreshBatteryInfo();
    loadSettings();
});

// Refresh battery information
async function refreshBatteryInfo() {
    try {
        const response = await fetch('/api/battery/info');
        if (response.ok) {
            const data = await response.json();
            updateBatteryDisplay(data);
            updateChargingInfo(data);
            checkBatteryAlerts(data);
        } else {
            showError('Failed to fetch battery information');
        }
    } catch (error) {
        console.error('Error fetching battery info:', error);
        showError('Error connecting to battery service');
    }
}

// Update battery display
function updateBatteryDisplay(data) {
    // Update percentage
    const percentageElement = document.getElementById('battery-percentage');
    if (percentageElement) {
        percentageElement.textContent = `${data.battery_percent}%`;
    }
    
    // Update status
    const statusElement = document.getElementById('battery-status');
    if (statusElement) {
        if (data.power_plugged) {
            statusElement.textContent = 'Charging';
            statusElement.className = 'text-success';
        } else {
            statusElement.textContent = 'On Battery';
            statusElement.className = 'text-warning';
        }
    }
    
    // Update battery icon
    const iconElement = document.getElementById('battery-icon');
    if (iconElement) {
        iconElement.className = getBatteryIconClass(data.battery_percent, data.power_plugged);
    }
    
    // Update progress bar
    const progressElement = document.getElementById('battery-progress');
    if (progressElement) {
        progressElement.style.width = `${data.battery_percent}%`;
        progressElement.setAttribute('aria-valuenow', data.battery_percent);
        progressElement.textContent = `${data.battery_percent}%`;
        
        // Update progress bar color
        progressElement.className = 'progress-bar ' + getProgressBarClass(data.battery_percent);
    }
    
    // Update charging status
    const chargingStatusElement = document.getElementById('charging-status');
    if (chargingStatusElement) {
        chargingStatusElement.textContent = data.power_plugged ? 'Charging' : 'Not Charging';
    }
    
    // Update power plugged status
    const powerPluggedElement = document.getElementById('power-plugged');
    if (powerPluggedElement) {
        powerPluggedElement.textContent = data.power_plugged ? 'Yes' : 'No';
    }
}

// Update charging information
function updateChargingInfo(data) {
    const chargingInfoDiv = document.getElementById('charging-info');
    
    if (data.power_plugged) {
        chargingInfoDiv.style.display = 'block';
        
        // Calculate charging rate (simplified)
        const chargerWattage = parseFloat(document.getElementById('charger-wattage').value) || 65;
        const batteryCapacity = parseFloat(document.getElementById('battery-capacity').value) || 50000;
        
        const remainingCapacity = (100 - data.battery_percent) / 100 * batteryCapacity;
        const chargingRate = chargerWattage * 0.85; // Assume 85% efficiency
        const timeToFull = remainingCapacity / chargingRate;
        
        document.getElementById('charging-rate').textContent = `${chargingRate.toFixed(1)} W`;
        document.getElementById('time-to-full').textContent = formatTime(timeToFull);
        document.getElementById('estimated-time').textContent = new Date(Date.now() + timeToFull * 3600000).toLocaleTimeString();
    } else {
        chargingInfoDiv.style.display = 'none';
    }
}

// Check battery alerts
function checkBatteryAlerts(data) {
    const alertsDiv = document.getElementById('battery-alerts');
    let alerts = [];
    
    if (data.battery_percent <= 10) {
        alerts.push({
            type: 'danger',
            message: 'Critical battery level! Connect charger immediately.'
        });
    } else if (data.battery_percent <= 20) {
        alerts.push({
            type: 'warning',
            message: 'Low battery level. Consider charging soon.'
        });
    }
    
    if (!data.power_plugged && data.battery_percent <= 5) {
        alerts.push({
            type: 'danger',
            message: 'System may shut down soon due to low battery.'
        });
    }
    
    if (alerts.length > 0) {
        alertsDiv.innerHTML = alerts.map(alert => 
            `<div class="alert alert-${alert.type} alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle"></i> ${alert.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>`
        ).join('');
    } else {
        alertsDiv.innerHTML = '<p class="text-muted">No alerts at this time.</p>';
    }
}

// Get battery icon class
function getBatteryIconClass(level, charging) {
    let iconClass = 'fas ';
    
    if (level >= 90) iconClass += 'fa-battery-full';
    else if (level >= 60) iconClass += 'fa-battery-three-quarters';
    else if (level >= 30) iconClass += 'fa-battery-half';
    else if (level >= 10) iconClass += 'fa-battery-quarter';
    else iconClass += 'fa-battery-empty';
    
    iconClass += ' fa-4x';
    
    if (charging) {
        iconClass += ' text-success battery-charging';
    } else {
        if (level < 20) iconClass += ' text-danger';
        else if (level < 50) iconClass += ' text-warning';
        else iconClass += ' text-success';
    }
    
    return iconClass;
}

// Get progress bar class
function getProgressBarClass(level) {
    if (level < 20) return 'bg-danger';
    else if (level < 50) return 'bg-warning';
    else return 'bg-success';
}

// Toggle auto refresh
function toggleAutoRefresh() {
    isAutoRefreshEnabled = !isAutoRefreshEnabled;
    const button = document.querySelector('button[onclick="toggleAutoRefresh()"]');
    
    if (isAutoRefreshEnabled) {
        const interval = parseInt(document.getElementById('update-interval').value) * 1000;
        batteryUpdateInterval = setInterval(refreshBatteryInfo, interval);
        button.innerHTML = '<i class="fas fa-pause"></i> Stop Auto Refresh';
        button.className = 'btn btn-warning btn-sm';
    } else {
        if (batteryUpdateInterval) {
            clearInterval(batteryUpdateInterval);
        }
        button.innerHTML = '<i class="fas fa-play"></i> Start Auto Refresh';
        button.className = 'btn btn-primary btn-sm';
    }
}

// Load settings from localStorage
function loadSettings() {
    const chargerWattage = localStorage.getItem('battery-charger-wattage');
    if (chargerWattage) {
        document.getElementById('charger-wattage').value = chargerWattage;
    }
    
    const batteryCapacity = localStorage.getItem('battery-capacity');
    if (batteryCapacity) {
        document.getElementById('battery-capacity').value = batteryCapacity;
    }
    
    const updateInterval = localStorage.getItem('battery-update-interval');
    if (updateInterval) {
        document.getElementById('update-interval').value = updateInterval;
    }
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem('battery-charger-wattage', document.getElementById('charger-wattage').value);
    localStorage.setItem('battery-capacity', document.getElementById('battery-capacity').value);
    localStorage.setItem('battery-update-interval', document.getElementById('update-interval').value);
}

// Format time in hours
function formatTime(hours) {
    if (hours < 1) {
        return `${Math.round(hours * 60)} minutes`;
    } else if (hours < 24) {
        const h = Math.floor(hours);
        const m = Math.round((hours - h) * 60);
        return `${h}h ${m}m`;
    } else {
        return '> 24 hours';
    }
}

// Show error message
function showError(message) {
    const alertsDiv = document.getElementById('battery-alerts');
    alertsDiv.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

// Save settings when inputs change
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['charger-wattage', 'battery-capacity', 'update-interval'];
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', saveSettings);
        }
    });
});