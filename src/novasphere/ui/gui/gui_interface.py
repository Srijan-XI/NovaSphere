"""
Graphical User Interface for NovaSphere: NovaSphere
Tkinter-based GUI implementation with themes, tray, and graphs
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import Optional
from pathlib import Path
from novasphere.utils.config import Config
from novasphere.utils.logger import Logger
from novasphere.utils.log_store import LogDataStore
from novasphere.utils.theme_manager import ThemeManager, ConfigManager
from novasphere.utils.tray_manager import TrayHelper, is_tray_available
from novasphere.utils.performance_graph import PerformanceGraph, is_matplotlib_available
from novasphere.utils.performance_monitor import ResourceMonitor, MetricSnapshot
from novasphere.utils.notifications import get_notification_manager
from novasphere.utils.report_exporter import create_exporter
from novasphere.core.battery.battery_monitor import create_battery_monitor
from novasphere.core.diagnostics.hardware_tests import create_diagnostics
from novasphere.core.monitoring.system_monitor import create_system_monitor

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class GUIInterface:
    """Graphical User Interface implementation using Tkinter"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.data_store = LogDataStore("gui")
        self.root = None
        self.notebook = None
        self._running = False
        self._update_thread = None
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.config_manager = ConfigManager()
        self.notification_manager = get_notification_manager()
        self.resource_monitor = ResourceMonitor()
        self.report_exporter = create_exporter()
        self.tray_helper = None
        
        # Initialize tools
        self.battery_monitor = create_battery_monitor()
        self.diagnostics = create_diagnostics()
        self.system_monitor = create_system_monitor()
        
        # UI elements
        self.battery_widgets = {}
        self.system_widgets = {}
        self.diagnostics_widgets = {}
        self.graph_widget = None
        
        # Notification state
        self.last_battery_alert = 0
        self.last_cpu_alert = 0
    
    def run(self):
        """Run the GUI interface"""
        self.logger.info("Launching Tkinter GUI interface v2.0")
        self.data_store.log_event("startup", {"interface": "gui"})
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("NovaSphere v2.0 - All-in-One System Diagnostic & Monitoring Suite")
        
        # Restore window geometry
        self.config_manager.restore_window_geometry(self.root)
        
        # Apply theme
        self.theme_manager.apply_theme(self.root)
        
        # Set window icon (if available)
        try:
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Create menu bar
        self._create_menu()
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_battery_tab()
        self._create_monitoring_tab()
        self._create_graphs_tab()
        self._create_diagnostics_tab()
        self._create_settings_tab()
        
        # Initialize system tray
        if is_tray_available():
            self.tray_helper = TrayHelper(self.root, "NovaSphere")
            self.tray_helper.tray.register_callback('battery', lambda: self.notebook.select(1))
            self.tray_helper.tray.register_callback('monitor', lambda: self.notebook.select(2))
            self.tray_helper.tray.register_callback('diagnostics', lambda: self.notebook.select(4))
            if self.tray_helper.start_tray():
                self.logger.info("System tray icon started")
        
        # Start update thread
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Run the main loop
        self.root.mainloop()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Report...", command=self._export_report)
        file_menu.add_command(label="Refresh", command=self._refresh_all)
        file_menu.add_separator()
        if is_tray_available():
            file_menu.add_command(label="Minimize to Tray", command=self._minimize_to_tray)
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self._toggle_theme)
        view_menu.add_separator()
        view_menu.add_command(label="Dashboard", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Battery", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Monitoring", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="Graphs", command=lambda: self.notebook.select(3))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Run All Diagnostics", command=self._run_all_diagnostics)
        tools_menu.add_command(label="Clear Graph Data", command=self._clear_graphs)
        tools_menu.add_separator()
        
        # Notifications submenu
        notif_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Notifications", menu=notif_menu)
        notif_menu.add_command(label="Enable Notifications", 
                              command=lambda: self.notification_manager.enable())
        notif_menu.add_command(label="Disable Notifications", 
                              command=lambda: self.notification_manager.disable())
        notif_menu.add_command(label="Test Notification", command=self._test_notification)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_dashboard_tab(self):
        """Create dashboard overview tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dashboard")
        
        # Title
        title = ttk.Label(frame, text="System Overview Dashboard", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Create grid for overview cards
        overview_frame = ttk.Frame(frame)
        overview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # System info card
        sys_card = ttk.LabelFrame(overview_frame, text="System Information", padding=10)
        sys_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.system_widgets['os_label'] = ttk.Label(sys_card, text="OS: Loading...")
        self.system_widgets['os_label'].pack(anchor='w')
        
        self.system_widgets['cpu_label'] = ttk.Label(sys_card, text="CPU: Loading...")
        self.system_widgets['cpu_label'].pack(anchor='w')
        
        self.system_widgets['ram_label'] = ttk.Label(sys_card, text="RAM: Loading...")
        self.system_widgets['ram_label'].pack(anchor='w')
        
        # Quick stats card
        stats_card = ttk.LabelFrame(overview_frame, text="Quick Stats", padding=10)
        stats_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.system_widgets['cpu_usage'] = ttk.Label(stats_card, text="CPU Usage: ---%", font=("Arial", 12))
        self.system_widgets['cpu_usage'].pack(anchor='w', pady=5)
        
        self.system_widgets['mem_usage'] = ttk.Label(stats_card, text="Memory Usage: ---%", font=("Arial", 12))
        self.system_widgets['mem_usage'].pack(anchor='w', pady=5)
        
        self.system_widgets['disk_usage'] = ttk.Label(stats_card, text="Disk Usage: ---%", font=("Arial", 12))
        self.system_widgets['disk_usage'].pack(anchor='w', pady=5)
        
        overview_frame.columnconfigure(0, weight=1)
        overview_frame.columnconfigure(1, weight=1)
    
    def _create_battery_tab(self):
        """Create battery monitoring tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Battery")
        
        title = ttk.Label(frame, text="Battery Monitor", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        info_frame = ttk.LabelFrame(frame, text="Battery Information", padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.battery_widgets['percent'] = ttk.Label(info_frame, text="Battery: ---%", font=("Arial", 24, "bold"))
        self.battery_widgets['percent'].pack(pady=10)
        
        self.battery_widgets['status'] = ttk.Label(info_frame, text="Status: Unknown", font=("Arial", 12))
        self.battery_widgets['status'].pack(pady=5)
        
        self.battery_widgets['time'] = ttk.Label(info_frame, text="Time Remaining: Unknown")
        self.battery_widgets['time'].pack(pady=5)
        
        # Progress bar
        self.battery_widgets['progress'] = ttk.Progressbar(info_frame, length=400, mode='determinate')
        self.battery_widgets['progress'].pack(pady=10)
    
    def _create_monitoring_tab(self):
        """Create system monitoring tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monitoring")
        
        title = ttk.Label(frame, text="System Performance Monitor", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # CPU section
        cpu_frame = ttk.LabelFrame(frame, text="CPU", padding=10)
        cpu_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.system_widgets['cpu_percent'] = ttk.Label(cpu_frame, text="Usage: ---%")
        self.system_widgets['cpu_percent'].pack(side=tk.LEFT, padx=10)
        
        self.system_widgets['cpu_cores'] = ttk.Label(cpu_frame, text="Cores: ---")
        self.system_widgets['cpu_cores'].pack(side=tk.LEFT, padx=10)
        
        # Memory section
        mem_frame = ttk.LabelFrame(frame, text="Memory", padding=10)
        mem_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.system_widgets['mem_percent'] = ttk.Label(mem_frame, text="Usage: ---%")
        self.system_widgets['mem_percent'].pack(side=tk.LEFT, padx=10)
        
        self.system_widgets['mem_total'] = ttk.Label(mem_frame, text="Total: ---")
        self.system_widgets['mem_total'].pack(side=tk.LEFT, padx=10)
        
        # Disk section
        disk_frame = ttk.LabelFrame(frame, text="Disk", padding=10)
        disk_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.system_widgets['disk_percent'] = ttk.Label(disk_frame, text="Usage: ---%")
        self.system_widgets['disk_percent'].pack(side=tk.LEFT, padx=10)
        
        self.system_widgets['disk_total'] = ttk.Label(disk_frame, text="Total: ---")
        self.system_widgets['disk_total'].pack(side=tk.LEFT, padx=10)
    
    def _create_diagnostics_tab(self):
        """Create hardware diagnostics tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Diagnostics")
        
        title = ttk.Label(frame, text="Hardware Diagnostics", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Run All Tests", command=self._run_all_diagnostics).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Results", command=self._clear_diagnostics).pack(side=tk.LEFT, padx=5)
        
        # Results text area
        results_frame = ttk.LabelFrame(frame, text="Test Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.diagnostics_widgets['results'] = tk.Text(results_frame, height=15, width=80, wrap=tk.WORD)
        self.diagnostics_widgets['results'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, command=self.diagnostics_widgets['results'].yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.diagnostics_widgets['results'].config(yscrollcommand=scrollbar.set)
    
    def _create_graphs_tab(self):
        """Create performance graphs tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Graphs")
        
        title = ttk.Label(frame, text="Performance Graphs", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Create graph widget
        self.graph_widget = PerformanceGraph(frame, "System Performance", max_points=60)
        
        # Info label
        if is_matplotlib_available():
            info = ttk.Label(frame, text="Live performance monitoring - Updates every 2 seconds")
        else:
            info = ttk.Label(frame, text="Install matplotlib for live graphs: pip install matplotlib")
        info.pack(pady=5)
    
    def _create_settings_tab(self):
        """Create settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚙️ Settings")
        
        title = ttk.Label(frame, text="Application Settings", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Theme section
        theme_frame = ttk.LabelFrame(frame, text="Appearance", padding=20)
        theme_frame.pack(fill=tk.X, padx=20, pady=10)
        
        current_theme = ttk.Label(theme_frame, text=f"Current Theme: {self.theme_manager.current_theme.title()}")
        current_theme.pack(pady=5)
        
        ttk.Button(theme_frame, text="Toggle Theme (Light/Dark)", 
                  command=self._toggle_theme).pack(pady=5)
        
        # Notifications section
        notif_frame = ttk.LabelFrame(frame, text="Notifications", padding=20)
        notif_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.notif_enabled_var = tk.BooleanVar(value=self.config_manager.get('notifications.enabled', True))
        ttk.Checkbutton(notif_frame, text="Enable Desktop Notifications", 
                       variable=self.notif_enabled_var,
                       command=self._toggle_notifications).pack(anchor='w', pady=2)
        
        ttk.Checkbutton(notif_frame, text="Battery Alerts", 
                       variable=tk.BooleanVar(value=self.config_manager.get('notifications.battery_alerts', True))).pack(anchor='w', pady=2)
        
        ttk.Checkbutton(notif_frame, text="CPU Alerts", 
                       variable=tk.BooleanVar(value=self.config_manager.get('notifications.cpu_alerts', True))).pack(anchor='w', pady=2)
        
        # System Tray section
        if is_tray_available():
            tray_frame = ttk.LabelFrame(frame, text="System Tray", padding=20)
            tray_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Label(tray_frame, text="✅ System tray icon enabled").pack(pady=5)
            ttk.Button(tray_frame, text="Minimize to Tray", 
                      command=self._minimize_to_tray).pack(pady=5)
        
        # Export section
        export_frame = ttk.LabelFrame(frame, text="Data Export", padding=20)
        export_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(export_frame, text="Export System Report", 
                  command=self._export_report).pack(pady=5)
    
    # Menu command implementations
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme(self.root)
        # Update theme label in settings tab
        for widget in self.notebook.winfo_children():
            if self.notebook.tab(widget, 'text') == '⚙️ Settings':
                for frame in widget.winfo_children():
                    if isinstance(frame, ttk.LabelFrame) and 'Appearance' in str(frame.cget('text')):
                        for child in frame.winfo_children():
                            if isinstance(child, ttk.Label) and 'Current Theme' in str(child.cget('text')):
                                child.config(text=f"Current Theme: {self.theme_manager.current_theme.title()}")
        self.logger.info(f"Switched to {self.theme_manager.current_theme} theme")
    
    def _export_report(self):
        """Export system report"""
        from tkinter import filedialog
        import os
        
        # Ask for export format
        export_type = None
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Report")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Select Export Format:", font=("Arial", 12)).pack(pady=20)
        
        def export_format(fmt):
            nonlocal export_type
            export_type = fmt
            dialog.destroy()
        
        ttk.Button(dialog, text="JSON Format", command=lambda: export_format('json')).pack(pady=5)
        ttk.Button(dialog, text="CSV Format", command=lambda: export_format('csv')).pack(pady=5)
        ttk.Button(dialog, text="Text Format", command=lambda: export_format('txt')).pack(pady=5)
        
        dialog.wait_window()
        
        if export_type:
            try:
                filepath = self.report_exporter.export_full_report(export_type)
                messagebox.showinfo("Export Success", f"Report exported to:\n{filepath}")
                self.logger.info(f"Exported report to {filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report:\n{e}")
                self.logger.error(f"Export failed: {e}")
    
    def _minimize_to_tray(self):
        """Minimize window to system tray"""
        if is_tray_available() and self.tray_helper:
            self.tray_helper.hide_window()
            self.logger.info("Minimized to system tray")
        else:
            messagebox.showwarning("Tray Not Available", 
                                 "System tray functionality requires pystray and Pillow.\n"
                                 "Install with: pip install pystray pillow")
    
    def _test_notification(self):
        """Send a test notification"""
        self.notification_manager.notify(
            "NovaSphere Test",
            "This is a test notification from NovaSphere!",
            duration=5
        )
        self.logger.info("Sent test notification")
    
    def _toggle_notifications(self):
        """Toggle notification system"""
        enabled = self.notif_enabled_var.get()
        self.config_manager.set('notifications.enabled', enabled)
        status = "enabled" if enabled else "disabled"
        messagebox.showinfo("Notifications", f"Notifications {status}")
        self.logger.info(f"Notifications {status}")
    
    def _clear_graphs(self):
        """Clear performance graphs"""
        if hasattr(self, 'graph_widget') and self.graph_widget:
            self.graph_widget.clear()
            messagebox.showinfo("Graphs", "Performance graphs cleared")
            self.logger.info("Cleared performance graphs")
    
    def _show_documentation(self):
        """Open documentation"""
        import os
        import webbrowser
        
        doc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'docs', 'ENHANCEMENTS.md')
        
        if os.path.exists(doc_path):
            webbrowser.open(f'file://{os.path.abspath(doc_path)}')
            self.logger.info("Opened documentation")
        else:
            messagebox.showinfo("Documentation", 
                              "Documentation available in docs/ folder:\n"
                              "- ENHANCEMENTS.md\n"
                              "- IMPROVEMENTS_SUMMARY.md\n"
                              "- WEB_INTERFACE_GUIDE.md")
    
    def _update_loop(self):
        """Background update loop with resource monitoring and notifications"""
        while self._running:
            try:
                # Get current metrics
                cpu_percent = psutil.cpu_percent(interval=0.5) if PSUTIL_AVAILABLE else 0
                mem = psutil.virtual_memory() if PSUTIL_AVAILABLE else None
                mem_percent = mem.percent if mem else 0
                disk = psutil.disk_usage('/') if PSUTIL_AVAILABLE else None
                disk_percent = disk.percent if disk else 0
                
                # Update resource monitor with snapshot
                if hasattr(self, 'resource_monitor'):
                    self.resource_monitor.update(cpu_percent, mem_percent, disk_percent)
                
                # Update graphs
                if hasattr(self, 'graph_widget') and self.graph_widget:
                    self.graph_widget.update_data(cpu_percent, mem_percent, disk_percent)
                
                # Update tray tooltip
                if hasattr(self, 'tray_helper') and self.tray_helper:
                    health = self.resource_monitor.get_health_score()
                    self.tray_helper.update_tooltip(
                        f"NovaSphere | CPU: {cpu_percent:.1f}% | RAM: {mem_percent:.1f}% | Health: {health}"
                    )
                
                # Check notification thresholds (if enabled)
                if self.config_manager.get('notifications.enabled', True):
                    # CPU alerts
                    if self.config_manager.get('notifications.cpu_alerts', True) and cpu_percent > 90:
                        self.notification_manager.cpu_alert(cpu_percent)
                    
                    # Memory alerts
                    if mem and mem_percent > 90:
                        self.notification_manager.memory_alert(mem_percent, mem.available)
                    
                    # Disk alerts
                    if disk and disk_percent > 90:
                        self.notification_manager.disk_alert('/', disk_percent, disk.free)
                
                # Update UI
                self._update_system_info()
                self._update_battery_info()
                
            except Exception as e:
                self.logger.error(f"Update error: {e}")
            
            time.sleep(2)
    
    def _update_system_info(self):
        """Update system information"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            import platform
            
            # Dashboard updates
            if 'os_label' in self.system_widgets:
                os_info = f"OS: {platform.system()} {platform.release()}"
                self.system_widgets['os_label'].config(text=os_info)
            
            if 'cpu_label' in self.system_widgets:
                cpu_info = f"CPU: {platform.processor()}"
                self.system_widgets['cpu_label'].config(text=cpu_info)
            
            if 'ram_label' in self.system_widgets:
                total_ram = psutil.virtual_memory().total / (1024**3)
                ram_info = f"RAM: {total_ram:.1f} GB"
                self.system_widgets['ram_label'].config(text=ram_info)
            
            # Quick stats
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
            
            if 'cpu_usage' in self.system_widgets:
                self.system_widgets['cpu_usage'].config(text=f"CPU Usage: {cpu_percent:.1f}%")
            
            if 'mem_usage' in self.system_widgets:
                self.system_widgets['mem_usage'].config(text=f"Memory Usage: {mem_percent:.1f}%")
            
            if 'disk_usage' in self.system_widgets:
                self.system_widgets['disk_usage'].config(text=f"Disk Usage: {disk_percent:.1f}%")
            
            # Monitoring tab
            if 'cpu_percent' in self.system_widgets:
                self.system_widgets['cpu_percent'].config(text=f"Usage: {cpu_percent:.1f}%")
            
            if 'cpu_cores' in self.system_widgets:
                self.system_widgets['cpu_cores'].config(text=f"Cores: {psutil.cpu_count()}")
            
            if 'mem_percent' in self.system_widgets:
                mem = psutil.virtual_memory()
                self.system_widgets['mem_percent'].config(text=f"Usage: {mem.percent:.1f}%")
                self.system_widgets['mem_total'].config(text=f"Total: {mem.total / (1024**3):.1f} GB")
            
            if 'disk_percent' in self.system_widgets:
                disk = psutil.disk_usage('/') if platform.system() != 'Windows' else psutil.disk_usage('C:')
                self.system_widgets['disk_percent'].config(text=f"Usage: {disk.percent:.1f}%")
                self.system_widgets['disk_total'].config(text=f"Total: {disk.total / (1024**3):.1f} GB")
                
        except Exception as e:
            self.logger.error(f"System info update error: {e}")
    
    def _update_battery_info(self):
        """Update battery information"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = int(battery.percent)
                plugged = battery.power_plugged
                
                self.battery_widgets['percent'].config(text=f"Battery: {percent}%")
                self.battery_widgets['progress']['value'] = percent
                
                status = "Charging" if plugged else "Discharging"
                self.battery_widgets['status'].config(text=f"Status: {status}")
                
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    self.battery_widgets['time'].config(text=f"Time Remaining: {hours}h {minutes}m")
                else:
                    self.battery_widgets['time'].config(text="Time Remaining: Calculating...")
            else:
                self.battery_widgets['percent'].config(text="No Battery Detected")
                self.battery_widgets['status'].config(text="Status: N/A")
                self.battery_widgets['time'].config(text="")
                
        except Exception as e:
            self.logger.error(f"Battery info update error: {e}")
    
    def _refresh_all(self):
        """Refresh all data"""
        self._update_system_info()
        self._update_battery_info()
        messagebox.showinfo("Refresh", "All data refreshed successfully!")
    
    def _run_all_diagnostics(self):
        """Run all diagnostic tests"""
        self.diagnostics_widgets['results'].delete(1.0, tk.END)
        self.diagnostics_widgets['results'].insert(tk.END, "Running diagnostics tests...\n\n")
        
        def run_tests():
            try:
                if hasattr(self.diagnostics, 'run_all_tests'):
                    results = self.diagnostics.run_all_tests()
                    output = "Diagnostic Tests Completed:\n\n"
                    for result in results:
                        output += f"{result}\n"
                else:
                    output = "Diagnostics module not fully implemented.\n"
                    output += "Use CLI for full diagnostics: python main.py --cli diagnostics\n"
                
                self.diagnostics_widgets['results'].insert(tk.END, output)
            except Exception as e:
                self.diagnostics_widgets['results'].insert(tk.END, f"Error: {e}\n")
        
        threading.Thread(target=run_tests, daemon=True).start()
    
    def _clear_diagnostics(self):
        """Clear diagnostics results"""
        self.diagnostics_widgets['results'].delete(1.0, tk.END)
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About NovaSphere",
            "All-in-One System Diagnostic & Monitoring Suite\n\n"
            "Version 2.0\n"
            "Author: Srijan-XI\n\n"
            "A comprehensive system monitoring and diagnostic tool."
        )
    
    def _on_closing(self):
        """Handle window close event"""
        # Save window geometry
        if hasattr(self, 'config_manager'):
            self.config_manager.save_window_geometry(self.root)
        
        # Stop update thread
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=1)
        
        # Cleanup tray
        if hasattr(self, 'tray_helper') and self.tray_helper:
            self.tray_helper.cleanup()
        
        self.root.destroy()
