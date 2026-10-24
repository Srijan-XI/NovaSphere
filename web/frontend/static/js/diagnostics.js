// Diagnostics JavaScript
let currentTests = {};
let testResults = {};

// Initialize diagnostics
document.addEventListener('DOMContentLoaded', function() {
    clearResults();
});

// Run all tests
async function runAllTests() {
    const testProgress = document.getElementById('test-progress');
    testProgress.style.display = 'block';
    
    const tests = ['bluetooth', 'wifi', 'camera', 'microphone', 'speaker', 'keyboard'];
    testResults = {};
    
    try {
        for (const test of tests) {
            await runSingleTest(test, false);
            await new Promise(resolve => setTimeout(resolve, 500)); // Small delay between tests
        }
        
        updateTestSummary();
    } catch (error) {
        console.error('Error running tests:', error);
        showError('Error running diagnostic tests');
    } finally {
        testProgress.style.display = 'none';
    }
}

// Run single test
async function runSingleTest(testName, updateSummary = true) {
    const resultDiv = document.getElementById(`${testName}-result`);
    if (!resultDiv) return;
    
    // Show loading state
    resultDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Running ${testName} test...</span>
        </div>
    `;
    
    try {
        const response = await fetch(`/api/diagnostics/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ test: testName })
        });
        
        if (response.ok) {
            const result = await response.json();
            testResults[testName] = result;
            displayTestResult(testName, result);
        } else {
            const error = await response.text();
            displayTestError(testName, error);
        }
    } catch (error) {
        console.error(`Error running ${testName} test:`, error);
        displayTestError(testName, 'Network error occurred');
    }
    
    if (updateSummary) {
        updateTestSummary();
    }
}

// Display test result
function displayTestResult(testName, result) {
    const resultDiv = document.getElementById(`${testName}-result`);
    if (!resultDiv) return;
    
    const success = result.status === 'passed' || result.success;
    const statusClass = success ? 'success' : 'danger';
    const statusIcon = success ? 'check-circle' : 'times-circle';
    
    let resultHtml = `
        <div class="alert alert-${statusClass} mb-2">
            <i class="fas fa-${statusIcon}"></i> 
            <strong>${success ? 'PASSED' : 'FAILED'}</strong>
        </div>
    `;
    
    if (result.message) {
        resultHtml += `<small class="text-muted">${result.message}</small>`;
    }
    
    if (result.details) {
        resultHtml += `<div class="mt-2"><small>${JSON.stringify(result.details, null, 2)}</small></div>`;
    }
    
    if (result.error) {
        resultHtml += `<div class="text-danger mt-2"><small>Error: ${result.error}</small></div>`;
    }
    
    resultDiv.innerHTML = resultHtml;
}

// Display test error
function displayTestError(testName, error) {
    const resultDiv = document.getElementById(`${testName}-result`);
    if (!resultDiv) return;
    
    resultDiv.innerHTML = `
        <div class="alert alert-danger mb-2">
            <i class="fas fa-times-circle"></i> 
            <strong>ERROR</strong>
        </div>
        <small class="text-danger">${error}</small>
    `;
    
    testResults[testName] = { status: 'error', error: error };
}

// Update test summary
function updateTestSummary() {
    const summaryDiv = document.getElementById('test-summary');
    if (!summaryDiv) return;
    
    const totalTests = Object.keys(testResults).length;
    if (totalTests === 0) {
        summaryDiv.innerHTML = '<p class="text-muted">No tests have been run yet. Click "Run All Tests" to begin.</p>';
        return;
    }
    
    let passed = 0;
    let failed = 0;
    let errors = 0;
    
    for (const [testName, result] of Object.entries(testResults)) {
        if (result.status === 'passed' || result.success) {
            passed++;
        } else if (result.status === 'error') {
            errors++;
        } else {
            failed++;
        }
    }
    
    const timestamp = new Date().toLocaleString();
    
    summaryDiv.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body text-center">
                        <h3>${passed}</h3>
                        <p class="mb-0">Passed</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-danger text-white">
                    <div class="card-body text-center">
                        <h3>${failed}</h3>
                        <p class="mb-0">Failed</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body text-center">
                        <h3>${errors}</h3>
                        <p class="mb-0">Errors</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body text-center">
                        <h3>${totalTests}</h3>
                        <p class="mb-0">Total</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-3">
            <p class="text-muted"><small>Last updated: ${timestamp}</small></p>
        </div>
    `;
}

// Clear all results
function clearResults() {
    testResults = {};
    
    const testNames = ['bluetooth', 'wifi', 'camera', 'microphone', 'speaker', 'keyboard'];
    testNames.forEach(testName => {
        const resultDiv = document.getElementById(`${testName}-result`);
        if (resultDiv) {
            resultDiv.innerHTML = '<p class="text-muted">Click the test button to run this diagnostic.</p>';
        }
    });
    
    updateTestSummary();
}

// Export results
function exportResults() {
    if (Object.keys(testResults).length === 0) {
        alert('No test results to export. Please run some tests first.');
        return;
    }
    
    const exportData = {
        timestamp: new Date().toISOString(),
        system: {
            userAgent: navigator.userAgent,
            platform: navigator.platform
        },
        results: testResults
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `diagnostic_results_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
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