"""
GUI Theme Manager
Provides dark/light theme support for Tkinter GUI
"""

import json
from pathlib import Path
from typing import Dict, Any
import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Manage GUI themes and color schemes"""
    
    THEMES = {
        'light': {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'card_bg': '#ffffff',
            'card_fg': '#000000',
            'accent': '#0078d4',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'button_bg': '#e0e0e0',
            'button_fg': '#000000',
            'hover_bg': '#d0d0d0',
            'border': '#cccccc',
            'text_bg': '#ffffff',
            'text_fg': '#000000',
            'selection': '#0078d4',
        },
        'dark': {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'card_bg': '#2d2d2d',
            'card_fg': '#ffffff',
            'accent': '#3b82f6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'button_bg': '#3d3d3d',
            'button_fg': '#ffffff',
            'hover_bg': '#4d4d4d',
            'border': '#404040',
            'text_bg': '#2d2d2d',
            'text_fg': '#ffffff',
            'selection': '#3b82f6',
        }
    }
    
    def __init__(self, config_file: Path = None):
        """
        Initialize theme manager
        
        Args:
            config_file: Path to theme config file
        """
        self.config_file = config_file or Path.home() / '.nova' / 'theme.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.current_theme = self._load_theme_preference()
        self.colors = self.THEMES[self.current_theme]
    
    def _load_theme_preference(self) -> str:
        """Load saved theme preference"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get('theme', 'light')
        except Exception:
            pass
        return 'light'
    
    def _save_theme_preference(self, theme: str):
        """Save theme preference"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'theme': theme}, f)
        except Exception as e:
            print(f"Failed to save theme: {e}")
    
    def apply_theme(self, root: tk.Tk):
        """
        Apply current theme to root window
        
        Args:
            root: Tkinter root window
        """
        # Configure root window
        root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style(root)
        
        # Frame styles
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['card_bg'], 
                       relief='raised', borderwidth=1)
        
        # Label styles
        style.configure('TLabel', background=self.colors['bg'], 
                       foreground=self.colors['fg'])
        style.configure('Card.TLabel', background=self.colors['card_bg'], 
                       foreground=self.colors['card_fg'])
        style.configure('Title.TLabel', background=self.colors['bg'], 
                       foreground=self.colors['fg'], font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel', background=self.colors['bg'], 
                       foreground=self.colors['fg'], font=('Arial', 12))
        
        # Button styles
        style.configure('TButton', background=self.colors['button_bg'], 
                       foreground=self.colors['button_fg'])
        style.map('TButton',
                 background=[('active', self.colors['hover_bg'])])
        
        # Notebook styles
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['button_bg'], 
                       foreground=self.colors['button_fg'])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', '#ffffff')])
        
        # Progressbar style
        style.configure('TProgressbar', background=self.colors['accent'])
        
        # LabelFrame style
        style.configure('TLabelframe', background=self.colors['bg'], 
                       foreground=self.colors['fg'], borderwidth=2)
        style.configure('TLabelframe.Label', background=self.colors['bg'], 
                       foreground=self.colors['fg'], font=('Arial', 10, 'bold'))
    
    def toggle_theme(self, root: tk.Tk) -> str:
        """
        Toggle between light and dark theme
        
        Args:
            root: Tkinter root window
            
        Returns:
            New theme name
        """
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.colors = self.THEMES[self.current_theme]
        self._save_theme_preference(self.current_theme)
        self.apply_theme(root)
        return self.current_theme
    
    def set_theme(self, theme: str, root: tk.Tk):
        """
        Set specific theme
        
        Args:
            theme: Theme name ('light' or 'dark')
            root: Tkinter root window
        """
        if theme in self.THEMES:
            self.current_theme = theme
            self.colors = self.THEMES[theme]
            self._save_theme_preference(theme)
            self.apply_theme(root)
    
    def get_color(self, color_name: str) -> str:
        """Get color value from current theme"""
        return self.colors.get(color_name, '#000000')
    
    def configure_text_widget(self, text_widget: tk.Text):
        """
        Configure Text widget with theme colors
        
        Args:
            text_widget: tk.Text widget
        """
        text_widget.configure(
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['selection'],
            selectforeground='#ffffff'
        )


class ConfigManager:
    """Manage persistent configuration settings"""
    
    def __init__(self, config_file: Path = None):
        """
        Initialize config manager
        
        Args:
            config_file: Path to config file
        """
        self.config_file = config_file or Path.home() / '.nova' / 'gui_config.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'window': {
                'width': 900,
                'height': 600,
                'x': None,
                'y': None
            },
            'notifications': {
                'enabled': True,
                'battery_alerts': True,
                'cpu_alerts': True,
                'memory_alerts': True
            },
            'monitoring': {
                'update_interval': 2,
                'history_length': 300
            },
            'theme': 'light'
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in loaded:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(loaded[key])
                            else:
                                default_config[key] = loaded[key]
                    return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get config value using dot notation (e.g., 'window.width')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """Set config value using dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def save_window_geometry(self, root: tk.Tk):
        """Save window size and position"""
        geometry = root.geometry()
        # Parse geometry string: widthxheight+x+y
        parts = geometry.replace('x', '+').split('+')
        if len(parts) >= 3:
            self.set('window.width', int(parts[0]))
            self.set('window.height', int(parts[1]))
            self.set('window.x', int(parts[2]))
            if len(parts) >= 4:
                self.set('window.y', int(parts[3]))
    
    def restore_window_geometry(self, root: tk.Tk):
        """Restore saved window size and position"""
        width = self.get('window.width', 900)
        height = self.get('window.height', 600)
        x = self.get('window.x')
        y = self.get('window.y')
        
        if x is not None and y is not None:
            root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            root.geometry(f"{width}x{height}")
