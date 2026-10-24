#!/usr/bin/env python3
"""
Standalone Web Server for NovaSphere
Direct Flask server for testing the web interface
"""

import os
import sys
import json
import platform
import webbrowser
import threading
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from flask import Flask, jsonify, request, send_file, send_from_directory
    from flask_cors import CORS
    import psutil
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install flask flask-cors psutil")
    DEPENDENCIES_AVAILABLE = False
    sys.exit(1)

# Create Flask app
app = Flask(__name__, 
           static_folder=str(Path(__file__).parent / "static"))

# Enable CORS
CORS(app)

# Configuration
CONFIG = {
    'host': '127.0.0.1',
    'port': 5000,
    'debug': True,
    'auto_open_browser': True
}

# Main routes
@app.route('/')
def index():
    """Serve the main index.html"""
    index_path = Path(__file__).parent / "index.html"
    return send_file(str(index_path))

@app.route('/test')
def test_integration():
    """Serve the integration test page"""
    test_path = Path(__file__).parent / "test_integration.html"
    return send_file(str(test_path))

@app.route('/main.css')
def main_css():
    """Serve main CSS file"""
    css_path = Path(__file__).parent / "main.css"
    return send_file(str(css_path), mimetype='text/css')

@app.route('/app.js')
def app_js():
    """Serve main JavaScript file"""
    js_path = Path(__file__).parent / "app.js"
    return send_file(str(js_path), mimetype='application/javascript')

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

# API Routes
@app.route('/api/battery/info')
def api_battery_info():
    """Get battery information"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            info = {
                "battery_percent": int(battery.percent),
                "power_plugged": battery.power_plugged
            }
        else:
            info = {
                "battery_percent": 100,
                "power_plugged": True,
                "error": "No battery detected (desktop system)"
            }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({
            "battery_percent": 0,
            "power_plugged": False,
            "error": str(e)
        }), 500

@app.route('/api/monitoring/metrics')
def api_monitoring_metrics():
    """Get system monitoring metrics"""
    try:
        # Get basic metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Get disk usage (handle different OS)
        if os.name == 'nt':  # Windows
            disk = psutil.disk_usage('C:')
        else:  # Unix/Linux
            disk = psutil.disk_usage('/')
        
        # Network I/O
        net_io = psutil.net_io_counters()
        
        # Top processes
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    proc_info['cpu_percent'] = proc.cpu_percent()
                    proc_info['memory_percent'] = proc.memory_percent()
                    if proc_info['memory_info']:
                        proc_info['memory_info'] = proc_info['memory_info'].rss
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get top 10
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            processes = processes[:10]
        except Exception:
            processes = []
        
        # Build response
        metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "platform": platform.system(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "network_connected": True,
            "memory_info": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used
            },
            "cpu_info": {
                "cores": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "brand": platform.processor()
            },
            "top_processes": processes,
            "network_io": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            }
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "network_connected": False
        }), 500

@app.route('/api/diagnostics/run', methods=['POST'])
def api_run_diagnostics():
    """Run hardware diagnostic tests"""
    try:
        data = request.get_json() or {}
        test_name = data.get('test', 'unknown')
        
        # Simulate test results
        test_results = {
            'bluetooth': {'status': 'passed', 'message': 'Bluetooth adapter detected'},
            'wifi': {'status': 'passed', 'message': 'Wi-Fi adapter working'},
            'camera': {'status': 'passed', 'message': 'Camera device found'},
            'microphone': {'status': 'passed', 'message': 'Audio input detected'},
            'speaker': {'status': 'passed', 'message': 'Audio output working'},
            'keyboard': {'status': 'passed', 'message': 'Keyboard input functional'}
        }
        
        result = test_results.get(test_name, {'status': 'failed', 'message': f'Unknown test: {test_name}'})
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/packages/status')
def api_packages_status():
    """Check package manager availability"""
    try:
        import subprocess
        
        # Check if winget is available
        try:
            result = subprocess.run(['winget', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
            version = result.stdout.strip() if available else "Not available"
        except Exception:
            available = False
            version = "Not available"
        
        return jsonify({
            "available": available,
            "version": version
        })
    except Exception as e:
        return jsonify({
            "available": False,
            "error": str(e)
        })

@app.route('/api/packages/list')
def api_packages_list():
    """List installed packages (mock data)"""
    try:
        # Mock package data for demonstration
        mock_packages = [
            {"id": "Microsoft.WindowsTerminal", "name": "Windows Terminal", "version": "1.18.0"},
            {"id": "Microsoft.VisualStudioCode", "name": "Visual Studio Code", "version": "1.84.0"},
            {"id": "Python.Python.3.11", "name": "Python 3.11", "version": "3.11.6"},
            {"id": "Git.Git", "name": "Git", "version": "2.42.0"},
        ]
        
        return jsonify({"packages": mock_packages})
    except Exception as e:
        return jsonify({"packages": [], "error": str(e)})

@app.route('/api/packages/count')
def api_packages_count():
    """Get package count information"""
    try:
        return jsonify({
            "installed_count": 42,
            "upgradable_count": 3
        })
    except Exception as e:
        return jsonify({
            "installed_count": 0,
            "upgradable_count": 0,
            "error": str(e)
        })

def main():
    """Main function to run the web server"""
    if not DEPENDENCIES_AVAILABLE:
        return
    
    host = CONFIG['host']
    port = CONFIG['port']
    
    print("🌐 NovaSphere - Web Interface")
    print(f"🚀 Starting server on http://{host}:{port}")
    print("📋 Features available:")
    print("   • System Dashboard with real-time metrics")
    print("   • Battery monitoring")
    print("   • Hardware diagnostics")
    print("   • System monitoring with charts")
    print("   • Package management")
    print("\n💡 Open your browser and navigate to the URL above")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    # Auto-open browser
    if CONFIG['auto_open_browser']:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    
    try:
        app.run(host=host, port=port, debug=CONFIG['debug'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()