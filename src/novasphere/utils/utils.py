"""
Common Utilities and Helper Functions
Shared utilities used across all system tools
"""

import platform
import sys
import time
import functools
from typing import Dict, Any, Callable, Optional
from pathlib import Path

def get_system_info() -> Dict[str, str]:
    """Get basic system information"""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'python_version': sys.version.split()[0],
        'hostname': platform.node()
    }

def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system().lower() == 'windows'

def is_linux() -> bool:
    """Check if running on Linux"""
    return platform.system().lower() == 'linux'

def is_macos() -> bool:
    """Check if running on macOS"""
    return platform.system().lower() == 'darwin'

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format"""
    value = float(bytes_value)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format value as percentage"""
    return f"{value:.{decimal_places}f}%"

def format_duration(seconds: float) -> str:
    """Format seconds into human readable duration"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def safe_execute(func: Callable, default_return: Any = None, 
                 suppress_exceptions: tuple = (Exception,)) -> Any:
    """Safely execute a function with exception handling"""
    try:
        return func()
    except suppress_exceptions:
        return default_return

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    
            # All attempts failed, raise the last exception or a default one
            if last_exception:
                raise last_exception
            else:
                raise Exception("Function failed after all retries")
        
        return wrapper
    return decorator

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a text-based progress bar"""
    if total == 0:
        return "[" + "=" * width + "] 100%"
    
    progress = current / total
    filled_width = int(width * progress)
    bar = "=" * filled_width + "-" * (width - filled_width)
    percentage = progress * 100
    
    return f"[{bar}] {percentage:.1f}%"

def validate_file_path(path: str, must_exist: bool = True) -> bool:
    """Validate if a file path is valid"""
    try:
        file_path = Path(path)
        if must_exist:
            return file_path.exists() and file_path.is_file()
        else:
            # Check if parent directory exists
            return file_path.parent.exists()
    except Exception:
        return False

def validate_directory_path(path: str, must_exist: bool = True) -> bool:
    """Validate if a directory path is valid"""
    try:
        dir_path = Path(path)
        if must_exist:
            return dir_path.exists() and dir_path.is_dir()
        else:
            # Check if parent directory exists
            return dir_path.parent.exists()
    except Exception:
        return False

def get_temp_directory() -> Path:
    """Get system temporary directory"""
    import tempfile
    return Path(tempfile.gettempdir())

def ensure_directory_exists(path: str) -> Path:
    """Ensure directory exists, create if it doesn't"""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

class Timer:
    """Simple timer context manager"""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        if self.start_time is not None:
            duration = self.end_time - self.start_time
            print(f"{self.description} completed in {format_duration(duration)}")
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string if it exceeds max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_size_string(size_str: str) -> int:
    """Parse size string like '10MB', '1.5GB' to bytes"""
    size_str = size_str.upper().strip()
    
    # Extract number and unit
    import re
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    value, unit = match.groups()
    value = float(value)
    
    # Convert to bytes
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    
    # Handle case where unit might be just 'K', 'M', 'G', 'T'
    if unit in ['K', 'M', 'G', 'T']:
        unit += 'B'
    
    multiplier = multipliers.get(unit, 1)
    return int(value * multiplier)