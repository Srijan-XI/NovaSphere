"""
Notification System
Cross-platform desktop notifications for system alerts
"""

import sys
import platform
from typing import Optional
from enum import Enum

class NotificationLevel(Enum):
    """Notification severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class NotificationManager:
    """Manage system notifications across platforms"""
    
    def __init__(self):
        self.enabled = True
        self.platform = platform.system()
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize platform-specific notification backend"""
        if self.platform == "Windows":
            try:
                from win10toast import ToastNotifier
                self.toaster = ToastNotifier()
                self.backend = "win10toast"
            except ImportError:
                self.backend = "print"
        elif self.platform == "Darwin":  # macOS
            self.backend = "osascript"
        elif self.platform == "Linux":
            self.backend = "notify-send"
        else:
            self.backend = "print"
    
    def notify(self, title: str, message: str, level: NotificationLevel = NotificationLevel.INFO, 
               duration: int = 5) -> bool:
        """
        Send a notification
        
        Args:
            title: Notification title
            message: Notification message
            level: Notification severity level
            duration: Display duration in seconds
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            if self.backend == "win10toast":
                return self._notify_windows(title, message, duration)
            elif self.backend == "osascript":
                return self._notify_macos(title, message)
            elif self.backend == "notify-send":
                return self._notify_linux(title, message, level)
            else:
                return self._notify_fallback(title, message, level)
        except Exception as e:
            print(f"Notification error: {e}")
            return False
    
    def _notify_windows(self, title: str, message: str, duration: int) -> bool:
        """Windows notification using win10toast"""
        try:
            self.toaster.show_toast(
                title,
                message,
                duration=duration,
                threaded=True,
                icon_path=None
            )
            return True
        except Exception:
            return False
    
    def _notify_macos(self, title: str, message: str) -> bool:
        """macOS notification using osascript"""
        import subprocess
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    def _notify_linux(self, title: str, message: str, level: NotificationLevel) -> bool:
        """Linux notification using notify-send"""
        import subprocess
        try:
            urgency_map = {
                NotificationLevel.INFO: "low",
                NotificationLevel.WARNING: "normal",
                NotificationLevel.ERROR: "critical",
                NotificationLevel.CRITICAL: "critical"
            }
            urgency = urgency_map.get(level, "normal")
            
            subprocess.run([
                'notify-send',
                '-u', urgency,
                title,
                message
            ], check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    def _notify_fallback(self, title: str, message: str, level: NotificationLevel) -> bool:
        """Fallback notification (print to console)"""
        level_symbols = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨"
        }
        symbol = level_symbols.get(level, "📢")
        print(f"\n{symbol} {title}: {message}\n")
        return True
    
    def battery_alert(self, percentage: int, plugged: bool):
        """Send battery-specific alert"""
        if percentage <= 10 and not plugged:
            self.notify(
                "Critical Battery",
                f"Battery at {percentage}%. Please charge immediately!",
                NotificationLevel.CRITICAL
            )
        elif percentage <= 20 and not plugged:
            self.notify(
                "Low Battery",
                f"Battery at {percentage}%. Consider charging soon.",
                NotificationLevel.WARNING
            )
    
    def cpu_alert(self, usage: float, threshold: float = 90.0):
        """Send CPU usage alert"""
        if usage >= threshold:
            self.notify(
                "High CPU Usage",
                f"CPU usage at {usage:.1f}%. System may be slow.",
                NotificationLevel.WARNING
            )
    
    def memory_alert(self, usage: float, threshold: float = 85.0):
        """Send memory usage alert"""
        if usage >= threshold:
            self.notify(
                "High Memory Usage",
                f"Memory usage at {usage:.1f}%. Close unused applications.",
                NotificationLevel.WARNING
            )
    
    def disk_alert(self, usage: float, threshold: float = 90.0):
        """Send disk usage alert"""
        if usage >= threshold:
            self.notify(
                "Low Disk Space",
                f"Disk usage at {usage:.1f}%. Free up some space.",
                NotificationLevel.WARNING
            )
    
    def diagnostic_complete(self, passed: int, failed: int):
        """Send diagnostic completion notification"""
        if failed > 0:
            self.notify(
                "Diagnostics Complete",
                f"Tests: {passed} passed, {failed} failed",
                NotificationLevel.WARNING
            )
        else:
            self.notify(
                "Diagnostics Complete",
                f"All {passed} tests passed successfully!",
                NotificationLevel.INFO
            )
    
    def enable(self):
        """Enable notifications"""
        self.enabled = True
    
    def disable(self):
        """Disable notifications"""
        self.enabled = False
    
    def toggle(self) -> bool:
        """Toggle notifications on/off"""
        self.enabled = not self.enabled
        return self.enabled


# Global notification manager instance
_notification_manager = None

def get_notification_manager() -> NotificationManager:
    """Get global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
