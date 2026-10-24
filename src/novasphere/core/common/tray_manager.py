"""
System Tray Manager
Provides system tray icon and background monitoring
"""

import sys
import threading
from pathlib import Path
from typing import Optional, Callable, TYPE_CHECKING

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    if TYPE_CHECKING:
        from PIL import Image
    else:
        class Image:  # type: ignore
            class Image: pass


class SystemTrayManager:
    """Manage system tray icon and menu"""
    
    def __init__(self, app_name: str = "NovaSphere"):
        """
        Initialize system tray manager
        
        Args:
            app_name: Application name for tray
        """
        self.app_name = app_name
        self.icon = None
        self.callbacks = {}
        self._running = False
        
        if not PYSTRAY_AVAILABLE:
            print("⚠️  pystray not available. Install with: pip install pystray pillow")
    
    def create_icon_image(self) -> Image.Image:
        """Create a simple icon image"""
        # Create a 64x64 image with a simple design
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'white')
        dc = ImageDraw.Draw(image)
        
        # Draw a simple monitoring icon (graph-like)
        dc.rectangle([0, 0, width-1, height-1], outline='black', width=2)
        
        # Draw simple bars representing monitoring
        bar_width = 8
        bars = [
            (10, 40, 'blue'),
            (22, 30, 'blue'),
            (34, 35, 'blue'),
            (46, 25, 'blue'),
        ]
        
        for x, h, color in bars:
            dc.rectangle([x, height-h, x+bar_width, height-5], fill=color, outline='black')
        
        return image
    
    def register_callback(self, action: str, callback: Callable):
        """
        Register callback for tray actions
        
        Args:
            action: Action name (show, hide, exit, etc.)
            callback: Function to call
        """
        self.callbacks[action] = callback
    
    def show_window(self):
        """Show main window"""
        if 'show' in self.callbacks:
            self.callbacks['show']()
    
    def hide_window(self):
        """Hide main window"""
        if 'hide' in self.callbacks:
            self.callbacks['hide']()
    
    def exit_app(self):
        """Exit application"""
        if 'exit' in self.callbacks:
            self.callbacks['exit']()
        self.stop()
    
    def create_menu(self):
        """Create tray menu"""
        if not PYSTRAY_AVAILABLE:
            return None
        
        return pystray.Menu(
            pystray.MenuItem('Show Window', self.show_window, default=True),
            pystray.MenuItem('Hide Window', self.hide_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Battery Status', 
                           lambda: self.callbacks.get('battery', lambda: None)()),
            pystray.MenuItem('System Monitor', 
                           lambda: self.callbacks.get('monitor', lambda: None)()),
            pystray.MenuItem('Diagnostics', 
                           lambda: self.callbacks.get('diagnostics', lambda: None)()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', self.exit_app)
        )
    
    def start(self):
        """Start system tray icon"""
        if not PYSTRAY_AVAILABLE:
            print("Cannot start system tray: pystray not installed")
            return False
        
        try:
            icon_image = self.create_icon_image()
            menu = self.create_menu()
            
            self.icon = pystray.Icon(
                self.app_name,
                icon_image,
                self.app_name,
                menu
            )
            
            self._running = True
            
            # Run in separate thread
            tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            tray_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to start system tray: {e}")
            return False
    
    def stop(self):
        """Stop system tray icon"""
        self._running = False
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
    
    def update_tooltip(self, text: str):
        """Update tray icon tooltip"""
        if self.icon:
            self.icon.title = text
    
    def notify(self, message: str, title: str = None):
        """
        Show notification from tray
        
        Args:
            message: Notification message
            title: Optional title (defaults to app name)
        """
        if self.icon and PYSTRAY_AVAILABLE:
            try:
                self.icon.notify(message, title or self.app_name)
            except Exception as e:
                print(f"Notification failed: {e}")


class TrayHelper:
    """Helper class for integrating tray with GUI"""
    
    def __init__(self, root, app_name: str = "NovaSphere"):
        """
        Initialize tray helper
        
        Args:
            root: Tkinter root window
            app_name: Application name
        """
        self.root = root
        self.tray = SystemTrayManager(app_name)
        self.minimized = False
        
        # Register callbacks
        self.tray.register_callback('show', self.show_window)
        self.tray.register_callback('hide', self.hide_window)
        self.tray.register_callback('exit', self.exit_app)
    
    def show_window(self):
        """Show and restore window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.minimized = False
    
    def hide_window(self):
        """Hide window to tray"""
        self.root.withdraw()
        self.minimized = True
    
    def exit_app(self):
        """Exit application"""
        self.tray.stop()
        self.root.quit()
    
    def on_window_minimize(self, event=None):
        """Handle window minimize event"""
        if PYSTRAY_AVAILABLE:
            self.hide_window()
            return "break"  # Prevent default minimize
    
    def start_tray(self):
        """Start system tray"""
        success = self.tray.start()
        if success:
            # Bind window close to minimize to tray
            self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        return success
    
    def update_status(self, cpu: float = None, memory: float = None, battery: int = None):
        """
        Update tray tooltip with system status
        
        Args:
            cpu: CPU usage percentage
            memory: Memory usage percentage
            battery: Battery percentage
        """
        parts = [self.tray.app_name]
        
        if cpu is not None:
            parts.append(f"CPU: {cpu:.1f}%")
        if memory is not None:
            parts.append(f"RAM: {memory:.1f}%")
        if battery is not None:
            parts.append(f"Battery: {battery}%")
        
        tooltip = " | ".join(parts)
        self.tray.update_tooltip(tooltip)


def is_tray_available() -> bool:
    """Check if system tray is available"""
    return PYSTRAY_AVAILABLE
