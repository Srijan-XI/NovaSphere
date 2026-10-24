/**
 * NovaSphere - Main JavaScript Application
 * Handles navigation, API calls, and dynamic content loading
 */

// Global variables
let currentSection = 'home';
let isMonitoring = false;
let monitoringInterval = null;
let systemData = {};
let loadingModal = null;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing NovaSphere...');
    
    // Initialize Bootstrap components
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    // Set up navigation
    setupNavigation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize cross-file integration
    initializeCrossFileIntegration();
    
    // Load initial system status
    loadSystemStatus();
    
    // Set up periodic updates for home page
    setInterval(loadSystemStatus, 30000); // Update every 30 seconds
    
    // Initialize static JS files if they're loaded
    setTimeout(() => {
        // Check if static JS files are loaded and initialize them
        if (typeof window.setupToolNavigation === 'function') {
            window.setupToolNavigation();
        }
        
        // Emit app ready event for other files to listen to
        window.appEvents.emit('appReady', { timestamp: Date.now() });
    }, 1000);
    
    console.log('Application initialized successfully');
}

/**
 * Set up navigation functionality
 */
function setupNavigation() {
    // Handle navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSection = this.getAttribute('href').substring(1);
            navigateToSection(targetSection);
        });
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.section) {
            showSection(e.state.section);
        }
    });
    
    // Set initial state
    history.replaceState({ section: 'home' }, 'Home', '#home');
}

/**
 * Set up event listeners for buttons and interactions
 */
function setupEventListeners() {
    // Refresh buttons
    document.getElementById('refresh-dashboard')?.addEventListener('click', () => loadDashboardContent());
    document.getElementById('refresh-battery')?.addEventListener('click', () => loadBatteryContent());
    document.getElementById('run-all-tests')?.addEventListener('click', () => runAllDiagnostics());
    document.getElementById('toggle-monitoring')?.addEventListener('click', () => toggleMonitoring());
    document.getElementById('export-metrics')?.addEventListener('click', () => exportMetrics());
}

/**
 * Navigate to a specific section
 * @param {string} sectionId - The ID of the section to navigate to
 */
function navigateToSection(sectionId) {
    showSection(sectionId);
    history.pushState({ section: sectionId }, sectionId, `#${sectionId}`);
    
    // Update navigation active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });
}

/**
 * Show a specific section and load its content
 * @param {string} sectionId - The ID of the section to show
 */
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
        
        // Load section-specific content
        loadSectionContent(sectionId);
    }
}

/**
 * Load content for a specific section
 * @param {string} sectionId - The ID of the section to load content for
 */
function loadSectionContent(sectionId) {
    switch (sectionId) {
        case 'dashboard':
            loadDashboardContent();
            break;
        case 'battery':
            loadBatteryContent();
            break;
        case 'diagnostics':
            loadDiagnosticsContent();
            break;
        case 'monitoring':
            loadMonitoringContent();
            break;
        case 'home':
            // Home content is static, just update system status
            loadSystemStatus();
            break;
    }
}

/**
 * Load system status for the home page
 */
async function loadSystemStatus() {
    try {
        // Load basic system metrics
        const response = await fetch('/api/monitoring/metrics');
        if (response.ok) {
            const data = await response.json();
            updateSystemStatus(data);
        }
        
        // Load battery status
        const batteryResponse = await fetch('/api/battery/info');
        if (batteryResponse.ok) {
            const batteryData = await batteryResponse.json();
            updateBatteryStatus(batteryData);
        }
    } catch (error) {
        console.error('Error loading system status:', error);
    }
}

/**
 * Update system status display
 * @param {Object} data - System metrics data
 */
