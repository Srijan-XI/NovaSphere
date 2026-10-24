// Dashboard JavaScript
let systemInfoInterval;
let isRealTimeEnabled = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadSystemInfo();
    setupToolNavigation();
    
    // Start real-time updates if enabled
    const realTimeToggle = localStorage.getItem('realTimeUpdates');
    if (realTimeToggle === 'true') {
        toggleRealTimeUpdates();
    }
});

// Load system information
async function loadSystemInfo() {
    try {
        // Load battery info
        const batteryResponse = await fetch('/api/battery/info');
        if (batteryResponse.ok) {
            const batteryData = await batteryResponse.json();
            updateBatteryInfo(batteryData);
        } else {
            setUnavailable('battery-level', 'Unavailable');
            setUnavailable('battery-status', 'Battery service unavailable');
        }
        
        // Load system metrics
        const monitoringResponse = await fetch('/api/monitoring/metrics');
        if (monitoringResponse.ok) {
            const monitoringData = await monitoringResponse.json();
            updateSystemMetrics(monitoringData);
        } else {
            ['cpu-usage', 'memory-usage', 'disk-usage', 'cpu-status', 'memory-status', 'disk-status'].forEach((id) => setUnavailable(id, 'Unavailable'));
        }
        
        
    } catch (error) {
        console.error('Error loading system info:', error);
        ['cpu-usage', 'memory-usage', 'disk-usage', 'cpu-status', 'memory-status', 'disk-status', 'battery-level', 'battery-status'].forEach((id) => setUnavailable(id, 'Unavailable'));
    }
}

function setUnavailable(id, text) {
    const element = document.getElementById(id);
    if (element) element.textContent = text;
}

// Update battery information
function updateBatteryInfo(data) {
    const batteryLevel = document.getElementById('battery-level');
    const batteryStatus = document.getElementById('battery-status');
    
    if (batteryLevel && data.battery_percent !== undefined) {
        batteryLevel.textContent = `${data.battery_percent}%`;
        
        // Update battery icon based on level
        const batteryIcon = document.querySelector('.battery-info .fa-battery-half');
        if (batteryIcon) {
            batteryIcon.className = getBatteryIconClass(data.battery_percent, data.power_plugged);
        }
    }
    
    if (batteryStatus && data.power_plugged !== undefined) {
        batteryStatus.textContent = data.power_plugged ? 'Charging' : 'On Battery';
        batteryStatus.className = data.power_plugged ? 'text-success' : 'text-warning';
    }
}

// Update system metrics
function updateSystemMetrics(data) {
    // CPU Usage
    const cpuUsage = document.getElementById('cpu-usage');
    const cpuValue = Number(data.cpu_percent || 0);
    if (cpuUsage) {
        cpuUsage.textContent = `${cpuValue.toFixed(1)}%`;
    }
    
    // Memory Usage
    const memoryUsage = document.getElementById('memory-usage');
    const memoryValue = Number(data.memory_percent || 0);
    if (memoryUsage) {
        memoryUsage.textContent = `${memoryValue.toFixed(1)}%`;
    }
    
    // Disk Usage
    const diskUsage = document.getElementById('disk-usage');
    const diskValue = Number(data.disk_percent || 0);
    if (diskUsage) {
        diskUsage.textContent = `${diskValue.toFixed(1)}%`;
    }

    const cpuStatus = document.getElementById('cpu-status');
    if (cpuStatus) {
        cpuStatus.textContent = `${cpuValue.toFixed(1)}%`;
        cpuStatus.className = `badge ${cpuValue < 80 ? 'bg-success' : 'bg-warning'}`;
    }
    const memoryStatus = document.getElementById('memory-status');
    if (memoryStatus) {
        memoryStatus.textContent = `${memoryValue.toFixed(1)}%`;
        memoryStatus.className = `badge ${memoryValue < 80 ? 'bg-success' : 'bg-warning'}`;
    }
    const diskStatus = document.getElementById('disk-status');
    if (diskStatus) {
        diskStatus.textContent = `${diskValue.toFixed(1)}%`;
        diskStatus.className = `badge ${diskValue < 90 ? 'bg-success' : 'bg-warning'}`;
    }
    
    // Network Status
    const networkStatus = document.getElementById('network-status');
    if (networkStatus) {
        const isConnected = data.network_connected !== false;
        networkStatus.innerHTML = `
            <span class="status-indicator ${isConnected ? 'status-online' : 'status-offline'}"></span>
            ${isConnected ? 'Connected' : 'Disconnected'}
        `;
    }
}

// Get battery icon class based on level and charging status
function getBatteryIconClass(level, charging) {
    let iconClass = 'fas ';
    
    if (level >= 90) iconClass += 'fa-battery-full';
    else if (level >= 60) iconClass += 'fa-battery-three-quarters';
    else if (level >= 30) iconClass += 'fa-battery-half';
    else if (level >= 10) iconClass += 'fa-battery-quarter';
    else iconClass += 'fa-battery-empty';
    
    if (charging) {
        iconClass += ' text-success charging-indicator';
    } else {
        if (level < 20) iconClass += ' text-danger';
        else if (level < 50) iconClass += ' text-warning';
        else iconClass += ' text-success';
    }
    
    return iconClass;
}

// Setup tool navigation
function setupToolNavigation() {
    const toolCards = document.querySelectorAll('.tool-card');
    toolCards.forEach(card => {
        card.addEventListener('click', function() {
            const href = this.getAttribute('data-href');
            if (href) {
                window.location.href = href;
            }
        });
    });
}

// Toggle real-time updates
function toggleRealTimeUpdates() {
    isRealTimeEnabled = !isRealTimeEnabled;
    const toggleBtn = document.getElementById('realtime-toggle');
    
    if (isRealTimeEnabled) {
        systemInfoInterval = setInterval(loadSystemInfo, 5000);
        toggleBtn.innerHTML = '<i class="fas fa-pause"></i> Stop Updates';
        toggleBtn.className = 'btn btn-warning btn-sm';
        localStorage.setItem('realTimeUpdates', 'true');
    } else {
        if (systemInfoInterval) {
            clearInterval(systemInfoInterval);
        }
        toggleBtn.innerHTML = '<i class="fas fa-play"></i> Start Updates';
        toggleBtn.className = 'btn btn-success btn-sm';
        localStorage.setItem('realTimeUpdates', 'false');
    }
}

// Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format uptime
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) {
        return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m`;
    }
}
