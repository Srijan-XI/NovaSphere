"""
Performance Monitoring with Historical Data
Track and visualize system metrics over time
"""

import time
from collections import deque
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MetricSnapshot:
    """Single metric snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int = 0
    network_recv: int = 0
    temperature: Optional[float] = None

class PerformanceHistory:
    """Track system performance history"""
    
    def __init__(self, max_length: int = 300):
        """
        Initialize performance history tracker
        
        Args:
            max_length: Maximum number of data points to keep (default 300 = 5 min at 1s interval)
        """
        self.max_length = max_length
        self.history: deque[MetricSnapshot] = deque(maxlen=max_length)
        self.start_time = time.time()
    
    def add_snapshot(self, snapshot: MetricSnapshot):
        """Add a new metric snapshot"""
        self.history.append(snapshot)
    
    def get_recent(self, count: int = 60) -> List[MetricSnapshot]:
        """Get most recent N snapshots"""
        return list(self.history)[-count:]
    
    def get_all(self) -> List[MetricSnapshot]:
        """Get all historical snapshots"""
        return list(self.history)
    
    def get_average(self, seconds: int = 60) -> Dict[str, float]:
        """Get average metrics over the last N seconds"""
        cutoff_time = time.time() - seconds
        recent = [s for s in self.history if s.timestamp >= cutoff_time]
        
        if not recent:
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0
            }
        
        return {
            'cpu_percent': sum(s.cpu_percent for s in recent) / len(recent),
            'memory_percent': sum(s.memory_percent for s in recent) / len(recent),
            'disk_percent': sum(s.disk_percent for s in recent) / len(recent),
        }
    
    def get_peak(self, seconds: int = 60) -> Dict[str, float]:
        """Get peak metrics over the last N seconds"""
        cutoff_time = time.time() - seconds
        recent = [s for s in self.history if s.timestamp >= cutoff_time]
        
        if not recent:
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0
            }
        
        return {
            'cpu_percent': max(s.cpu_percent for s in recent),
            'memory_percent': max(s.memory_percent for s in recent),
            'disk_percent': max(s.disk_percent for s in recent),
        }
    
    def get_trend(self, metric: str = 'cpu_percent', window: int = 10) -> str:
        """
        Analyze trend for a metric
        
        Returns: 'rising', 'falling', or 'stable'
        """
        if len(self.history) < window * 2:
            return 'stable'
        
        recent = list(self.history)[-window:]
        older = list(self.history)[-window*2:-window]
        
        recent_avg = sum(getattr(s, metric) for s in recent) / len(recent)
        older_avg = sum(getattr(s, metric) for s in older) / len(older)
        
        diff = recent_avg - older_avg
        
        if abs(diff) < 2.0:  # Less than 2% change
            return 'stable'
        elif diff > 0:
            return 'rising'
        else:
            return 'falling'
    
    def get_chart_data(self, metric: str = 'cpu_percent', points: int = 60) -> Tuple[List[float], List[float]]:
        """
        Get data formatted for charting
        
        Returns: (timestamps, values)
        """
        recent = self.get_recent(points)
        
        timestamps = [s.timestamp - self.start_time for s in recent]
        values = [getattr(s, metric) for s in recent]
        
        return timestamps, values
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.start_time = time.time()
    
    def get_summary(self) -> Dict[str, any]:
        """Get comprehensive summary of performance data"""
        if not self.history:
            return {
                'duration': 0,
                'samples': 0,
                'cpu': {'current': 0, 'average': 0, 'peak': 0},
                'memory': {'current': 0, 'average': 0, 'peak': 0},
                'disk': {'current': 0, 'average': 0, 'peak': 0},
            }
        
        latest = self.history[-1]
        avg = self.get_average(seconds=300)  # 5 min average
        peak = self.get_peak(seconds=300)
        
        return {
            'duration': time.time() - self.start_time,
            'samples': len(self.history),
            'cpu': {
                'current': latest.cpu_percent,
                'average': avg['cpu_percent'],
                'peak': peak['cpu_percent'],
                'trend': self.get_trend('cpu_percent')
            },
            'memory': {
                'current': latest.memory_percent,
                'average': avg['memory_percent'],
                'peak': peak['memory_percent'],
                'trend': self.get_trend('memory_percent')
            },
            'disk': {
                'current': latest.disk_percent,
                'average': avg['disk_percent'],
                'peak': peak['disk_percent'],
                'trend': self.get_trend('disk_percent')
            },
        }


class ResourceMonitor:
    """Resource usage monitor with alerts"""
    
    def __init__(self, cpu_threshold: float = 80.0, 
                 memory_threshold: float = 85.0,
                 disk_threshold: float = 90.0):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.history = PerformanceHistory()
        self.alert_callbacks = []
    
    def add_alert_callback(self, callback):
        """Add callback for alerts"""
        self.alert_callbacks.append(callback)
    
    def update(self, cpu: float, memory: float, disk: float, 
               network_sent: int = 0, network_recv: int = 0):
        """Update metrics and check for alerts"""
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
            network_sent=network_sent,
            network_recv=network_recv
        )
        
        self.history.add_snapshot(snapshot)
        self._check_thresholds(snapshot)
    
    def _check_thresholds(self, snapshot: MetricSnapshot):
        """Check if metrics exceed thresholds"""
        alerts = []
        
        if snapshot.cpu_percent >= self.cpu_threshold:
            alerts.append(('cpu', snapshot.cpu_percent, self.cpu_threshold))
        
        if snapshot.memory_percent >= self.memory_threshold:
            alerts.append(('memory', snapshot.memory_percent, self.memory_threshold))
        
        if snapshot.disk_percent >= self.disk_threshold:
            alerts.append(('disk', snapshot.disk_percent, self.disk_threshold))
        
        for callback in self.alert_callbacks:
            for alert in alerts:
                callback(*alert)
    
    def get_health_score(self) -> int:
        """
        Calculate overall system health score (0-100)
        
        100 = Excellent, 80-99 = Good, 60-79 = Fair, <60 = Poor
        """
        if not self.history.history:
            return 100
        
        latest = self.history.history[-1]
        
        # Weight: CPU 40%, Memory 40%, Disk 20%
        cpu_score = max(0, 100 - latest.cpu_percent)
        mem_score = max(0, 100 - latest.memory_percent)
        disk_score = max(0, 100 - latest.disk_percent)
        
        health = int(cpu_score * 0.4 + mem_score * 0.4 + disk_score * 0.2)
        
        return max(0, min(100, health))
    
    def get_health_status(self) -> Tuple[int, str, str]:
        """
        Get health score with status and recommendation
        
        Returns: (score, status, recommendation)
        """
        score = self.get_health_score()
        
        if score >= 90:
            return score, "Excellent", "System is running optimally"
        elif score >= 75:
            return score, "Good", "System performance is good"
        elif score >= 60:
            return score, "Fair", "Consider closing some applications"
        else:
            return score, "Poor", "System is under heavy load"
