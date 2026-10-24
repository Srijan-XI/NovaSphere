// Package Manager JavaScript
let wingetAvailable = false;

// Initialize package manager
document.addEventListener('DOMContentLoaded', function() {
    checkWingetAvailability();
    setupSearchHandler();
});

// Check winget availability
async function checkWingetAvailability() {
    const statusDiv = document.getElementById('winget-status');
    
    try {
        const response = await fetch('/api/packages/status');
        if (response.ok) {
            const data = await response.json();
            wingetAvailable = data.available;
            
            if (wingetAvailable) {
                statusDiv.innerHTML = `
                    <div class="d-flex align-items-center text-success">
                        <i class="fas fa-check-circle me-2"></i>
                        <span>Winget is available (${data.version || 'Unknown version'})</span>
                    </div>
                `;
                document.getElementById('package-content').style.display = 'block';
            } else {
                statusDiv.innerHTML = `
                    <div class="d-flex align-items-center text-danger">
                        <i class="fas fa-times-circle me-2"></i>
                        <span>Winget is not available on this system</span>
                    </div>
                `;
            }
        } else {
            throw new Error('Failed to check winget status');
        }
    } catch (error) {
        console.error('Error checking winget availability:', error);
        statusDiv.innerHTML = `
            <div class="d-flex align-items-center text-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <span>Unable to check winget availability</span>
            </div>
        `;
    }
}

// Load installed packages
async function loadInstalledPackages() {
    if (!wingetAvailable) return;
    
    const packagesDiv = document.getElementById('installed-packages');
    packagesDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Loading installed packages...</span>
        </div>
    `;
    
    try {
        const response = await fetch('/api/packages/list');
        if (response.ok) {
            const data = await response.json();
            displayPackageList(packagesDiv, data.packages || [], 'installed');
        } else {
            throw new Error('Failed to load installed packages');
        }
    } catch (error) {
        console.error('Error loading installed packages:', error);
        packagesDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> Error loading installed packages: ${error.message}
            </div>
        `;
    }
}

// Load upgradable packages
async function loadUpgradablePackages() {
    if (!wingetAvailable) return;
    
    const packagesDiv = document.getElementById('upgradable-packages');
    packagesDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Checking for package updates...</span>
        </div>
    `;
    
    try {
        const response = await fetch('/api/packages/upgradable');
        if (response.ok) {
            const data = await response.json();
            displayPackageList(packagesDiv, data.packages || [], 'upgradable');
        } else {
            throw new Error('Failed to load upgradable packages');
        }
    } catch (error) {
        console.error('Error loading upgradable packages:', error);
        packagesDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> Error checking for updates: ${error.message}
            </div>
        `;
    }
}

// Search packages
async function searchPackages() {
    if (!wingetAvailable) return;
    
    const query = document.getElementById('search-query').value.trim();
    if (!query) {
        alert('Please enter a search term');
        return;
    }
    
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Searching for "${query}"...</span>
        </div>
    `;
    
    try {
        const response = await fetch(`/api/packages/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const data = await response.json();
            displayPackageList(resultsDiv, data.packages || [], 'search');
        } else {
            throw new Error('Search failed');
        }
    } catch (error) {
        console.error('Error searching packages:', error);
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> Search error: ${error.message}
            </div>
        `;
    }
}

// Display package list
function displayPackageList(container, packages, type) {
    if (packages.length === 0) {
        container.innerHTML = `<p class="text-muted">No packages found.</p>`;
        return;
    }
    
    const tableHtml = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>ID</th>
                        <th>Version</th>
                        ${type === 'upgradable' ? '<th>Available</th>' : ''}
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${packages.map(pkg => `
                        <tr>
                            <td><strong>${pkg.name || pkg.id}</strong></td>
                            <td><small class="text-muted">${pkg.id}</small></td>
                            <td>${pkg.version || 'Unknown'}</td>
                            ${type === 'upgradable' ? `<td><span class="badge bg-primary">${pkg.available || 'Unknown'}</span></td>` : ''}
                            <td>
                                ${getPackageActions(pkg, type)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = tableHtml;
}

// Get package actions based on type
function getPackageActions(pkg, type) {
    switch (type) {
        case 'installed':
            return `<button class="btn btn-sm btn-outline-danger" onclick="uninstallPackage('${pkg.id}')">
                        <i class="fas fa-trash"></i> Uninstall
                    </button>`;
        case 'upgradable':
            return `<button class="btn btn-sm btn-success" onclick="upgradePackage('${pkg.id}')">
                        <i class="fas fa-arrow-up"></i> Upgrade
                    </button>`;
        case 'search':
            return `<button class="btn btn-sm btn-primary" onclick="installPackage('${pkg.id}', '${pkg.name || pkg.id}')">
                        <i class="fas fa-download"></i> Install
                    </button>`;
        default:
            return '';
    }
}

// Install package
function installPackage(packageId, packageName) {
    document.getElementById('install-package-name').textContent = packageName;
    
    const installModal = new bootstrap.Modal(document.getElementById('installModal'));
    installModal.show();
    
    document.getElementById('confirm-install').onclick = async function() {
        const progressDiv = document.getElementById('install-progress');
        progressDiv.style.display = 'block';
        
        try {
            const response = await fetch('/api/packages/install', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ package_id: packageId })
            });
            
            const result = await response.text();
            logOperation(`Install ${packageName}`, result, response.ok);
            
            if (response.ok) {
                installModal.hide();
                showSuccess(`Package "${packageName}" installed successfully`);
            } else {
                showError(`Failed to install package: ${result}`);
            }
        } catch (error) {
            console.error('Error installing package:', error);
            showError(`Error installing package: ${error.message}`);
        } finally {
            progressDiv.style.display = 'none';
        }
    };
}

