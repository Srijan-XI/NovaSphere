"""
Battery Monitoring Core Module
Extracted and refactored from BatteryMonitoringTool
"""

import psutil
import time
from typing import Dict, Any, Optional, NamedTuple, Callable
from dataclasses import dataclass
from novasphere.utils.utils import safe_execute, format_percentage, format_duration

class BatteryInfo(NamedTuple):
    """Battery information data structure"""
    percentage: float
    is_charging: bool
    time_left: Optional[int]  # seconds, None if unknown
    power_plugged: bool

@dataclass
class BatteryConfig:
    """Battery monitoring configuration"""
    charger_wattage: float = 65.0  # Watts
    battery_capacity: float = 50000.0  # mWh
    update_interval: int = 5  # seconds
    low_battery_threshold: int = 15  # percentage
    alert_on_low_battery: bool = True

class BatteryMonitor:
    """Core battery monitoring functionality"""
    
    def __init__(self, config: Optional[BatteryConfig] = None):
        self.config = config or BatteryConfig()
        self._last_info: Optional[BatteryInfo] = None
        self._callbacks: Dict[str, list] = {
            'update': [],
            'low_battery': [],
            'charging_changed': []
        }
    
    def get_battery_info(self) -> Optional[BatteryInfo]:
        """Get current battery information"""
        def _get_info():
            battery = psutil.sensors_battery()
            if battery is None:
                return None
            
            return BatteryInfo(
                percentage=battery.percent,
                is_charging=battery.power_plugged,
                time_left=battery.secsleft if hasattr(battery, 'secsleft') and battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                power_plugged=battery.power_plugged
            )
        
        info = safe_execute(_get_info)
        
        # Trigger callbacks if info changed
        if info and self._last_info:
            self._check_callbacks(self._last_info, info)
        
        self._last_info = info
        return info
    
    def calculate_charging_time(self, current_percentage: float) -> Optional[float]:
        """Calculate estimated charging time in minutes"""
        if current_percentage >= 100:
            return 0.0
        
        try:
            # Calculate charging rate (% per hour)
            charging_rate = (self.config.charger_wattage * 1000) / self.config.battery_capacity
            
            # Calculate remaining percentage and time
            remaining_percentage = 100 - current_percentage
            time_hours = remaining_percentage / charging_rate
            
            return time_hours * 60  # Convert to minutes
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def calculate_discharge_time(self, current_percentage: float) -> Optional[float]:
        """Estimate battery discharge time (simplified calculation)"""
        if current_percentage <= 0:
            return 0.0
        
        # This is a simplified estimation - in reality, discharge rate varies greatly
        # Based on typical laptop usage patterns
        estimated_hours = (current_percentage / 100) * 8  # Assume 8 hours max battery life
        return estimated_hours * 60  # Convert to minutes
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed battery information"""
        info = self.get_battery_info()
        if not info:
            return {"error": "No battery information available"}
        
        result = {
            "percentage": info.percentage,
            "is_charging": info.is_charging,
            "power_plugged": info.power_plugged,
            "percentage_formatted": format_percentage(info.percentage),
            "status": "Charging" if info.is_charging else "Discharging",
            "low_battery": info.percentage <= self.config.low_battery_threshold
        }
        
        # Add time estimates
        if info.is_charging:
            charging_time = self.calculate_charging_time(info.percentage)
            if charging_time is not None:
                result["estimated_charging_time"] = charging_time
                result["estimated_charging_time_formatted"] = format_duration(charging_time * 60)
                
                # Calculate charging rate
                charging_rate = (self.config.charger_wattage * 1000) / self.config.battery_capacity
                result["charging_rate"] = charging_rate
                result["charging_rate_formatted"] = f"{charging_rate:.2f}% per hour"
        else:
            discharge_time = self.calculate_discharge_time(info.percentage)
            if discharge_time is not None:
                result["estimated_discharge_time"] = discharge_time
                result["estimated_discharge_time_formatted"] = format_duration(discharge_time * 60)
        
        # System time left (if available)
        if info.time_left:
            result["system_time_left"] = info.time_left
            result["system_time_left_formatted"] = format_duration(info.time_left)
        
        return result
    
    def is_battery_available(self) -> bool:
        """Check if battery is available on this system"""
        return safe_execute(lambda: psutil.sensors_battery() is not None, default_return=False)
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for battery events"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def unregister_callback(self, event: str, callback: Callable):
        """Unregister callback for battery events"""
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
    
    def _check_callbacks(self, old_info: BatteryInfo, new_info: BatteryInfo):
        """Check and trigger appropriate callbacks"""
        # Low battery alert
        if (new_info.percentage <= self.config.low_battery_threshold and 
            not new_info.is_charging and 
            self.config.alert_on_low_battery):
            for callback in self._callbacks['low_battery']:
                safe_execute(lambda: callback(new_info))
        
        # Charging status changed
        if old_info.is_charging != new_info.is_charging:
            for callback in self._callbacks['charging_changed']:
                safe_execute(lambda: callback(old_info, new_info))
        
        # General update
        for callback in self._callbacks['update']:
            safe_execute(lambda: callback(new_info))
    
    def start_monitoring(self, callback: Callable, interval: Optional[int] = None):
        """Start continuous monitoring (blocking)"""
        monitor_interval = interval or self.config.update_interval
        
        try:
            while True:
                info = self.get_battery_info()
                if info:
                    detailed_info = self.get_detailed_info()
                    safe_execute(lambda: callback(detailed_info))
                
                time.sleep(monitor_interval)
                
        except KeyboardInterrupt:
            pass
    
    def get_battery_health_info(self) -> Dict[str, Any]:
        """Get battery health information (platform dependent)"""
        result: Dict[str, Any] = {"health_available": False}
        
        # On Windows, we might be able to get more detailed info
        if hasattr(psutil, 'sensors_battery'):
            info = self.get_battery_info()
            if info:
                result.update({
                    "health_available": True,
                    "current_percentage": info.percentage,
                    "charging_cycles": "Unknown",  # Not available via psutil
                    "design_capacity": "Unknown",  # Not available via psutil
                    "current_capacity": "Unknown"  # Not available via psutil
                })
        
        return result

# Factory function for easy instantiation
def create_battery_monitor(charger_wattage: float = 65.0, 
                          battery_capacity: float = 50000.0,
                          **kwargs) -> BatteryMonitor:
    """Create a battery monitor with specified configuration"""
    config = BatteryConfig(
        charger_wattage=charger_wattage,
        battery_capacity=battery_capacity,
        **kwargs
    )
    return BatteryMonitor(config)