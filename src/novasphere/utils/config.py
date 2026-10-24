"""
Common Configuration Management
Handles application-wide configuration settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the NovaSphere"""
    
    def __init__(self):
        self._config: Dict[str, Any] = self._get_default_config()
        self._config_file: Optional[Path] = None
        
        # Try to load default config file
        default_config_path = Path(__file__).parent.parent.parent / "config.json"
        if default_config_path.exists():
            self.load_from_file(str(default_config_path))
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "interface": {
                "default": "cli",
                "cli": {
                    "colors": True,
                    "progress_bars": True
                },
                "gui": {
                    "theme": "default",
                    "window_size": [800, 600],
                    "remember_geometry": True
                },
                "web": {
                    "port": 8080,
                    "host": "localhost",
                    "auto_open_browser": True,
                    "debug": False
                }
            },
            "storage": {
                "mode": "log_file",
                "web_type": "sqlite",
                "web_db_path": "web/backend/data/novasphere_web.db",
                "cli_gui_type": "log_file",
                "cli_gui_log_path": "logs/novasphere_cli_gui.log"
            },
            "tools": {
                "battery": {
                    "update_interval": 5,
                    "show_detailed_info": True,
                    "alert_low_battery": True,
                    "low_battery_threshold": 15
                },
                "diagnostics": {
                    "timeout": 30,
                    "auto_fix": False,
                    "generate_report": True
                },
                "monitoring": {
                    "update_interval": 2,
                    "history_length": 100,
                    "show_graphs": True
                },
                "packages": {
                    "auto_update_check": True,
                    "backup_before_update": True,
                    "log_actions": True
                }
            },
            "system": {
                "log_level": "INFO",
                "log_file": "system_tools.log",
                "temp_directory": None,  # Use system temp if None
                "max_log_size": "10MB"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'interface.gui.theme')"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from JSON file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Merge with default config
            self._merge_config(self._config, user_config)
            self._config_file = path
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def save_to_file(self, file_path: Optional[str] = None) -> None:
        """Save current configuration to JSON file"""
        if file_path:
            path = Path(file_path)
        elif self._config_file:
            path = self._config_file
        else:
            path = Path(__file__).parent.parent.parent / "config.json"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            self._config_file = path
        except Exception as e:
            raise IOError(f"Failed to save configuration: {e}")
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool"""
        return self.get(f"tools.{tool_name}", {})
    
    def get_interface_config(self, interface_name: str) -> Dict[str, Any]:
        """Get configuration for a specific interface"""
        return self.get(f"interface.{interface_name}", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Get the complete configuration as a dictionary"""
        return self._config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = self._get_default_config()
    
    def __str__(self) -> str:
        return f"Config(file={self._config_file})"
    
    def __repr__(self) -> str:
        return f"Config(config={self._config})"