function updateSystemStatus(data) {
    // Update CPU status
    const cpuStatus = document.getElementById('cpu-status');
    if (cpuStatus && data.cpu_percent !== undefined) {
        cpuStatus.textContent = `${data.cpu_percent.toFixed(1)}%`;
        cpuStatus.className = `badge ${getCpuStatusClass(data.cpu_percent)}`;
    }
    
    // Update Memory status
    const memoryStatus = document.getElementById('memory-status');
    if (memoryStatus && data.memory_percent !== undefined) {
        memoryStatus.textContent = `${data.memory_percent.toFixed(1)}%`;
        memoryStatus.className = `badge ${getMemoryStatusClass(data.memory_percent)}`;
    }
    
    // Update Disk status
    const diskStatus = document.getElementById('disk-status');
    if (diskStatus && data.disk_percent !== undefined) {
        diskStatus.textContent = `${data.disk_percent.toFixed(1)}%`;
        diskStatus.className = `badge ${getDiskStatusClass(data.disk_percent)}`;
    }
}

/**
 * Update battery status display
 * @param {Object} data - Battery data
 */
function updateBatteryStatus(data) {
    const batteryStatus = document.getElementById('battery-status');
    if (batteryStatus && data.battery_percent !== undefined) {
        batteryStatus.textContent = `${data.battery_percent}%`;
        batteryStatus.className = `badge ${getBatteryStatusClass(data.battery_percent, data.power_plugged)}`;
    }
}

/**
 * Get CSS class for CPU status based on usage
 * @param {number} cpuPercent - CPU usage percentage
 * @returns {string} CSS class name
 */
function getCpuStatusClass(cpuPercent) {
    if (cpuPercent < 30) return 'bg-success';
    if (cpuPercent < 70) return 'bg-warning';
    return 'bg-danger';
}

/**
 * Get CSS class for memory status based on usage
 * @param {number} memoryPercent - Memory usage percentage
 * @returns {string} CSS class name
 */
function getMemoryStatusClass(memoryPercent) {
    if (memoryPercent < 50) return 'bg-success';
    if (memoryPercent < 80) return 'bg-warning';
    return 'bg-danger';
}

/**
 * Get CSS class for disk status based on usage
 * @param {number} diskPercent - Disk usage percentage
 * @returns {string} CSS class name
 */
function getDiskStatusClass(diskPercent) {
    if (diskPercent < 70) return 'bg-success';
    if (diskPercent < 90) return 'bg-warning';
    return 'bg-danger';
}

/**
 * Get CSS class for battery status
 * @param {number} batteryPercent - Battery percentage
 * @param {boolean} powerPlugged - Whether power is plugged in
 * @returns {string} CSS class name
 */
function getBatteryStatusClass(batteryPercent, powerPlugged) {
    if (powerPlugged) return 'bg-info';
    if (batteryPercent > 50) return 'bg-success';
    if (batteryPercent > 20) return 'bg-warning';
    return 'bg-danger';
}

/**
 * Load dashboard content
 */
async function loadDashboardContent() {
    const contentDiv = document.getElementById('dashboard-content');
    const metricsDiv = document.getElementById('dashboard-metrics');
    showLoading('Loading dashboard...');
    
    try {
        // Build dashboard HTML structure
        metricsDiv.innerHTML = `
            <div class="col-lg-8">
                <div class="card h-100">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line me-2"></i>System Overview</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="dashboardChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card h-100">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>System Information</h5>
                    </div>
                    <div class="card-body">
                        <div id="system-info">Loading...</div>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mt-4">
                <div class="card h-100">
                    <div class="card-header">
                        <h5><i class="fas fa-tasks me-2"></i>Top Processes</h5>
                    </div>
                    <div class="card-body">
                        <div id="top-processes">Loading...</div>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mt-4">
                <div class="card h-100">
                    <div class="card-header">
                        <h5><i class="fas fa-network-wired me-2"></i>Network Information</h5>
                    </div>
                    <div class="card-body">
                        <div id="network-info">Loading...</div>
                    </div>
                </div>
            </div>
        `;
        
        // Load dashboard data
        await loadDashboardData();
        
        // If dashboard.js is available, initialize it
        if (typeof loadSystemInfo === 'function') {
            loadSystemInfo();
        }
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        metricsDiv.innerHTML = `<div class="col-12"><div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>Error loading dashboard content: ${error.message}
        </div></div>`;
    } finally {
        hideLoading();
    }
}

/**
 * Load dashboard data and create charts
 */
