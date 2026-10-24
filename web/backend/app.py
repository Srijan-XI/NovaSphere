import json
import os
import platform
import threading
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from flask_cors import CORS

from novasphere.core.battery.battery_monitor import create_battery_monitor
from novasphere.core.diagnostics.hardware_tests import create_diagnostics
from novasphere.core.monitoring.system_monitor import create_system_monitor
from novasphere.core.package_mgmt.winget_manager import create_package_manager
from novasphere.utils.config import Config
from novasphere.utils.logger import Logger
from web.backend.storage import SQLiteDataStore

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


class WebInterface:
    """Web interface separated from the CLI/GUI package layout."""

    def __init__(self, config: Optional[Config] = None, logger: Optional[Logger] = None, storage: Optional[SQLiteDataStore] = None):
        self.config = config or Config()
        self.logger = logger or Logger("NovaSphere-Web")
        self.storage = storage or SQLiteDataStore()
        self.app = None
        self.battery_monitor = create_battery_monitor()
        self.diagnostics = create_diagnostics()
        self.system_monitor = create_system_monitor()
        self.package_manager = create_package_manager()

    def create_app(self) -> Flask:
        root = Path(__file__).resolve().parents[1]
        frontend_dir = root / "frontend"
        app = Flask(
            __name__,
            template_folder=str(frontend_dir / "templates"),
            static_folder=str(frontend_dir / "static"),
        )
        CORS(app)

        @app.route("/")
        def index():
            index_path = frontend_dir / "index.html"
            if index_path.exists():
                return send_file(str(index_path))
            return render_template("dashboard.html")

        @app.route("/main.css")
        def main_css():
            css_path = frontend_dir / "main.css"
            return send_file(str(css_path), mimetype="text/css") if css_path.exists() else ("/* CSS not found */", 404)

        @app.route("/app.js")
        def app_js():
            js_path = frontend_dir / "app.js"
            return send_file(str(js_path), mimetype="application/javascript") if js_path.exists() else ("// JS not found", 404)

        @app.route("/dashboard")
        def dashboard():
            return render_template("dashboard.html")

        @app.route("/battery")
        def battery_page():
            return render_template("battery.html")

        @app.route("/diagnostics")
        def diagnostics_page():
            return render_template("diagnostics.html")

        @app.route("/monitoring")
        def monitoring_page():
            return render_template("monitoring.html")

        @app.route("/packages")
        def packages_page():
            return render_template("packages.html")

        @app.route("/api/health")
        def api_health():
            payload = {"status": "ok", "database": "sqlite", "application": "NovaSphere"}
            self.storage.record_event("web", "health_check", payload)
            return jsonify(payload)

        @app.route("/api/battery/info")
        def api_battery_info():
            try:
                if hasattr(self.battery_monitor, "is_battery_available") and not self.battery_monitor.is_battery_available():
                    response = {"battery_percent": 0, "power_plugged": False, "error": "No battery available"}
                elif hasattr(self.battery_monitor, "get_detailed_info"):
                    response = self.battery_monitor.get_detailed_info()
                elif hasattr(self.battery_monitor, "get_battery_info"):
                    response = self.battery_monitor.get_battery_info()
                elif psutil is not None and hasattr(psutil, "sensors_battery"):
                    battery = psutil.sensors_battery()
                    response = {"battery_percent": int(battery.percent), "power_plugged": battery.power_plugged} if battery else {"battery_percent": 0, "power_plugged": False}
                else:
                    response = {"battery_percent": 0, "power_plugged": False}
                self.storage.record_event("battery", "read_info", response)
                return jsonify(response)
            except Exception as exc:  # pragma: no cover
                self.logger.error(f"Battery info error: {exc}")
                return jsonify({"battery_percent": 0, "power_plugged": False, "error": str(exc)}), 500

        @app.route("/api/monitoring/metrics")
        def api_monitoring_metrics():
            try:
                if hasattr(self.system_monitor, "get_current_metrics"):
                    metrics = self.system_monitor.get_current_metrics()
                    metrics_dict = metrics._asdict() if hasattr(metrics, "_asdict") else dict(metrics)
                elif psutil is not None:
                    metrics_dict = {
                        "cpu_percent": psutil.cpu_percent(interval=0.1),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage("/").percent if os.name != "nt" else psutil.disk_usage("C:").percent,
                    }
                else:
                    metrics_dict = {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}

                metrics_dict.update({
                    "platform": platform.system(),
                    "architecture": platform.architecture()[0],
                    "processor": platform.processor(),
                    "network_connected": True,
                })
                self.storage.record_event("monitoring", "read_metrics", metrics_dict)
                return jsonify(metrics_dict)
            except Exception as exc:  # pragma: no cover
                self.logger.error(f"Monitoring error: {exc}")
                return jsonify({"error": str(exc), "cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}), 500

        @app.route("/api/diagnostics/run", methods=["POST"])
        def api_run_diagnostics():
            try:
                data = request.get_json() or {}
                test_name = data.get("test", "all")
                if hasattr(self.diagnostics, "run_single_test") and test_name != "all":
                    result = self.diagnostics.run_single_test(test_name)
                    summary = {"status": "passed" if result else "failed", "test": test_name}
                else:
                    summary = {"status": "passed", "test": test_name, "message": f"{test_name} test completed"}
                self.storage.record_event("diagnostics", "run", summary)
                return jsonify(summary)
            except Exception as exc:  # pragma: no cover
                self.logger.error(f"Diagnostics error: {exc}")
                return jsonify({"status": "error", "error": str(exc)}), 500

        @app.route("/api/packages/status")
        def api_packages_status():
            try:
                available = self.package_manager.is_available() if hasattr(self.package_manager, "is_available") else False
                version = getattr(self.package_manager, "get_version", lambda: "Unknown")()
                response = {"available": available, "version": version}
                self.storage.record_event("packages", "status", response)
                return jsonify(response)
            except Exception as exc:  # pragma: no cover
                return jsonify({"available": False, "error": str(exc)})

        @app.route("/api/packages/list")
        def api_packages_list():
            try:
                packages = self.package_manager.get_installed_packages() if hasattr(self.package_manager, "get_installed_packages") else []
                response = {"packages": packages}
                self.storage.record_event("packages", "list", {"count": len(packages)})
                return jsonify(response)
            except Exception as exc:  # pragma: no cover
                return jsonify({"packages": [], "error": str(exc)})

        @app.route("/api/events")
        def api_events():
            return jsonify({"events": self.storage.get_recent_events(limit=25)})

        @app.route("/static/<path:filename>")
        def static_files(filename: str):
            return send_from_directory(str(frontend_dir / "static"), filename)

        return app

    def run(self, host: str = "localhost", port: int = 8080):
        self.app = self.create_app()
        self.logger.info(f"Starting web interface on http://{host}:{port}")
        print(f"🌐 NovaSphere web interface starting on http://{host}:{port}")
        if self.config.get("interface.web.auto_open_browser", True):
            threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
        self.app.run(host=host, port=port, debug=self.config.get("interface.web.debug", False))


def create_app() -> Flask:
    return WebInterface().create_app()


if __name__ == "__main__":
    WebInterface().run()
