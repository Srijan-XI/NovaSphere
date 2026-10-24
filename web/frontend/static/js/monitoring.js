// System Monitoring JavaScript
let monitoringInterval;
let cpuMemoryChart;
let isMonitoringActive = false;

// Initialize monitoring
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadSystemMetrics();
    startMonitoring();
});

// Initialize charts
function initializeCharts() {
    const ctx = document.getElementById('cpuMemoryChart').getContext('2d');
    
    cpuMemoryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'CPU %',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }, {
                label: 'Memory %',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Load system metrics
async function loadSystemMetrics() {
    try {
        const response = await fetch('/api/monitoring/metrics');
        if (response.ok) {
            const data = await response.json();
            updateMetricsDisplay(data);
            updateCharts(data);
            updateSystemInfo(data);
            updateProcessTable(data);
        } else {
            showError('Failed to fetch system metrics');
        }
    } catch (error) {
        console.error('Error loading system metrics:', error);
        showError('Error connecting to monitoring service');
    }
}

// Update metrics display
function updateMetricsDisplay(data) {
    // CPU Usage
    const cpuUsage = document.getElementById('cpu-usage');
    if (cpuUsage && data.cpu_percent !== undefined) {
        cpuUsage.textContent = `${data.cpu_percent.toFixed(1)}%`;
    }
    
    // Memory Usage
    const memoryUsage = document.getElementById('memory-usage');
    if (memoryUsage && data.memory_percent !== undefined) {
        memoryUsage.textContent = `${data.memory_percent.toFixed(1)}%`;
    }
    
    // Disk Usage
    const diskUsage = document.getElementById('disk-usage');
    if (diskUsage && data.disk_percent !== undefined) {
        diskUsage.textContent = `${data.disk_percent.toFixed(1)}%`;
    }
    
    // Network Status
    const networkStatus = document.getElementById('network-status');
    if (networkStatus) {
        const isConnected = data.network_connected !== false;
        networkStatus.textContent = isConnected ? 'Connected' : 'Disconnected';
    }
}

// Update charts
function updateCharts(data) {
    if (!cpuMemoryChart || !data.cpu_percent || !data.memory_percent) return;
    
    const now = new Date().toLocaleTimeString();
    
    // Add new data point
    cpuMemoryChart.data.labels.push(now);
    cpuMemoryChart.data.datasets[0].data.push(data.cpu_percent);
    cpuMemoryChart.data.datasets[1].data.push(data.memory_percent);
    
    // Keep only last 20 data points
    if (cpuMemoryChart.data.labels.length > 20) {
        cpuMemoryChart.data.labels.shift();
        cpuMemoryChart.data.datasets[0].data.shift();
        cpuMemoryChart.data.datasets[1].data.shift();
    }
    
    cpuMemoryChart.update('none');
}

// Update system information
function updateSystemInfo(data) {
    // CPU Info
    const cpuInfo = document.getElementById('cpu-info');
    if (cpuInfo && data.cpu_info) {
        cpuInfo.innerHTML = `
            <div class="row">
                <div class="col-sm-4"><strong>Model:</strong></div>
                <div class="col-sm-8">${data.cpu_info.brand || 'Unknown'}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Cores:</strong></div>
                <div class="col-sm-8">${data.cpu_info.cores || 'Unknown'}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Frequency:</strong></div>
                <div class="col-sm-8">${data.cpu_info.frequency ? data.cpu_info.frequency.toFixed(2) + ' GHz' : 'Unknown'}</div>
            </div>
        `;
    }
    
    // Memory Info
    const memoryInfo = document.getElementById('memory-info');
    if (memoryInfo && data.memory_info) {
        memoryInfo.innerHTML = `
            <div class="row">
                <div class="col-sm-4"><strong>Total:</strong></div>
                <div class="col-sm-8">${formatBytes(data.memory_info.total)}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Available:</strong></div>
                <div class="col-sm-8">${formatBytes(data.memory_info.available)}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Used:</strong></div>
                <div class="col-sm-8">${formatBytes(data.memory_info.used)} (${data.memory_percent.toFixed(1)}%)</div>
            </div>
        `;
    }
    
    // Temperature Info
    const temperatureInfo = document.getElementById('temperature-info');
    if (temperatureInfo) {
        if (data.temperature_info && data.temperature_info.length > 0) {
            temperatureInfo.innerHTML = data.temperature_info.map(temp => `
                <div class="row mb-1">
                    <div class="col-sm-6"><strong>${temp.name}:</strong></div>
                    <div class="col-sm-6">${temp.temperature}°C</div>
                </div>
            `).join('');
        } else {
            temperatureInfo.innerHTML = '<p class="text-muted">Temperature information not available</p>';
        }
    }
}

// Update process table
function updateProcessTable(data) {
    const processTable = document.getElementById('process-table');
    if (!processTable || !data.top_processes) return;
    
    const processes = data.top_processes.slice(0, 10); // Top 10 processes
    
    processTable.innerHTML = processes.map(proc => `
        <tr>
            <td>${proc.name}</td>
            <td>${proc.pid}</td>
            <td>${proc.cpu_percent ? proc.cpu_percent.toFixed(1) : '0.0'}%</td>
            <td>${proc.memory_percent ? proc.memory_percent.toFixed(1) : '0.0'}%</td>
            <td>${formatBytes(proc.memory_info || 0)}</td>
        </tr>
    `).join('');
}

// Start monitoring
function startMonitoring() {
    if (!isMonitoringActive) {
        isMonitoringActive = true;
        monitoringInterval = setInterval(loadSystemMetrics, 3000); // Update every 3 seconds
    }
}

// Stop monitoring
function stopMonitoring() {
    if (isMonitoringActive) {
        isMonitoringActive = false;
        if (monitoringInterval) {
            clearInterval(monitoringInterval);
        }
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

// Show error message
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopMonitoring();
});