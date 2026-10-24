"""
Dependency Checker
Validates all required packages and system dependencies
"""

import sys
import subprocess
from typing import List, Dict, Tuple
from pathlib import Path

class DependencyChecker:
    """Check and validate system and Python dependencies"""
    
    REQUIRED_PACKAGES = {
        'psutil': 'psutil>=5.9.0',
        'flask': 'Flask>=2.3.0',
        'flask_cors': 'Flask-CORS>=4.0.0',
        'colorama': 'colorama>=0.4.6',
    }
    
    OPTIONAL_PACKAGES = {
        'cv2': 'opencv-python>=4.5.0',
        'sounddevice': 'sounddevice>=0.4.4',
        'pygame': 'pygame>=2.1.0',
        'bleak': 'bleak>=0.19.0',
        'pynput': 'pynput>=1.7.6',
        'requests': 'requests>=2.28.0',
    }
    
    WINDOWS_PACKAGES = {
        'wmi': 'WMI>=1.5.0',
    }
    
    def __init__(self):
        self.missing_required: List[str] = []
        self.missing_optional: List[str] = []
        self.available_packages: Dict[str, str] = {}
    
    def check_all(self) -> Tuple[bool, str]:
        """
        Check all dependencies
        Returns: (all_required_available, status_message)
        """
        self._check_python_version()
        self._check_packages()
        
        all_ok = len(self.missing_required) == 0
        message = self._generate_report()
        
        return all_ok, message
    
    def _check_python_version(self) -> None:
        """Check if Python version meets requirements"""
        if sys.version_info < (3, 7):
            print("⚠️  Warning: Python 3.7+ is required")
            print(f"   Current version: {sys.version}")
    
    def _check_packages(self) -> None:
        """Check all Python packages"""
        # Check required packages
        for module_name, package_spec in self.REQUIRED_PACKAGES.items():
            if not self._is_package_available(module_name):
                self.missing_required.append(package_spec)
            else:
                self.available_packages[module_name] = package_spec
        
        # Check optional packages
        for module_name, package_spec in self.OPTIONAL_PACKAGES.items():
            if not self._is_package_available(module_name):
                self.missing_optional.append(package_spec)
            else:
                self.available_packages[module_name] = package_spec
        
        # Check Windows-specific packages
        if sys.platform == 'win32':
            for module_name, package_spec in self.WINDOWS_PACKAGES.items():
                if not self._is_package_available(module_name):
                    self.missing_optional.append(package_spec)
                else:
                    self.available_packages[module_name] = package_spec
    
    def _is_package_available(self, module_name: str) -> bool:
        """Check if a package is available"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def _generate_report(self) -> str:
        """Generate dependency status report"""
        lines = []
        
        if self.missing_required:
            lines.append("❌ MISSING REQUIRED PACKAGES:")
            lines.append("   The following packages are required but not installed:")
            lines.append("")
            for package in self.missing_required:
                lines.append(f"   • {package}")
            lines.append("")
            lines.append("   Install with:")
            lines.append(f"   pip install {' '.join(self.missing_required)}")
            lines.append("")
        
        if self.missing_optional:
            lines.append("⚠️  MISSING OPTIONAL PACKAGES:")
            lines.append("   Some features may not work without these packages:")
            lines.append("")
            for package in self.missing_optional:
                lines.append(f"   • {package}")
            lines.append("")
            lines.append("   Install with:")
            lines.append(f"   pip install {' '.join(self.missing_optional)}")
            lines.append("")
        
        if not self.missing_required and not self.missing_optional:
            lines.append("✅ All dependencies installed!")
            lines.append(f"   {len(self.available_packages)} packages available")
        
        return "\n".join(lines)
    
    def install_missing(self, optional: bool = False) -> bool:
        """
        Auto-install missing packages
        Returns: True if successful
        """
        packages_to_install = self.missing_required.copy()
        if optional:
            packages_to_install.extend(self.missing_optional)
        
        if not packages_to_install:
            return True
        
        print(f"\n📦 Installing {len(packages_to_install)} packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade'
            ] + packages_to_install)
            print("✅ Installation completed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def get_package_info(self, module_name: str) -> Dict[str, str]:
        """Get detailed package information"""
        try:
            import importlib.metadata
            dist = importlib.metadata.distribution(module_name)
            return {
                'name': dist.metadata['Name'],
                'version': dist.metadata['Version'],
                'summary': dist.metadata.get('Summary', 'N/A'),
            }
        except Exception:
            return {'name': module_name, 'version': 'Unknown', 'summary': 'N/A'}


def check_dependencies_startup() -> bool:
    """
    Quick startup check for critical dependencies
    Returns: True if all required dependencies available
    """
    checker = DependencyChecker()
    all_ok, message = checker.check_all()
    
    if not all_ok:
        print("\n" + "="*60)
        print(message)
        print("="*60)
        
        response = input("\nWould you like to install missing packages now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if checker.install_missing():
                print("\n✅ Ready to launch!")
                return True
            else:
                print("\n❌ Please install packages manually and try again")
                return False
        else:
            print("\n❌ Cannot continue without required packages")
            return False
    
    return True