// Upgrade package
async function upgradePackage(packageId) {
    if (!confirm(`Are you sure you want to upgrade ${packageId}?`)) return;
    
    try {
        const response = await fetch('/api/packages/upgrade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ package_id: packageId })
        });
        
        const result = await response.text();
        logOperation(`Upgrade ${packageId}`, result, response.ok);
        
        if (response.ok) {
            showSuccess(`Package "${packageId}" upgraded successfully`);
            loadUpgradablePackages(); // Refresh the list
        } else {
            showError(`Failed to upgrade package: ${result}`);
        }
    } catch (error) {
        console.error('Error upgrading package:', error);
        showError(`Error upgrading package: ${error.message}`);
    }
}

// Upgrade all packages
async function upgradeAllPackages() {
    if (!confirm('Are you sure you want to upgrade all packages? This may take a while.')) return;
    
    try {
        const response = await fetch('/api/packages/upgrade-all', {
            method: 'POST'
        });
        
        const result = await response.text();
        logOperation('Upgrade All Packages', result, response.ok);
        
        if (response.ok) {
            showSuccess('All packages upgraded successfully');
            loadUpgradablePackages(); // Refresh the list
        } else {
            showError(`Failed to upgrade packages: ${result}`);
        }
    } catch (error) {
        console.error('Error upgrading all packages:', error);
        showError(`Error upgrading packages: ${error.message}`);
    }
}

// Uninstall package
async function uninstallPackage(packageId) {
    if (!confirm(`Are you sure you want to uninstall ${packageId}?`)) return;
    
    try {
        const response = await fetch('/api/packages/uninstall', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ package_id: packageId })
        });
        
        const result = await response.text();
        logOperation(`Uninstall ${packageId}`, result, response.ok);
        
        if (response.ok) {
            showSuccess(`Package "${packageId}" uninstalled successfully`);
            loadInstalledPackages(); // Refresh the list
        } else {
            showError(`Failed to uninstall package: ${result}`);
        }
    } catch (error) {
        console.error('Error uninstalling package:', error);
        showError(`Error uninstalling package: ${error.message}`);
    }
}

// Log operation
function logOperation(operation, result, success) {
    const logDiv = document.getElementById('operation-results');
    const operationsLog = document.getElementById('operations-log');
    
    const timestamp = new Date().toLocaleString();
    const statusClass = success ? 'success' : 'danger';
    const statusIcon = success ? 'check-circle' : 'times-circle';
    
    const logEntry = `
        <div class="alert alert-${statusClass} alert-dismissible fade show" role="alert">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <i class="fas fa-${statusIcon}"></i> 
                    <strong>${operation}</strong>
                    <small class="text-muted d-block">${timestamp}</small>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            <div class="mt-2">
                <pre class="mb-0" style="white-space: pre-wrap; font-size: 0.875em;">${result}</pre>
            </div>
        </div>
    `;
    
    logDiv.innerHTML = logEntry + logDiv.innerHTML;
    operationsLog.style.display = 'block';
}

// Setup search handler
function setupSearchHandler() {
    const searchInput = document.getElementById('search-query');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchPackages();
            }
        });
    }
}

// Show success message
function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Show error message
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}