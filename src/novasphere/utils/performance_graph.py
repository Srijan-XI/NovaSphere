"""
Performance Graph Widget
Matplotlib-based performance charts for Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Optional
import time

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PerformanceGraph:
    """Matplotlib-based performance graph widget"""
    
    def __init__(self, parent, title: str = "Performance", max_points: int = 60):
        """
        Initialize performance graph
        
        Args:
            parent: Parent Tkinter widget
            title: Graph title
            max_points: Maximum data points to display
        """
        self.parent = parent
        self.title = title
        self.max_points = max_points
        
        # Data storage
        self.timestamps: List[float] = []
        self.cpu_data: List[float] = []
        self.memory_data: List[float] = []
        self.disk_data: List[float] = []
        
        self.start_time = time.time()
        
        if MATPLOTLIB_AVAILABLE:
            self._create_matplotlib_graph()
        else:
            self._create_fallback_graph()
    
    def _create_matplotlib_graph(self):
        """Create matplotlib graph"""
        # Create figure
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Initial setup
        self.ax.set_title(self.title)
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Usage (%)')
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.3)
        
        # Create lines
        self.cpu_line, = self.ax.plot([], [], 'r-', label='CPU', linewidth=2)
        self.mem_line, = self.ax.plot([], [], 'b-', label='Memory', linewidth=2)
        self.disk_line, = self.ax.plot([], [], 'g-', label='Disk', linewidth=2)
        
        self.ax.legend(loc='upper right')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_fallback_graph(self):
        """Create simple fallback when matplotlib not available"""
        frame = ttk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = ttk.Label(frame, 
                         text="📊 Performance Graphs\n\n"
                              "Install matplotlib for live graphs:\n"
                              "pip install matplotlib",
                         font=('Arial', 12))
        label.pack(expand=True)
        
        # Simple text display
        self.fallback_text = tk.Text(frame, height=10, width=50)
        self.fallback_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def update_data(self, cpu: float, memory: float, disk: float):
        """
        Update graph with new data
        
        Args:
            cpu: CPU usage percentage
            memory: Memory usage percentage
            disk: Disk usage percentage
        """
        current_time = time.time() - self.start_time
        
        # Add new data
        self.timestamps.append(current_time)
        self.cpu_data.append(cpu)
        self.memory_data.append(memory)
        self.disk_data.append(disk)
        
        # Keep only last max_points
        if len(self.timestamps) > self.max_points:
            self.timestamps = self.timestamps[-self.max_points:]
            self.cpu_data = self.cpu_data[-self.max_points:]
            self.memory_data = self.memory_data[-self.max_points:]
            self.disk_data = self.disk_data[-self.max_points:]
        
        if MATPLOTLIB_AVAILABLE:
            self._update_matplotlib_graph()
        else:
            self._update_fallback_display(cpu, memory, disk)
    
    def _update_matplotlib_graph(self):
        """Update matplotlib graph"""
        # Update line data
        self.cpu_line.set_data(self.timestamps, self.cpu_data)
        self.mem_line.set_data(self.timestamps, self.memory_data)
        self.disk_line.set_data(self.timestamps, self.disk_data)
        
        # Adjust x-axis limits
        if self.timestamps:
            self.ax.set_xlim(max(0, self.timestamps[-1] - self.max_points), 
                            self.timestamps[-1] + 1)
        
        # Redraw
        self.canvas.draw()
    
    def _update_fallback_display(self, cpu: float, memory: float, disk: float):
        """Update fallback text display"""
        self.fallback_text.delete(1.0, tk.END)
        
        text = f"Current Metrics:\n"
        text += f"{'='*40}\n"
        text += f"CPU:    {cpu:6.1f}% {'█' * int(cpu/5)}\n"
        text += f"Memory: {memory:6.1f}% {'█' * int(memory/5)}\n"
        text += f"Disk:   {disk:6.1f}% {'█' * int(disk/5)}\n"
        text += f"\n"
        text += f"Time: {int(self.timestamps[-1] if self.timestamps else 0)}s\n"
        text += f"Samples: {len(self.timestamps)}\n"
        
        if self.cpu_data:
            text += f"\nAverages (last {len(self.cpu_data)} samples):\n"
            text += f"CPU:    {sum(self.cpu_data)/len(self.cpu_data):6.1f}%\n"
            text += f"Memory: {sum(self.memory_data)/len(self.memory_data):6.1f}%\n"
            text += f"Disk:   {sum(self.disk_data)/len(self.disk_data):6.1f}%\n"
        
        self.fallback_text.insert(1.0, text)
    
    def clear(self):
        """Clear all graph data"""
        self.timestamps.clear()
        self.cpu_data.clear()
        self.memory_data.clear()
        self.disk_data.clear()
        self.start_time = time.time()
        
        if MATPLOTLIB_AVAILABLE:
            self._update_matplotlib_graph()


class MultiGraphPanel:
    """Panel containing multiple performance graphs"""
    
    def __init__(self, parent):
        """
        Initialize multi-graph panel
        
        Args:
            parent: Parent Tkinter widget
        """
        self.parent = parent
        self.graphs = {}
        
        if MATPLOTLIB_AVAILABLE:
            self._create_matplotlib_panel()
        else:
            self._create_simple_panel()
    
    def _create_matplotlib_panel(self):
        """Create panel with matplotlib graphs"""
        # Create figure with subplots
        self.figure = Figure(figsize=(10, 8), dpi=100)
        
        # Create 3 subplots
        self.ax_cpu = self.figure.add_subplot(311)
        self.ax_mem = self.figure.add_subplot(312)
        self.ax_disk = self.figure.add_subplot(313)
        
        # Setup CPU graph
        self.ax_cpu.set_title('CPU Usage')
        self.ax_cpu.set_ylabel('Usage (%)')
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.grid(True, alpha=0.3)
        self.cpu_line, = self.ax_cpu.plot([], [], 'r-', linewidth=2)
        
        # Setup Memory graph
        self.ax_mem.set_title('Memory Usage')
        self.ax_mem.set_ylabel('Usage (%)')
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.grid(True, alpha=0.3)
        self.mem_line, = self.ax_mem.plot([], [], 'b-', linewidth=2)
        
        # Setup Disk graph
        self.ax_disk.set_title('Disk Usage')
        self.ax_disk.set_xlabel('Time (seconds)')
        self.ax_disk.set_ylabel('Usage (%)')
        self.ax_disk.set_ylim(0, 100)
        self.ax_disk.grid(True, alpha=0.3)
        self.disk_line, = self.ax_disk.plot([], [], 'g-', linewidth=2)
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Data storage
        self.timestamps: List[float] = []
        self.cpu_data: List[float] = []
        self.memory_data: List[float] = []
        self.disk_data: List[float] = []
        self.start_time = time.time()
        self.max_points = 60
    
    def _create_simple_panel(self):
        """Create simple panel without matplotlib"""
        frame = ttk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Performance Graphs", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(frame, 
                 text="Install matplotlib for live performance graphs:\n"
                      "pip install matplotlib",
                 font=('Arial', 10)).pack(pady=5)
        
        self.simple_display = tk.Text(frame, height=20, width=60)
        self.simple_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def update_data(self, cpu: float, memory: float, disk: float):
        """Update all graphs with new data"""
        if MATPLOTLIB_AVAILABLE:
            current_time = time.time() - self.start_time
            
            self.timestamps.append(current_time)
            self.cpu_data.append(cpu)
            self.memory_data.append(memory)
            self.disk_data.append(disk)
            
            # Keep only recent data
            if len(self.timestamps) > self.max_points:
                self.timestamps = self.timestamps[-self.max_points:]
                self.cpu_data = self.cpu_data[-self.max_points:]
                self.memory_data = self.memory_data[-self.max_points:]
                self.disk_data = self.disk_data[-self.max_points:]
            
            # Update lines
            self.cpu_line.set_data(self.timestamps, self.cpu_data)
            self.mem_line.set_data(self.timestamps, self.memory_data)
            self.disk_line.set_data(self.timestamps, self.disk_data)
            
            # Update x-axis
            if self.timestamps:
                xlim = (max(0, self.timestamps[-1] - self.max_points), 
                       self.timestamps[-1] + 1)
                self.ax_cpu.set_xlim(xlim)
                self.ax_mem.set_xlim(xlim)
                self.ax_disk.set_xlim(xlim)
            
            self.canvas.draw()
        else:
            # Update simple display
            if hasattr(self, 'simple_display'):
                self.simple_display.delete(1.0, tk.END)
                text = "Performance Metrics\n" + "="*50 + "\n\n"
                text += f"CPU Usage:    {cpu:6.1f}%\n"
                text += f"Memory Usage: {memory:6.1f}%\n"
                text += f"Disk Usage:   {disk:6.1f}%\n"
                self.simple_display.insert(1.0, text)


def is_matplotlib_available() -> bool:
    """Check if matplotlib is available"""
    return MATPLOTLIB_AVAILABLE
