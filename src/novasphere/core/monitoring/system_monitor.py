"""
System Monitoring Core Module
Extracted and refactored from SystemMonitorTool
"""

import subprocess
import platform
import psutil
from typing import Dict, Any, List, Optional, NamedTuple
from dataclasses import dataclass
from novasphere.utils.utils import safe_execute, format_bytes, format_percentage, is_windows, is_linux

class SystemMetrics(NamedTuple):
    """System metrics data structure"""
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_percent: float
    disk_used: int
    disk_total: int
    network_sent: int
    network_recv: int

@dataclass
class MonitoringConfig:
    """System monitoring configuration"""
    update_interval: int = 2
    history_length: int = 100
    include_per_cpu: bool = True
    include_disk_io: bool = True
    include_network: bool = True
    temperature_monitoring: bool = True

class SystemMonitor:
    """Core system monitoring functionality"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self._metrics_history: List[SystemMetrics] = []
        self._network_counters_last = None
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information and usage"""
        try:
            cpu_info = {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count_logical": psutil.cpu_count(),
                "count_physical": psutil.cpu_count(logical=False),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            if self.config.include_per_cpu:
                cpu_info["per_cpu_percent"] = psutil.cpu_percent(percpu=True)
            
            return cpu_info
            
        except Exception as e:
            return {"error": f"Failed to get CPU info: {str(e)}"}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            return {
                "virtual": {
                    "total": virtual_mem.total,
                    "available": virtual_mem.available,
                    "used": virtual_mem.used,
                    "free": virtual_mem.free,
                    "percent": virtual_mem.percent,
                    "total_formatted": format_bytes(virtual_mem.total),
                    "available_formatted": format_bytes(virtual_mem.available),
                    "used_formatted": format_bytes(virtual_mem.used),
                    "percent_formatted": format_percentage(virtual_mem.percent)
                },
                "swap": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "free": swap_mem.free,
                    "percent": swap_mem.percent,
                    "total_formatted": format_bytes(swap_mem.total),
                    "used_formatted": format_bytes(swap_mem.used),
                    "percent_formatted": format_percentage(swap_mem.percent)
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get memory info: {str(e)}"}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        try:
            disk_usage = psutil.disk_usage('/')
            
            result = {
                "usage": {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": (disk_usage.used / disk_usage.total) * 100,
                    "total_formatted": format_bytes(disk_usage.total),
                    "used_formatted": format_bytes(disk_usage.used),
                    "free_formatted": format_bytes(disk_usage.free),
                    "percent_formatted": format_percentage((disk_usage.used / disk_usage.total) * 100)
                },
                "partitions": []
            }
            
            # Get all disk partitions
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    result["partitions"].append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": partition_usage.total,
                        "used": partition_usage.used,
                        "free": partition_usage.free,
                        "percent": (partition_usage.used / partition_usage.total) * 100 if partition_usage.total > 0 else 0,
                        "total_formatted": format_bytes(partition_usage.total),
                        "used_formatted": format_bytes(partition_usage.used),
                        "free_formatted": format_bytes(partition_usage.free)
                    })
                except (PermissionError, OSError):
                    # Skip inaccessible partitions
                    continue
            
            if self.config.include_disk_io:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    result["io"] = {
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count,
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_bytes_formatted": format_bytes(disk_io.read_bytes),
                        "write_bytes_formatted": format_bytes(disk_io.write_bytes)
                    }
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to get disk info: {str(e)}"}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            if not self.config.include_network:
                return {"disabled": True}
            
            network_io = psutil.net_io_counters()
            network_interfaces = psutil.net_if_addrs()
            network_stats = psutil.net_if_stats()
            
            result = {
                "io": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv,
                    "bytes_sent_formatted": format_bytes(network_io.bytes_sent),
                    "bytes_recv_formatted": format_bytes(network_io.bytes_recv)
                },
                "interfaces": {}
            }
            
            # Calculate network speed if we have previous counters
            if self._network_counters_last:
                time_diff = 1  # Assume 1 second interval
                sent_diff = network_io.bytes_sent - self._network_counters_last.bytes_sent
                recv_diff = network_io.bytes_recv - self._network_counters_last.bytes_recv
                
                result["io"]["send_speed"] = sent_diff / time_diff
                result["io"]["recv_speed"] = recv_diff / time_diff
                result["io"]["send_speed_formatted"] = f"{format_bytes(sent_diff)}/s"
                result["io"]["recv_speed_formatted"] = f"{format_bytes(recv_diff)}/s"
            
            self._network_counters_last = network_io
            
            # Get interface details
            for interface_name, addresses in network_interfaces.items():
                stats_data = network_stats.get(interface_name)
                interface_info = {
                    "addresses": [],
                    "stats": stats_data._asdict() if stats_data and hasattr(stats_data, '_asdict') else {}
                }
                
                for addr in addresses:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                result["interfaces"][interface_name] = interface_info
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to get network info: {str(e)}"}
    
    def get_temperature_info(self) -> Dict[str, Any]:
        """Get system temperature information"""
        if not self.config.temperature_monitoring:
            return {"disabled": True}
        
        try:
            if is_windows():
                return self._get_windows_temperature()
            elif is_linux():
                return self._get_linux_temperature()
            else:
                return {"error": "Temperature monitoring not supported on this platform"}
                
        except Exception as e:
            return {"error": f"Failed to get temperature info: {str(e)}"}
    
    def _get_windows_temperature(self) -> Dict[str, Any]:
        """Get temperature information on Windows using WMI"""
        try:
            import wmi
            
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            temperature_infos = w.Sensor()
            
            temperatures = []
            fan_speeds = []
            
            for sensor in temperature_infos:
                if sensor.SensorType == 'Temperature' and sensor.Value:
                    temperatures.append({
                        "name": sensor.Name,
                        "value": float(sensor.Value),
                        "unit": "°C"
                    })
                elif sensor.SensorType == 'Fan' and sensor.Value:
                    fan_speeds.append({
                        "name": sensor.Name,
                        "value": float(sensor.Value),
                        "unit": "RPM"
                    })
            
            return {
                "temperatures": temperatures,
                "fan_speeds": fan_speeds,
                "source": "OpenHardwareMonitor",
                "note": "Requires OpenHardwareMonitor to be running"
            }
            
        except ImportError:
            return {"error": "WMI library not available"}
        except Exception as e:
            return {"error": f"Windows temperature monitoring failed: {str(e)}"}
    
    def _get_linux_temperature(self) -> Dict[str, Any]:
        """Get temperature information on Linux using sensors"""
        try:
            result = subprocess.run(
                ["sensors", "-A", "-j"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                sensors_data = json.loads(result.stdout)
                
                temperatures = []
                fan_speeds = []
                
                for chip_name, chip_data in sensors_data.items():
                    if isinstance(chip_data, dict):
                        for sensor_name, sensor_data in chip_data.items():
                            if isinstance(sensor_data, dict):
                                # Look for temperature sensors
                                for key, value in sensor_data.items():
                                    if "temp" in key.lower() and "input" in key.lower():
                                        temperatures.append({
                                            "name": f"{chip_name}:{sensor_name}",
                                            "value": float(value),
                                            "unit": "°C"
                                        })
                                    elif "fan" in key.lower() and "input" in key.lower():
                                        fan_speeds.append({
                                            "name": f"{chip_name}:{sensor_name}",
                                            "value": float(value),
                                            "unit": "RPM"
                                        })
                
                return {
                    "temperatures": temperatures,
                    "fan_speeds": fan_speeds,
                    "source": "lm-sensors"
                }
            else:
                # Fallback to simple sensors output parsing
                result = subprocess.run(
                    ["sensors"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    temperatures = []
                    fan_speeds = []
                    
                    for line in lines:
                        line = line.strip()
                        if '°C' in line and ('Core' in line or 'temp' in line):
                            # Parse temperature line
                            parts = line.split(':')
                            if len(parts) >= 2:
                                name = parts[0].strip()
                                temp_part = parts[1].split('°C')[0].strip()
                                try:
                                    temp_value = float(temp_part.split()[-1])
                                    temperatures.append({
                                        "name": name,
                                        "value": temp_value,
                                        "unit": "°C"
                                    })
                                except ValueError:
                                    continue
                        elif 'RPM' in line and 'fan' in line.lower():
                            # Parse fan speed line
                            parts = line.split(':')
                            if len(parts) >= 2:
                                name = parts[0].strip()
                                rpm_part = parts[1].split('RPM')[0].strip()
                                try:
                                    rpm_value = float(rpm_part.split()[-1])
                                    fan_speeds.append({
                                        "name": name,
                                        "value": rpm_value,
                                        "unit": "RPM"
                                    })
                                except ValueError:
                                    continue
                    
                    return {
                        "temperatures": temperatures,
                        "fan_speeds": fan_speeds,
                        "source": "lm-sensors (text parsing)"
                    }
                
            return {"error": "sensors command failed"}
            
        except subprocess.TimeoutExpired:
            return {"error": "sensors command timed out"}
        except FileNotFoundError:
            return {"error": "sensors command not found (install lm-sensors)"}
        except Exception as e:
            return {"error": f"Linux temperature monitoring failed: {str(e)}"}
    
    def get_process_info(self, limit: int = 10) -> Dict[str, Any]:
        """Get information about running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "cpu_percent": proc_info['cpu_percent'] or 0,
                        "memory_percent": proc_info['memory_percent'] or 0,
                        "memory_rss": proc_info['memory_info'].rss if proc_info['memory_info'] else 0,
                        "memory_rss_formatted": format_bytes(proc_info['memory_info'].rss) if proc_info['memory_info'] else "0 B"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and limit results
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                "total_processes": len(processes),
                "top_processes": processes[:limit],
                "cpu_intensive": [p for p in processes if p['cpu_percent'] > 5.0][:5],
                "memory_intensive": sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
            }
            
        except Exception as e:
            return {"error": f"Failed to get process info: {str(e)}"}
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get a comprehensive system summary"""
        return {
            "system_info": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "hostname": platform.node(),
                "boot_time": psutil.boot_time()
            },
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "temperature": self.get_temperature_info(),
            "processes": self.get_process_info(5)  # Top 5 processes
        }
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics for monitoring"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                disk_percent=(disk.used / disk.total) * 100,
                disk_used=disk.used,
                disk_total=disk.total,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv
            )
            
            # Add to history
            self._metrics_history.append(metrics)
            if len(self._metrics_history) > self.config.history_length:
                self._metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            # Return empty metrics on error
            return SystemMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def get_metrics_history(self) -> List[SystemMetrics]:
        """Get historical metrics data"""
        return self._metrics_history.copy()
    
    def clear_history(self) -> None:
        """Clear metrics history"""
        self._metrics_history.clear()

# Factory function for easy instantiation
def create_system_monitor(update_interval: int = 2, **kwargs) -> SystemMonitor:
    """Create a system monitor with specified configuration"""
    config = MonitoringConfig(update_interval=update_interval, **kwargs)
    return SystemMonitor(config)