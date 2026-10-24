"""FastAPI web application backed by NovaSphere's shared core services."""

import os
import platform
import threading
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from novasphere.core.battery.battery_monitor import create_battery_monitor
from novasphere.core.diagnostics.hardware_tests import create_diagnostics
from novasphere.core.monitoring.system_monitor import create_system_monitor
from novasphere.utils.config import Config
from novasphere.utils.logger import Logger
from web.backend.storage import SQLiteDataStore

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


class DiagnosticRequest(BaseModel):
    test: str = "all"


class WebInterface:
    """Serve the web UI and API using FastAPI and shared NovaSphere services."""

    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None,
        storage: Optional[SQLiteDataStore] = None,
    ):
        self.config = config or Config()
        self.logger = logger or Logger("NovaSphere-Web")
        self.storage = storage or SQLiteDataStore()
        self.battery_monitor = create_battery_monitor()
        self.diagnostics = create_diagnostics()
        self.system_monitor = create_system_monitor()
        self.app = self.create_app()

    def _record_event(self, category: str, action: str, payload: Dict[str, Any]) -> None:
        """Persist telemetry without making API responses depend on SQLite."""
        try:
            self.storage.record_event(category, action, payload)
        except Exception as exc:  # pragma: no cover
            self.logger.warning(f"Could not record {category}/{action} event: {exc}")

    def create_app(self) -> FastAPI:
        frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
        templates_dir = frontend_dir / "templates"
        app = FastAPI(title="NovaSphere API", version="2.0.0")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/", include_in_schema=False)
        def index():
            return FileResponse(frontend_dir / "index.html")

        @app.get("/main.css", include_in_schema=False)
        def main_css():
            css_path = frontend_dir / "main.css"
            return FileResponse(css_path, media_type="text/css") if css_path.exists() else JSONResponse({"error": "CSS not found"}, status_code=404)

        @app.get("/app.js", include_in_schema=False)
        def app_js():
            js_path = frontend_dir / "app.js"
            return FileResponse(js_path, media_type="application/javascript") if js_path.exists() else JSONResponse({"error": "JavaScript not found"}, status_code=404)

        def make_page_handler(page_name: str):
            def serve_page():
                return FileResponse(templates_dir / f"{page_name}.html")
            return serve_page

        for page in ("dashboard", "battery", "diagnostics", "monitoring"):
            app.add_api_route(
                f"/{page}",
                make_page_handler(page),
                methods=["GET"],
                include_in_schema=False,
                name=f"{page}_page",
            )

        @app.get("/api/health")
        def api_health():
            payload = {"status": "ok", "database": "sqlite", "application": "NovaSphere"}
            self._record_event("web", "health_check", payload)
            return payload

        @app.get("/api/battery/info")
        def api_battery_info():
            try:
                if hasattr(self.battery_monitor, "is_battery_available") and not self.battery_monitor.is_battery_available():
                    response = {"battery_percent": 0, "power_plugged": False, "available": False, "error": "No battery available"}
                elif hasattr(self.battery_monitor, "get_detailed_info"):
                    response = self.battery_monitor.get_detailed_info()
                elif hasattr(self.battery_monitor, "get_battery_info"):
                    response = _json_safe(self.battery_monitor.get_battery_info())
                elif psutil is not None:
                    battery = psutil.sensors_battery()
                    response = (
                        {"battery_percent": battery.percent, "power_plugged": battery.power_plugged, "available": True}
                        if battery
                        else {"battery_percent": 0, "power_plugged": False, "available": False, "error": "No battery available"}
                    )
                else:
                    response = {"battery_percent": 0, "power_plugged": False, "available": False, "error": "Battery service unavailable"}

                response = _json_safe(response)
                if isinstance(response, dict):
                    percent = response.get("battery_percent", response.get("percentage", 0))
                    response["battery_percent"] = percent
                    response.setdefault("percentage", percent)
                    response["power_plugged"] = response.get(
                        "power_plugged", response.get("is_charging", False)
                    )
                    response["available"] = response.get(
                        "available", "error" not in response
                    )
                else:
                    response = {"battery_percent": 0, "percentage": 0, "power_plugged": False, "available": False}
                self._record_event("battery", "read_info", response)
                return response
            except Exception as exc:  # pragma: no cover
                self.logger.error(f"Battery info error: {exc}")
                return JSONResponse(
                    {"battery_percent": 0, "percentage": 0, "power_plugged": False, "available": False, "error": str(exc)},
                    status_code=500,
                )

        @app.get("/api/monitoring/metrics")
        def api_monitoring_metrics():
            try:
                metrics = self.system_monitor.get_current_metrics()
                metrics_dict = metrics._asdict() if hasattr(metrics, "_asdict") else dict(metrics)
                memory = psutil.virtual_memory() if psutil is not None else None
                disk_path = (os.getenv("SystemDrive", "C:") + "\\") if os.name == "nt" else "/"
                disk = psutil.disk_usage(disk_path) if psutil is not None else None
                network = psutil.net_io_counters() if psutil is not None else None
                frequency = psutil.cpu_freq() if psutil is not None else None
                process_data = self.system_monitor.get_process_info(10)
                top_processes = process_data.get("top_processes", [])
                for process in top_processes:
                    process.setdefault("memory_info", process.get("memory_rss", 0))

                if memory:
                    metrics_dict.update({
                        "memory_percent": memory.percent,
                        "memory_info": {"total": memory.total, "available": memory.available, "used": memory.used},
                    })
                if disk:
                    metrics_dict.update({"disk_percent": disk.percent, "disk_used": disk.used, "disk_total": disk.total})
                if network:
                    metrics_dict["network_io"] = {"bytes_sent": network.bytes_sent, "bytes_recv": network.bytes_recv}
                    metrics_dict["network_sent"] = network.bytes_sent
                    metrics_dict["network_recv"] = network.bytes_recv

                metrics_dict.update({
                    "platform": platform.system(),
                    "architecture": platform.architecture()[0],
                    "processor": platform.processor(),
                    "hostname": platform.node(),
                    "boot_time": psutil.boot_time() if psutil is not None else None,
                    "network_connected": _network_connected(),
                    "total_processes": process_data.get("total_processes", 0),
                    "cpu_intensive": process_data.get("cpu_intensive", []),
                    "memory_intensive": process_data.get("memory_intensive", []),
                    "cpu_info": {
                        "cores": psutil.cpu_count() if psutil else None,
                        "frequency": frequency.current / 1000 if frequency and frequency.current else None,
                        "brand": platform.processor(),
                    },
                    "top_processes": top_processes,
                })
                payload = _json_safe(metrics_dict)
                self._record_event("monitoring", "read_metrics", payload)
                return payload
            except Exception as exc:  # pragma: no cover
                self.logger.error(f"Monitoring error: {exc}")
                return JSONResponse(
                    {"error": str(exc), "cpu_percent": 0, "memory_percent": 0, "disk_percent": 0},
                    status_code=500,
                )

        @app.post("/api/diagnostics/run")
        def api_run_diagnostics(data: DiagnosticRequest):
            try:
                test_name = data.test.lower().strip()
                if test_name == "all":
                    self.diagnostics.run_all_tests()
                    summary = self.diagnostics.get_test_summary()
                    summary["status"] = (
                        "completed"
                        if summary.get("total_tests", 0) > 0
                        and summary.get("failed", 0) == 0
                        and summary.get("errors", 0) == 0
                        else "completed_with_issues"
                    )
                else:
                    result = self.diagnostics.run_single_test(test_name)
                    if result is None:
                        return JSONResponse(
                            {"status": "error", "test": test_name, "message": "Diagnostic test did not return a result"},
                            status_code=500,
                        )
                    summary = {
                        "test": result.test_name,
                        "status": result.status.value,
                        "message": result.message,
                        "details": _json_safe(result.details),
                        "duration": result.duration,
                    }
                self._record_event("diagnostics", "run", summary)
                return _json_safe(summary)
            except Exception as exc:  # pragma: no cover
                self.logger.error(f"Diagnostics error: {exc}")
                return JSONResponse({"status": "error", "error": str(exc)}, status_code=500)

        @app.get("/api/events")
        def api_events():
            try:
                return {"events": self.storage.get_recent_events(limit=25)}
            except Exception as exc:  # pragma: no cover
                self.logger.warning(f"Could not read recent events: {exc}")
                return {"events": []}

        app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")
        return app

    def run(self, host: str = "localhost", port: int = 8080) -> None:
        self.logger.info(f"Starting web interface on http://{host}:{port}")
        print(f"🌐 NovaSphere web interface starting on http://{host}:{port}")
        if self.config.get("interface.web.auto_open_browser", True):
            threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
        uvicorn.run(self.app, host=host, port=port, log_level="debug" if self.config.get("interface.web.debug", False) else "info")


def create_app() -> FastAPI:
    return WebInterface().app


def _json_safe(value: Any) -> Any:
    """Convert core service values into JSON-compatible data."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "_asdict"):
        return _json_safe(value._asdict())
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return _json_safe(value.__dict__)
    return value


def _network_connected() -> bool:
    if psutil is None:
        return False
    try:
        return any(
            stats.isup and name.lower() not in ("lo", "loopback")
            for name, stats in psutil.net_if_stats().items()
        )
    except Exception:
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the NovaSphere FastAPI web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    arguments = parser.parse_args()
    WebInterface().run(host=arguments.host, port=arguments.port)