async function loadDashboardData() {
    try {
        const response = await fetch('/api/monitoring/metrics');
        if (!response.ok) throw new Error('Failed to fetch metrics');
        
        const data = await response.json();
        
        // Create dashboard chart
        createDashboardChart(data);
        
        // Update system info
        updateSystemInfo(data);
        
        // Update top processes
        updateTopProcesses(data.top_processes || []);
        
        // Update network info
        updateNetworkInfo(data);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

/**
 * Create dashboard chart
 * @param {Object} data - System data
 */
function createDashboardChart(data) {
    const ctx = document.getElementById('dashboardChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['CPU Usage', 'Memory Usage', 'Disk Usage'],
            datasets: [{
                data: [
                    data.cpu_percent || 0,
                    data.memory_percent || 0,
                    data.disk_percent || 0
                ],
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#ffc107'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Update system information display
 * @param {Object} data - System data
 */
function updateSystemInfo(data) {
    const systemInfoDiv = document.getElementById('system-info');
    if (!systemInfoDiv) return;
    
    systemInfoDiv.innerHTML = `
        <div class="row g-2">
            <div class="col-12">
                <strong>Platform:</strong> ${data.platform || 'Unknown'}
            </div>
            <div class="col-12">
                <strong>Architecture:</strong> ${data.architecture || 'Unknown'}
            </div>
            <div class="col-12">
                <strong>Processor:</strong> ${data.processor || 'Unknown'}
            </div>
            <div class="col-12">
                <strong>Total Memory:</strong> ${formatBytes(data.memory_info?.total || 0)}
            </div>
            <div class="col-12">
                <strong>Available Memory:</strong> ${formatBytes(data.memory_info?.available || 0)}
            </div>
        </div>
    `;
}

/**
 * Update top processes display
 * @param {Array} processes - Array of process data
 */
function updateTopProcesses(processes) {
    const processesDiv = document.getElementById('top-processes');
    if (!processesDiv) return;
    
    if (processes.length === 0) {
        processesDiv.innerHTML = '<p class="text-muted">No process data available</p>';
        return;
    }
    
    const topProcesses = processes.slice(0, 5);
    processesDiv.innerHTML = `
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Process</th>
                        <th>CPU %</th>
                        <th>Memory</th>
                    </tr>
                </thead>
                <tbody>
                    ${topProcesses.map(proc => `
                        <tr>
                            <td>${proc.name || 'Unknown'}</td>
                            <td>${(proc.cpu_percent || 0).toFixed(1)}%</td>
                            <td>${formatBytes(proc.memory_info || 0)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Update network information display
 * @param {Object} data - System data
 */
function updateNetworkInfo(data) {
    const networkInfoDiv = document.getElementById('network-info');
    if (!networkInfoDiv) return;
    
    networkInfoDiv.innerHTML = `
        <div class="row g-2">
            <div class="col-12">
                <strong>Status:</strong>
                <span class="badge ${data.network_connected ? 'bg-success' : 'bg-danger'}">
                    ${data.network_connected ? 'Connected' : 'Disconnected'}
                </span>
            </div>
            <div class="col-12">
                <strong>Bytes Sent:</strong> ${formatBytes(data.network_io?.bytes_sent || 0)}
            </div>
            <div class="col-12">
                <strong>Bytes Received:</strong> ${formatBytes(data.network_io?.bytes_recv || 0)}
            </div>
        </div>
    `;
}

/**
 * Load battery content
 */
async function loadBatteryContent() {
    const contentDiv = document.getElementById('battery-content');
    const batteryInfoDiv = document.getElementById('battery-info');
    showLoading('Loading battery information...');
    
    try {
        const response = await fetch('/api/battery/info');
        if (!response.ok) throw new Error('Failed to fetch battery info');
        
        const data = await response.json();
        
        // Build battery interface HTML
        batteryInfoDiv.innerHTML = `
            <div class="col-lg-8">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <div class="battery-display">
                            <div class="battery-icon mb-3">
                                <i id="battery-icon" class="fas fa-battery-half fa-4x text-${getBatteryColor(data.battery_percent)}"></i>
                            </div>
                            <h2 id="battery-percentage">${data.battery_percent}%</h2>
                            <p id="battery-status" class="lead text-${data.power_plugged ? 'success' : 'warning'}">
                                ${data.power_plugged ? 'Charging' : 'On Battery'}
                            </p>
                            <div class="progress mb-3" style="height: 25px;">
                                <div id="battery-progress" class="progress-bar bg-${getBatteryColor(data.battery_percent)}" 
                                     style="width: ${data.battery_percent}%" role="progressbar">
                                    ${data.battery_percent}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card h-100">
                    <div class="card-header">
                        <h6><i class="fas fa-info-circle me-2"></i>Battery Details</h6>
                    </div>
                    <div class="card-body">
                        <div class="row g-2">
                            <div class="col-12">
                                <div class="info-item">
                                    <strong>Charging Status:</strong>
                                    <span id="charging-status">${data.power_plugged ? 'Charging' : 'Not Charging'}</span>
                                </div>
                            </div>
                            <div class="col-12">
                                <div class="info-item">
                                    <strong>Power Plugged:</strong>
                                    <span id="power-plugged">${data.power_plugged ? 'Yes' : 'No'}</span>
                                </div>
                            </div>
                            <div class="col-12">
                                <div class="info-item">
                                    <strong>Battery Level:</strong>
                                    <span>${data.battery_percent}%</span>
                                </div>
                            </div>
                            <div class="col-12">
                                <div class="info-item">
                                    <strong>Health Status:</strong>
                                    <span class="badge bg-${data.battery_percent > 80 ? 'success' : data.battery_percent > 50 ? 'warning' : 'danger'}">
                                        ${data.battery_percent > 80 ? 'Good' : data.battery_percent > 50 ? 'Fair' : 'Poor'}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-primary btn-sm" onclick="refreshBatteryInfo()">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // If battery.js is available, initialize it
        if (typeof refreshBatteryInfo === 'function') {
            // Battery.js is loaded, it will handle updates
        }
        
    } catch (error) {
        console.error('Error loading battery content:', error);
        batteryInfoDiv.innerHTML = `<div class="col-12"><div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>Error loading battery information: ${error.message}
        </div></div>`;
    } finally {
        hideLoading();
    }
}

/**
 * Get battery color based on percentage
 * @param {number} percent - Battery percentage
 * @returns {string} Color class
 */
function getBatteryColor(percent) {
    if (percent > 50) return 'success';
    if (percent > 20) return 'warning';
    return 'danger';
}

/**
 * Load diagnostics content
 */
function loadDiagnosticsContent() {
    const contentDiv = document.getElementById('diagnostics-content');
    const testsDiv = document.getElementById('diagnostics-tests');
    
    // Build diagnostics interface HTML
    testsDiv.innerHTML = `
        <div class="col-12 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-play me-2"></i>Test Controls</h5>
                </div>
                <div class="card-body">
                    <div class="d-flex gap-2 flex-wrap">
                        <button class="btn btn-primary" onclick="runAllDiagnostics()">
                            <i class="fas fa-play me-1"></i>Run All Tests
                        </button>
                        <button class="btn btn-secondary" onclick="clearResults()">
                            <i class="fas fa-trash me-1"></i>Clear Results
                        </button>
                        <button class="btn btn-info" onclick="exportResults()" style="display:none;" id="export-btn">
                            <i class="fas fa-download me-1"></i>Export Results
                        </button>
                    </div>
                    <div id="test-progress" class="mt-3" style="display: none;">
                        <div class="d-flex align-items-center">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            <span>Running tests...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-hover">
                <div class="card-body text-center">
                    <i class="fas fa-bluetooth fa-3x text-primary mb-3"></i>
                    <h5>Bluetooth Test</h5>
                    <p class="text-muted">Test Bluetooth connectivity and devices</p>
                    <button class="btn btn-outline-primary" onclick="runSingleTest('bluetooth')">
                        <i class="fas fa-play me-1"></i>Run Test
                    </button>
                    <div id="bluetooth-result" class="mt-2"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-hover">
                <div class="card-body text-center">
                    <i class="fas fa-wifi fa-3x text-success mb-3"></i>
                    <h5>Wi-Fi Test</h5>
                    <p class="text-muted">Test wireless network connectivity</p>
                    <button class="btn btn-outline-success" onclick="runSingleTest('wifi')">
                        <i class="fas fa-play me-1"></i>Run Test
                    </button>
                    <div id="wifi-result" class="mt-2"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-hover">
                <div class="card-body text-center">
                    <i class="fas fa-camera fa-3x text-info mb-3"></i>
                    <h5>Camera Test</h5>
                    <p class="text-muted">Test camera functionality</p>
                    <button class="btn btn-outline-info" onclick="runSingleTest('camera')">
                        <i class="fas fa-play me-1"></i>Run Test
                    </button>
                    <div id="camera-result" class="mt-2"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-hover">
                <div class="card-body text-center">
                    <i class="fas fa-microphone fa-3x text-warning mb-3"></i>
                    <h5>Microphone Test</h5>
                    <p class="text-muted">Test microphone input</p>
                    <button class="btn btn-outline-warning" onclick="runSingleTest('microphone')">
                        <i class="fas fa-play me-1"></i>Run Test
                    </button>
                    <div id="microphone-result" class="mt-2"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-hover">
                <div class="card-body text-center">
                    <i class="fas fa-volume-up fa-3x text-danger mb-3"></i>
                    <h5>Speaker Test</h5>
                    <p class="text-muted">Test audio output</p>
                    <button class="btn btn-outline-danger" onclick="runSingleTest('speaker')">
                        <i class="fas fa-play me-1"></i>Run Test
                    </button>
                    <div id="speaker-result" class="mt-2"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-hover">
                <div class="card-body text-center">
                    <i class="fas fa-keyboard fa-3x text-secondary mb-3"></i>
                    <h5>Keyboard Test</h5>
                    <p class="text-muted">Test keyboard input</p>
                    <button class="btn btn-outline-secondary" onclick="runSingleTest('keyboard')">
                        <i class="fas fa-play me-1"></i>Run Test
                    </button>
                    <div id="keyboard-result" class="mt-2"></div>
                </div>
            </div>
        </div>
        <div class="col-12 mt-4">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-clipboard-check me-2"></i>Test Summary</h5>
                </div>
                <div class="card-body">
                    <div id="test-summary">
                        <p class="text-muted">No tests have been run yet. Click "Run All Tests" to begin.</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // If diagnostics.js is available, initialize it
    if (typeof clearResults === 'function') {
        clearResults();
    }
}

/**
 * Run a specific diagnostic test
 * @param {string} testName - Name of the test to run
 */
async function runDiagnostic(testName) {
    const resultDiv = document.getElementById(`${testName}-result`);
    resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
    
    try {
        const response = await fetch('/api/diagnostics/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ test: testName })
        });
        
        if (response.ok) {
            const result = await response.json();
            const success = result.status === 'passed' || result.success;
            resultDiv.innerHTML = `
                <div class="alert alert-${success ? 'success' : 'danger'} mt-2">
                    <i class="fas fa-${success ? 'check' : 'times'} me-1"></i>
                    ${success ? 'PASSED' : 'FAILED'}
                </div>
            `;
        } else {
            throw new Error('Test failed');
        }
    } catch (error) {
        console.error(`Error running ${testName} test:`, error);
        resultDiv.innerHTML = `
            <div class="alert alert-danger mt-2">
                <i class="fas fa-times me-1"></i>ERROR
            </div>
        `;
    }
}

/**
 * Run all diagnostic tests
 */
async function runAllDiagnostics() {
    const tests = ['bluetooth', 'wifi', 'camera', 'microphone', 'speaker', 'keyboard'];
    showLoading('Running all diagnostic tests...');
    
    try {
        for (const test of tests) {
            await runDiagnostic(test);
            // Small delay between tests
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    } catch (error) {
        console.error('Error running all diagnostics:', error);
    } finally {
        hideLoading();
    }
}

/**
 * Load monitoring content
 */
function loadMonitoringContent() {
    const contentDiv = document.getElementById('monitoring-content');
    
    contentDiv.innerHTML = `
        <div class="content-area">
            <p class="text-muted">Real-time system monitoring will be displayed here.</p>
            <p>This feature integrates with the existing monitoring dashboard.</p>
        </div>
    `;
}

/**
 * Toggle system monitoring
 */
function toggleMonitoring() {
    const button = document.getElementById('toggle-monitoring');
    
    if (isMonitoring) {
        // Stop monitoring
        if (monitoringInterval) {
            clearInterval(monitoringInterval);
            monitoringInterval = null;
        }
        isMonitoring = false;
        button.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
        button.className = 'btn btn-outline-warning me-2';
    } else {
        // Start monitoring
        isMonitoring = true;
        monitoringInterval = setInterval(loadSystemStatus, 5000);
        button.innerHTML = '<i class="fas fa-pause"></i> Stop Monitoring';
        button.className = 'btn btn-warning me-2';
    }
}

/**
 * Export system metrics
 */
function exportMetrics() {
    const data = {
        timestamp: new Date().toISOString(),
        systemData: systemData
    };
    
    downloadJSON(data, `system_metrics_${new Date().toISOString().split('T')[0]}.json`);
}

/**
 * Show about modal
 */
function showAbout() {
    const aboutModal = new bootstrap.Modal(document.getElementById('aboutModal'));
    aboutModal.show();
}

/**
 * Show loading modal with message
 * @param {string} message - Loading message
 */
function showLoading(message = 'Loading...') {
    document.getElementById('loading-message').textContent = message;
    loadingModal.show();
}

/**
 * Hide loading modal
 */
function hideLoading() {
    loadingModal.hide();
}

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Format bytes to human readable string
 * @param {number} bytes - Number of bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted string
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Download data as JSON file
 * @param {Object} data - Data to download
 * @param {string} filename - Filename for download
 */
function downloadJSON(data, filename) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = filename;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

/**
 * Utility functions for cross-file integration
 */
function updateGlobalData(key, data) {
    window.appData[key] = data;
    window.appEvents.emit('dataUpdated', { key, data });
}

function getGlobalData(key) {
    return window.appData[key];
}

/**
 * Enhanced error handling with user notifications
 */
function handleError(error, context = 'Operation') {
    console.error(`${context} error:`, error);
    showNotification(`${context} failed: ${error.message}`, 'error');
}

/**
 * Create loading placeholder
 */
function createLoadingHTML(message = 'Loading...') {
    return `
        <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
            <div class="text-center">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted">${message}</p>
            </div>
        </div>
    `;
}

/**
 * Initialize cross-file event listeners
 */
function initializeCrossFileIntegration() {
    // Listen for data updates from other files
    window.appEvents.on('dataUpdated', function(event) {
        const { key, data } = event.detail;
        console.log(`Data updated: ${key}`, data);
        
        // Update relevant sections based on data type
        if (key === 'systemData' && currentSection === 'home') {
            updateSystemStatus(data);
        }
    });
    
    // Listen for section changes
    window.appEvents.on('sectionChanged', function(event) {
        const { section } = event.detail;
        console.log(`Section changed to: ${section}`);
    });
}

// Global functions for HTML onclick handlers and integration
window.navigateToSection = navigateToSection;
window.showAbout = showAbout;
window.runDiagnostic = runDiagnostic;

// Function aliases for integration with static JS files
window.runSingleTest = runDiagnostic;  // Alias for diagnostics.js compatibility
window.refreshBatteryInfo = loadBatteryContent;  // Alias for battery.js compatibility

// Global data store for cross-file communication
window.appData = {
    currentSection: 'home',
    systemData: {},
    batteryData: {},
    diagnosticsResults: {},
    isMonitoring: false
};

// Event system for cross-file communication
window.appEvents = {
    emit: function(event, data) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    },
    on: function(event, callback) {
        document.addEventListener(event, callback);
    }
};
