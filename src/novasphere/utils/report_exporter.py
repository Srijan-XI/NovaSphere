"""
Report Export Module
Export system diagnostics and monitoring data to various formats
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import platform

class ReportExporter:
    """Export system reports to multiple formats"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize report exporter
        
        Args:
            output_dir: Directory to save reports (default: ./reports)
        """
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_filename(self, prefix: str, extension: str) -> Path:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{prefix}_{timestamp}.{extension}"
    
    def export_json(self, data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        Export data to JSON format
        
        Args:
            data: Dictionary of data to export
            filename: Optional custom filename
            
        Returns:
            Path to created file
        """
        if filename:
            filepath = self.output_dir / filename
        else:
            filepath = self.generate_filename("system_report", "json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    
    def export_csv(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> Path:
        """
        Export tabular data to CSV format
        
        Args:
            data: List of dictionaries with same keys
            filename: Optional custom filename
            
        Returns:
            Path to created file
        """
        if not data:
            raise ValueError("No data to export")
        
        if filename:
            filepath = self.output_dir / filename
        else:
            filepath = self.generate_filename("system_data", "csv")
        
        keys = data[0].keys()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        
        return filepath
    
    def export_text(self, content: str, filename: Optional[str] = None) -> Path:
        """
        Export formatted text report
        
        Args:
            content: Text content to export
            filename: Optional custom filename
            
        Returns:
            Path to created file
        """
        if filename:
            filepath = self.output_dir / filename
        else:
            filepath = self.generate_filename("system_report", "txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def create_system_report(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive system report
        
        Args:
            system_data: Dictionary containing system metrics
            
        Returns:
            Formatted report dictionary
        """
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "System Diagnostics & Monitoring",
                "version": "2.0"
            },
            "system_information": {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node()
            },
            "metrics": system_data.get("metrics", {}),
            "battery": system_data.get("battery", {}),
            "diagnostics": system_data.get("diagnostics", {}),
            "performance": system_data.get("performance", {})
        }
        
        return report
    
    def create_text_report(self, report_data: Dict[str, Any]) -> str:
        """
        Create formatted text report
        
        Args:
            report_data: Report dictionary
            
        Returns:
            Formatted text string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("SYSTEM DIAGNOSTIC & MONITORING REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Metadata
        meta = report_data.get("report_metadata", {})
        lines.append(f"Generated: {meta.get('generated_at', 'Unknown')}")
        lines.append(f"Report Type: {meta.get('report_type', 'Unknown')}")
        lines.append(f"Version: {meta.get('version', 'Unknown')}")
        lines.append("")
        
        # System Information
        lines.append("-" * 80)
        lines.append("SYSTEM INFORMATION")
        lines.append("-" * 80)
        sys_info = report_data.get("system_information", {})
        for key, value in sys_info.items():
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
        lines.append("")
        
        # Metrics
        if "metrics" in report_data:
            lines.append("-" * 80)
            lines.append("CURRENT METRICS")
            lines.append("-" * 80)
            metrics = report_data["metrics"]
            for key, value in metrics.items():
                if isinstance(value, dict):
                    lines.append(f"\n{key.upper()}:")
                    for k, v in value.items():
                        lines.append(f"  {k}: {v}")
                else:
                    lines.append(f"{key}: {value}")
            lines.append("")
        
        # Battery
        if "battery" in report_data and report_data["battery"]:
            lines.append("-" * 80)
            lines.append("BATTERY STATUS")
            lines.append("-" * 80)
            battery = report_data["battery"]
            for key, value in battery.items():
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
            lines.append("")
        
        # Diagnostics
        if "diagnostics" in report_data and report_data["diagnostics"]:
            lines.append("-" * 80)
            lines.append("DIAGNOSTIC RESULTS")
            lines.append("-" * 80)
            diag = report_data["diagnostics"]
            for key, value in diag.items():
                lines.append(f"{key}: {value}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def export_full_report(self, system_data: Dict[str, Any], 
                          formats: List[str] = None) -> Dict[str, Path]:
        """
        Export full system report in multiple formats
        
        Args:
            system_data: System data dictionary
            formats: List of formats to export ['json', 'txt', 'csv']
            
        Returns:
            Dictionary mapping format to filepath
        """
        if formats is None:
            formats = ['json', 'txt']
        
        report = self.create_system_report(system_data)
        exported_files = {}
        
        if 'json' in formats:
            exported_files['json'] = self.export_json(report)
        
        if 'txt' in formats:
            text_content = self.create_text_report(report)
            exported_files['txt'] = self.export_text(text_content)
        
        if 'csv' in formats and 'performance' in system_data:
            perf_data = system_data['performance']
            if isinstance(perf_data, list) and perf_data:
                exported_files['csv'] = self.export_csv(perf_data)
        
        return exported_files
    
    def export_performance_history(self, history_data: List[Dict[str, Any]]) -> Path:
        """
        Export performance history to CSV
        
        Args:
            history_data: List of performance snapshots
            
        Returns:
            Path to created CSV file
        """
        return self.export_csv(history_data, "performance_history.csv")
    
    def create_summary(self, system_data: Dict[str, Any]) -> str:
        """
        Create quick summary text
        
        Args:
            system_data: System data dictionary
            
        Returns:
            Summary string
        """
        lines = []
        lines.append("SYSTEM SUMMARY")
        lines.append("=" * 50)
        
        # System info
        lines.append(f"OS: {platform.system()} {platform.release()}")
        lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Quick metrics
        if "metrics" in system_data:
            metrics = system_data["metrics"]
            lines.append("Quick Stats:")
            if "cpu_percent" in metrics:
                lines.append(f"  CPU: {metrics['cpu_percent']:.1f}%")
            if "memory_percent" in metrics:
                lines.append(f"  Memory: {metrics['memory_percent']:.1f}%")
            if "disk_percent" in metrics:
                lines.append(f"  Disk: {metrics['disk_percent']:.1f}%")
        
        # Health score
        if "health_score" in system_data:
            score = system_data["health_score"]
            lines.append(f"\nHealth Score: {score}/100")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


def create_exporter(output_dir: Optional[str] = None) -> ReportExporter:
    """
    Factory function to create report exporter
    
    Args:
        output_dir: Optional output directory path
        
    Returns:
        ReportExporter instance
    """
    if output_dir:
        return ReportExporter(Path(output_dir))
    return ReportExporter()
