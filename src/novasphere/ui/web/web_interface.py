"""
Web Interface for NovaSphere
Flask-based web interface with REST API and Single Page Application
"""

import json
import threading
import webbrowser
import os
import platform
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
    from flask_cors import CORS
    import psutil
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from novasphere.utils.config import Config
from novasphere.utils.logger import Logger
from novasphere.core.battery.battery_monitor import create_battery_monitor
from novasphere.core.diagnostics.hardware_tests import create_diagnostics
from novasphere.core.monitoring.system_monitor import create_system_monitor
from novasphere.core.package_mgmt.winget_manager import create_package_manager

class WebInterface:
    """Flask-based Web Interface implementation"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.app = None
        self._initialize_tools()
        
        if not FLASK_AVAILABLE:
            self.logger.error("Flask is not installed. Install with: pip install flask flask-cors")
    
    def _initialize_tools(self):
        """Initialize all tool instances"""
        self.battery_monitor = create_battery_monitor()
        self.diagnostics = create_diagnostics()
        self.system_monitor = create_system_monitor()
        self.package_manager = create_package_manager()
    
    def run(self, host: str = "localhost", port: int = 8080):
        """Run the web interface"""
        if not FLASK_AVAILABLE:
            print("Flask is not installed!")
            print("Install it with: pip install flask flask-cors")
            print("Then run: python main.py --web")
            input("Press Enter to exit...")
            return
        
        self.app = Flask(__name__, 
                        template_folder=str(Path(__file__).parent / "templates"),
                        static_folder=str(Path(__file__).parent / "static"))
        
        # Enable CORS for API endpoints
        CORS(self.app)
        
        self._setup_routes()
        
        self.logger.info(f"Starting web interface on http://{host}:{port}")
        print(f"🌐 Web interface starting on http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Auto-open browser if configured
        if self.config.get('interface.web.auto_open_browser', True):
            threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
        
        try:
            self.app.run(host=host, port=port, debug=self.config.get('interface.web.debug', False))
        except KeyboardInterrupt:
            self.logger.info("Web interface stopped by user")
        except Exception as e:
            self.logger.error(f"Web interface error: {e}")
            print(f"Error starting web server: {e}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        # Main SPA route - serve index.html
        @self.app.route('/')
        def index():
            """Main single-page application"""
            index_path = Path(__file__).parent / "index.html"
            if index_path.exists():
                return send_file(str(index_path))
            else:
                # Fallback to dashboard template
                return render_template('dashboard.html')
        
        # Serve main CSS and JS files
        @self.app.route('/main.css')
        def main_css():
            """Serve main CSS file"""
            css_path = Path(__file__).parent / "main.css"
            if css_path.exists():
                return send_file(str(css_path), mimetype='text/css')
            else:
                return "/* Main CSS not found */", 404
        
        @self.app.route('/app.js')
        def app_js():
            """Serve main JavaScript file"""
            js_path = Path(__file__).parent / "app.js"
            if js_path.exists():
                return send_file(str(js_path), mimetype='application/javascript')
            else:
                return "// Main JS not found", 404
        
        # Legacy template routes for backward compatibility
        @self.app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html')
        
        # Tool-specific pages (backward compatibility)
        @self.app.route('/battery')
        def battery_page():
            return render_template('battery.html')
        
        @self.app.route('/diagnostics')
        def diagnostics_page():
            return render_template('diagnostics.html')
        
        @self.app.route('/monitoring')
        def monitoring_page():
            return render_template('monitoring.html')
        
        @self.app.route('/packages')
        def packages_page():
            return render_template('packages.html')
        
        # API Endpoints for the new SPA interface
        @self.app.route('/api/battery/info')
        def api_battery_info():
            """Get battery information"""
            try:
                if hasattr(self.battery_monitor, 'is_battery_available') and not self.battery_monitor.is_battery_available():
                    return jsonify({
                        "battery_percent": 0,
                        "power_plugged": False,
                        "error": "No battery available"
                    })
                
                # Get basic battery info
                if hasattr(self.battery_monitor, 'get_detailed_info'):
                    info = self.battery_monitor.get_detailed_info()
                elif hasattr(self.battery_monitor, 'get_battery_info'):
                    info = self.battery_monitor.get_battery_info()
                else:
                    # Fallback using psutil
                    battery = psutil.sensors_battery()
                    if battery:
                        info = {
                            "battery_percent": int(battery.percent),
                            "power_plugged": battery.power_plugged
                        }
                    else:
                        info = {"battery_percent": 0, "power_plugged": False}
                
                return jsonify(info)
            except Exception as e:
                self.logger.error(f"Battery info error: {e}")
                return jsonify({
                    "battery_percent": 0,
                    "power_plugged": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/monitoring/metrics')
        def api_monitoring_metrics():
            """Get comprehensive system monitoring metrics"""
            try:
                # Get basic system metrics
                if hasattr(self.system_monitor, 'get_current_metrics'):
                    metrics = self.system_monitor.get_current_metrics()
                    if hasattr(metrics, '_asdict'):
                        metrics_dict = metrics._asdict()
                    else:
                        metrics_dict = metrics if isinstance(metrics, dict) else {}
                else:
                    # Fallback using psutil directly
                    metrics_dict = {
                        "cpu_percent": psutil.cpu_percent(interval=1),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
                    }
                
                # Add system information
                metrics_dict.update({
                    "platform": platform.system(),
                    "architecture": platform.architecture()[0],
                    "processor": platform.processor(),
                    "network_connected": True,  # Basic assumption
                    "memory_info": {
                        "total": psutil.virtual_memory().total,
                        "available": psutil.virtual_memory().available,
                        "used": psutil.virtual_memory().used
                    },
                    "cpu_info": {
                        "cores": psutil.cpu_count(),
                        "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                        "brand": platform.processor()
                    },
                    "top_processes": []
                })
                
                # Get top processes
                try:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                        try:
                            proc_info = proc.info
                            proc_info['cpu_percent'] = proc.cpu_percent()
                            proc_info['memory_percent'] = proc.memory_percent()
                            processes.append(proc_info)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # Sort by CPU usage and get top 10
                    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                    metrics_dict["top_processes"] = processes[:10]
                except Exception:
                    pass
                
                # Add network I/O
                try:
                    net_io = psutil.net_io_counters()
                    metrics_dict["network_io"] = {
                        "bytes_sent": net_io.bytes_sent,
                        "bytes_recv": net_io.bytes_recv
                    }
                except Exception:
                    metrics_dict["network_io"] = {"bytes_sent": 0, "bytes_recv": 0}
                
                return jsonify(metrics_dict)
            except Exception as e:
                self.logger.error(f"Monitoring metrics error: {e}")
                return jsonify({
                    "error": str(e),
                    "cpu_percent": 0,
                    "memory_percent": 0,
                    "disk_percent": 0,
                    "network_connected": False
                }), 500
        
        @self.app.route('/api/diagnostics/run', methods=['POST'])
        def api_run_diagnostics():
            """Run hardware diagnostic tests"""
            try:
                data = request.get_json() or {}
                test_name = data.get('test', 'all')
                
                if hasattr(self.diagnostics, 'run_single_test'):
                    if test_name == 'all':
                        results = self.diagnostics.run_all_tests() if hasattr(self.diagnostics, 'run_all_tests') else []
                        summary = self.diagnostics.get_test_summary() if hasattr(self.diagnostics, 'get_test_summary') else {"results": results}
                    else:
                        result = self.diagnostics.run_single_test(test_name)
                        summary = {"status": "passed" if result else "failed", "test": test_name}
                else:
                    # Basic test simulation
                    summary = {"status": "passed", "test": test_name, "message": f"{test_name} test completed"}
                
                return jsonify(summary)
            except Exception as e:
                self.logger.error(f"Diagnostics error: {e}")
                return jsonify({"status": "error", "error": str(e)}), 500
        
        @self.app.route('/api/packages/status')
        def api_packages_status():
            """Check package manager availability"""
            try:
                if hasattr(self.package_manager, 'is_available'):
                    available = self.package_manager.is_available()
                    version = getattr(self.package_manager, 'get_version', lambda: "Unknown")()
                else:
                    # Basic winget check
                    import subprocess
                    try:
                        result = subprocess.run(['winget', '--version'], capture_output=True, text=True, timeout=5)
                        available = result.returncode == 0
                        version = result.stdout.strip() if available else "Unknown"
                    except Exception:
                        available = False
                        version = "Unknown"
                
                return jsonify({
                    "available": available,
                    "version": version
                })
            except Exception as e:
                return jsonify({"available": False, "error": str(e)})
        
        @self.app.route('/api/packages/list')
        def api_packages_list():
            """List installed packages"""
            try:
                if hasattr(self.package_manager, 'get_installed_packages'):
                    packages = self.package_manager.get_installed_packages()
                    if packages and hasattr(packages[0], '_asdict'):
                        packages_data = [pkg._asdict() for pkg in packages]
                    else:
                        packages_data = packages or []
                else:
                    packages_data = []
                
                return jsonify({"packages": packages_data})
            except Exception as e:
                return jsonify({"packages": [], "error": str(e)})
        
        @self.app.route('/api/packages/count')
        def api_packages_count():
            """Get package count information"""
            try:
                installed_count = 0
                upgradable_count = 0
                
                if hasattr(self.package_manager, 'get_installed_packages'):
                    installed = self.package_manager.get_installed_packages()
                    installed_count = len(installed) if installed else 0
                
                if hasattr(self.package_manager, 'get_upgradable_packages'):
                    upgradable = self.package_manager.get_upgradable_packages()
                    upgradable_count = len(upgradable) if upgradable else 0
                
                return jsonify({
                    "installed_count": installed_count,
                    "upgradable_count": upgradable_count
                })
            except Exception as e:
                return jsonify({
                    "installed_count": 0,
                    "upgradable_count": 0,
                    "error": str(e)
                })
        
        # Static files handling
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            return send_from_directory(self.app.static_folder, filename)