"""
Package Management Core Module
Extracted and refactored from winget_cli_tool
Windows-specific package management using winget
"""

import subprocess
import json
import platform
from typing import Dict, Any, List, Optional, NamedTuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from novasphere.utils.utils import safe_execute, is_windows
from novasphere.utils.logger import get_logger

class PackageInfo(NamedTuple):
    """Package information data structure"""
    id: str
    name: str
    version: str
    available_version: Optional[str] = None
    source: str = "winget"

class PackageOperation(NamedTuple):
    """Package operation result"""
    package_id: str
    operation: str  # install, uninstall, upgrade
    success: bool
    message: str
    timestamp: datetime

@dataclass
class PackageConfig:
    """Package management configuration"""
    auto_update_check: bool = True
    backup_before_update: bool = True
    log_actions: bool = True
    timeout: int = 300  # 5 minutes
    silent_install: bool = True

class PackageManager:
    """Core package management functionality"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        self.config = config or PackageConfig()
        self.logger = get_logger("PackageManager")
        self._log_file = Path("package_operations.log")
        
        if not is_windows():
            self.logger.warning("Package manager is designed for Windows only")
    
    def is_available(self) -> bool:
        """Check if winget is available on the system"""
        if not is_windows():
            return False
        
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_installed_packages(self) -> List[PackageInfo]:
        """Get list of installed packages"""
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return self._parse_package_list(result.stdout)
            else:
                self.logger.error(f"Failed to get installed packages: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout while getting installed packages")
            return []
        except Exception as e:
            self.logger.error(f"Error getting installed packages: {str(e)}")
            return []
    
    def get_upgradable_packages(self) -> List[PackageInfo]:
        """Get list of packages that can be upgraded"""
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                ["winget", "upgrade", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return self._parse_upgrade_list(result.stdout)
            else:
                self.logger.error(f"Failed to get upgradable packages: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout while getting upgradable packages")
            return []
        except Exception as e:
            self.logger.error(f"Error getting upgradable packages: {str(e)}")
            return []
    
    def search_packages(self, query: str, limit: int = 20) -> List[PackageInfo]:
        """Search for packages"""
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                ["winget", "search", query, "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = self._parse_package_list(result.stdout)
                return packages[:limit]
            else:
                self.logger.error(f"Failed to search packages: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout while searching packages")
            return []
        except Exception as e:
            self.logger.error(f"Error searching packages: {str(e)}")
            return []
    
    def install_package(self, package_id: str, version: Optional[str] = None) -> PackageOperation:
        """Install a package"""
        if not self.is_available():
            return PackageOperation(
                package_id=package_id,
                operation="install",
                success=False,
                message="Winget not available",
                timestamp=datetime.now()
            )
        
        try:
            cmd = ["winget", "install", package_id, "--accept-source-agreements", "--accept-package-agreements"]
            
            if self.config.silent_install:
                cmd.append("--silent")
            
            if version:
                cmd.extend(["--version", version])
            
            self.logger.info(f"Installing package: {package_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            operation = PackageOperation(
                package_id=package_id,
                operation="install",
                success=result.returncode == 0,
                message=result.stdout if result.returncode == 0 else result.stderr,
                timestamp=datetime.now()
            )
            
            if self.config.log_actions:
                self._log_operation(operation)
            
            return operation
            
        except subprocess.TimeoutExpired:
            operation = PackageOperation(
                package_id=package_id,
                operation="install",
                success=False,
                message="Installation timed out",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return operation
            
        except Exception as e:
            operation = PackageOperation(
                package_id=package_id,
                operation="install",
                success=False,
                message=f"Installation failed: {str(e)}",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return operation
    
    def uninstall_package(self, package_id: str) -> PackageOperation:
        """Uninstall a package"""
        if not self.is_available():
            return PackageOperation(
                package_id=package_id,
                operation="uninstall",
                success=False,
                message="Winget not available",
                timestamp=datetime.now()
            )
        
        try:
            cmd = ["winget", "uninstall", package_id, "--accept-source-agreements"]
            
            if self.config.silent_install:
                cmd.append("--silent")
            
            self.logger.info(f"Uninstalling package: {package_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            operation = PackageOperation(
                package_id=package_id,
                operation="uninstall",
                success=result.returncode == 0,
                message=result.stdout if result.returncode == 0 else result.stderr,
                timestamp=datetime.now()
            )
            
            if self.config.log_actions:
                self._log_operation(operation)
            
            return operation
            
        except subprocess.TimeoutExpired:
            operation = PackageOperation(
                package_id=package_id,
                operation="uninstall",
                success=False,
                message="Uninstallation timed out",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return operation
            
        except Exception as e:
            operation = PackageOperation(
                package_id=package_id,
                operation="uninstall",
                success=False,
                message=f"Uninstallation failed: {str(e)}",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return operation
    
    def upgrade_package(self, package_id: str) -> PackageOperation:
        """Upgrade a specific package"""
        if not self.is_available():
            return PackageOperation(
                package_id=package_id,
                operation="upgrade",
                success=False,
                message="Winget not available",
                timestamp=datetime.now()
            )
        
        try:
            cmd = ["winget", "upgrade", package_id, "--accept-source-agreements", "--accept-package-agreements"]
            
            if self.config.silent_install:
                cmd.append("--silent")
            
            self.logger.info(f"Upgrading package: {package_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            operation = PackageOperation(
                package_id=package_id,
                operation="upgrade",
                success=result.returncode == 0,
                message=result.stdout if result.returncode == 0 else result.stderr,
                timestamp=datetime.now()
            )
            
            if self.config.log_actions:
                self._log_operation(operation)
            
            return operation
            
        except subprocess.TimeoutExpired:
            operation = PackageOperation(
                package_id=package_id,
                operation="upgrade",
                success=False,
                message="Upgrade timed out",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return operation
            
        except Exception as e:
            operation = PackageOperation(
                package_id=package_id,
                operation="upgrade",
                success=False,
                message=f"Upgrade failed: {str(e)}",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return operation
    
    def upgrade_all_packages(self) -> List[PackageOperation]:
        """Upgrade all packages"""
        if not self.is_available():
            return []
        
        try:
            cmd = ["winget", "upgrade", "--all", "--accept-source-agreements", "--accept-package-agreements"]
            
            if self.config.silent_install:
                cmd.append("--silent")
            
            self.logger.info("Upgrading all packages")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout * 3  # Longer timeout for bulk operations
            )
            
            operation = PackageOperation(
                package_id="all",
                operation="upgrade",
                success=result.returncode == 0,
                message=result.stdout if result.returncode == 0 else result.stderr,
                timestamp=datetime.now()
            )
            
            if self.config.log_actions:
                self._log_operation(operation)
            
            return [operation]
            
        except subprocess.TimeoutExpired:
            operation = PackageOperation(
                package_id="all",
                operation="upgrade",
                success=False,
                message="Bulk upgrade timed out",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return [operation]
            
        except Exception as e:
            operation = PackageOperation(
                package_id="all",
                operation="upgrade",
                success=False,
                message=f"Bulk upgrade failed: {str(e)}",
                timestamp=datetime.now()
            )
            if self.config.log_actions:
                self._log_operation(operation)
            return [operation]
    
    def get_package_info(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a package"""
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                ["winget", "show", package_id, "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return self._parse_package_info(result.stdout)
            else:
                return None
                
        except (subprocess.TimeoutExpired, Exception):
            return None
    
    def get_sources(self) -> List[Dict[str, str]]:
        """Get list of package sources"""
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                ["winget", "source", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return self._parse_sources(result.stdout)
            else:
                return []
                
        except (subprocess.TimeoutExpired, Exception):
            return []
    
    def add_source(self, name: str, url: str) -> bool:
        """Add a package source"""
        if not self.is_available():
            return False
        
        try:
            result = subprocess.run(
                ["winget", "source", "add", "--name", name, "--arg", url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def remove_source(self, name: str) -> bool:
        """Remove a package source"""
        if not self.is_available():
            return False
        
        try:
            result = subprocess.run(
                ["winget", "source", "remove", "--name", name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def _parse_package_list(self, output: str) -> List[PackageInfo]:
        """Parse winget list/search output"""
        packages = []
        lines = output.strip().split('\n')
        
        # Skip header lines
        data_start = -1
        for i, line in enumerate(lines):
            if '---' in line or 'Name' in line:
                data_start = i + 1
                break
        
        if data_start == -1:
            return packages
        
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            
            # Simple parsing - this could be improved
            parts = line.split()
            if len(parts) >= 3:
                name = ' '.join(parts[:-2])
                package_id = parts[-2]
                version = parts[-1]
                
                packages.append(PackageInfo(
                    id=package_id,
                    name=name,
                    version=version
                ))
        
        return packages
    
    def _parse_upgrade_list(self, output: str) -> List[PackageInfo]:
        """Parse winget upgrade output"""
        packages = []
        lines = output.strip().split('\n')
        
        # Skip header lines
        data_start = -1
        for i, line in enumerate(lines):
            if '---' in line or 'Name' in line:
                data_start = i + 1
                break
        
        if data_start == -1:
            return packages
        
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            
            # Parse upgrade format: Name Id Version Available
            parts = line.split()
            if len(parts) >= 4:
                name = ' '.join(parts[:-3])
                package_id = parts[-3]
                current_version = parts[-2]
                available_version = parts[-1]
                
                packages.append(PackageInfo(
                    id=package_id,
                    name=name,
                    version=current_version,
                    available_version=available_version
                ))
        
        return packages
    
    def _parse_package_info(self, output: str) -> Dict[str, Any]:
        """Parse winget show output"""
        info = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        
        return info
    
    def _parse_sources(self, output: str) -> List[Dict[str, str]]:
        """Parse winget source list output"""
        sources = []
        lines = output.strip().split('\n')
        
        # Skip header lines
        data_start = -1
        for i, line in enumerate(lines):
            if '---' in line or 'Name' in line:
                data_start = i + 1
                break
        
        if data_start == -1:
            return sources
        
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                sources.append({
                    "name": parts[0],
                    "argument": ' '.join(parts[1:])
                })
        
        return sources
    
    def _log_operation(self, operation: PackageOperation) -> None:
        """Log package operation to file"""
        try:
            log_entry = f"{operation.timestamp.isoformat()} | {operation.operation.upper()} | {operation.package_id} | {'SUCCESS' if operation.success else 'FAILED'} | {operation.message}\n"
            
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            self.logger.error(f"Failed to log operation: {str(e)}")
    
    def get_operation_history(self, limit: int = 50) -> List[PackageOperation]:
        """Get recent package operations from log"""
        if not self._log_file.exists():
            return []
        
        try:
            operations = []
            with open(self._log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse recent log entries
            for line in reversed(lines[-limit:]):
                parts = line.strip().split(' | ')
                if len(parts) >= 5:
                    operations.append(PackageOperation(
                        package_id=parts[2],
                        operation=parts[1].lower(),
                        success=parts[3] == 'SUCCESS',
                        message=parts[4],
                        timestamp=datetime.fromisoformat(parts[0])
                    ))
            
            return operations
            
        except Exception as e:
            self.logger.error(f"Failed to read operation history: {str(e)}")
            return []

# Factory function for easy instantiation
def create_package_manager(silent_install: bool = True, **kwargs) -> PackageManager:
    """Create a package manager with specified configuration"""
    config = PackageConfig(silent_install=silent_install, **kwargs)
    return PackageManager(config)