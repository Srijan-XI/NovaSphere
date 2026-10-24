"""
Command Line Interface for NovaSphere: NovaSphere
"""

import sys
import time
from typing import Optional, Dict, Any
from novasphere.utils.config import Config
from novasphere.utils.logger import Logger
from novasphere.utils.log_store import LogDataStore
from novasphere.core.battery.battery_monitor import create_battery_monitor
from novasphere.core.diagnostics.hardware_tests import create_diagnostics
from novasphere.core.monitoring.system_monitor import create_system_monitor
from novasphere.core.package_mgmt.winget_manager import create_package_manager
from novasphere.utils.utils import create_progress_bar, format_duration

class CLIInterface:
    """Command Line Interface implementation"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.data_store = LogDataStore("cli")
        self._running = False
    
    def run(self, tool: Optional[str] = None):
        """Run the CLI interface"""
        self._running = True
        self.data_store.log_event("startup", {"tool": tool or "menu"})
        
        if tool:
            # Run specific tool
            self._run_tool(tool)
        else:
            # Show main menu
            self._show_main_menu()
    
    def _show_main_menu(self):
        """Display and handle main menu"""
        while self._running:
            self._clear_screen()
            print("=" * 60)
            print("          NovaSphere - CLI")
            print("=" * 60)
            print()
            print("Available Tools:")
            print("  1. Battery Monitor")
            print("  2. Hardware Diagnostics")
            print("  3. System Monitor")
            print("  4. Package Manager (Windows)")
            print("  5. System Summary")
            print()
            print("  0. Exit")
            print()
            
            try:
                choice = input("Select a tool (0-5): ").strip()
                
                if choice == '0':
                    self._running = False
                    print("Goodbye!")
                elif choice == '1':
                    self._run_battery_monitor()
                elif choice == '2':
                    self._run_diagnostics()
                elif choice == '3':
                    self._run_system_monitor()
                elif choice == '4':
                    self._run_package_manager()
                elif choice == '5':
                    self._show_system_summary()
                else:
                    print("Invalid choice. Please try again.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self._running = False
                print("\nGoodbye!")
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)
    
    def _run_tool(self, tool_name: str):
        """Run a specific tool directly"""
        tool_methods = {
            'battery': self._run_battery_monitor,
            'diagnostics': self._run_diagnostics,
            'monitoring': self._run_system_monitor,
            'packages': self._run_package_manager
        }
        
        if tool_name in tool_methods:
            tool_methods[tool_name]()
        else:
            print(f"Unknown tool: {tool_name}")
            print("Available tools: battery, diagnostics, monitoring, packages")
    
    def _run_battery_monitor(self):
        """Run battery monitoring tool"""
        self._clear_screen()
        print("=" * 60)
        print("                BATTERY MONITOR")
        print("=" * 60)
        
        # Get user configuration
        config = self.config.get_tool_config('battery')
        
        try:
            charger_wattage = float(input(f"Enter charger wattage (default: {config.get('charger_wattage', 65)}W): ") or config.get('charger_wattage', 65))
            battery_capacity = float(input(f"Enter battery capacity (default: {config.get('battery_capacity', 50000)}mWh): ") or config.get('battery_capacity', 50000))
            interval = int(input(f"Enter refresh interval (default: {config.get('update_interval', 5)}s): ") or config.get('update_interval', 5))
        except ValueError:
            print("Invalid input, using default values.")
            charger_wattage = config.get('charger_wattage', 65)
            battery_capacity = config.get('battery_capacity', 50000)
            interval = config.get('update_interval', 5)
        
        monitor = create_battery_monitor(
            charger_wattage=charger_wattage,
            battery_capacity=battery_capacity,
            update_interval=interval
        )
        
        if not monitor.is_battery_available():
            print("No battery found on this system!")
            input("Press Enter to continue...")
            return
        
        print(f"\nMonitoring battery (refresh every {interval}s). Press Ctrl+C to stop...\n")
        
        try:
            def display_battery_info(info):
                self._clear_screen()
                print("=" * 60)
                print("                BATTERY MONITOR")
                print("=" * 60)
                print()
                
                if 'error' in info:
                    print(f"Error: {info['error']}")
                    return
                
                print(f"Battery Percentage: {info['percentage_formatted']}")
                print(f"Status: {info['status']}")
                
                if info['is_charging']:
                    if 'charging_rate_formatted' in info:
                        print(f"Charging Rate: {info['charging_rate_formatted']}")
                    if 'estimated_charging_time_formatted' in info:
                        print(f"Time to Full: {info['estimated_charging_time_formatted']}")
                else:
                    if 'estimated_discharge_time_formatted' in info:
                        print(f"Estimated Runtime: {info['estimated_discharge_time_formatted']}")
                
                if info.get('low_battery'):
                    print("\n⚠️  LOW BATTERY WARNING!")
                
                print(f"\nLast updated: {time.strftime('%H:%M:%S')}")
                print("Press Ctrl+C to stop monitoring")
            
            monitor.start_monitoring(display_battery_info, interval)
            
        except KeyboardInterrupt:
            print("\nBattery monitoring stopped.")
        
        input("Press Enter to continue...")
    
    def _run_diagnostics(self):
        """Run hardware diagnostics"""
        self._clear_screen()
        print("=" * 60)
        print("              HARDWARE DIAGNOSTICS")
        print("=" * 60)
        print()
        print("1. Run All Tests")
        print("2. Run Individual Test")
        print("3. Back to Main Menu")
        print()
        
        choice = input("Select option (1-3): ").strip()
        
        diagnostics = create_diagnostics()
        
        if choice == '1':
            print("\nRunning all diagnostic tests...")
            print("This may take a while, please wait...\n")
            
            results = diagnostics.run_all_tests()
            
            self._display_diagnostic_results(results)
            
        elif choice == '2':
            self._run_individual_diagnostic(diagnostics)
            
        elif choice == '3':
            return
        
        input("\nPress Enter to continue...")
    
    def _run_individual_diagnostic(self, diagnostics):
        """Run individual diagnostic test"""
        tests = ['bluetooth', 'wifi', 'camera', 'microphone', 'speaker', 'keyboard', 'mouse']
        
        print("\nAvailable Tests:")
        for i, test in enumerate(tests, 1):
            print(f"  {i}. {test.title()}")
        
        try:
            choice = int(input(f"\nSelect test (1-{len(tests)}): ")) - 1
            if 0 <= choice < len(tests):
                test_name = tests[choice]
                print(f"\nRunning {test_name} test...")
                
                result = diagnostics.run_single_test(test_name)
                if result:
                    self._display_diagnostic_results([result])
                else:
                    print("Test failed to run.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    
    def _display_diagnostic_results(self, results):
        """Display diagnostic test results"""
        self._clear_screen()
        print("=" * 60)
        print("              DIAGNOSTIC RESULTS")
        print("=" * 60)
        
        status_symbols = {
            'success': '✓',
            'failed': '✗',
            'warning': '⚠',
            'skipped': '⏭',
            'error': '❌'
        }
        
        for result in results:
            symbol = status_symbols.get(result.status.value, '?')
            print(f"\n{symbol} {result.test_name.upper()}")
            print(f"   Status: {result.status.value}")
            print(f"   Message: {result.message}")
            print(f"   Duration: {result.duration:.2f}s")
            
            if result.details:
                print("   Details:")
                for key, value in result.details.items():
                    if isinstance(value, list) and key == 'devices':
                        print(f"     {key}: {len(value)} found")
                        for device in value[:3]:  # Show first 3
                            print(f"       - {device}")
                        if len(value) > 3:
                            print(f"       ... and {len(value) - 3} more")
                    else:
                        print(f"     {key}: {value}")
        
        # Summary
        successful = len([r for r in results if r.status.value == 'success'])
        total = len(results)
        print(f"\nSummary: {successful}/{total} tests passed")
    
    def _run_system_monitor(self):
        """Run system monitoring"""
        self._clear_screen()
        print("=" * 60)
        print("                SYSTEM MONITOR")
        print("=" * 60)
        print()
        print("1. Real-time Monitoring")
        print("2. System Summary")
        print("3. Temperature Info")
        print("4. Process Info")
        print("5. Back to Main Menu")
        print()
        
        choice = input("Select option (1-5): ").strip()
        
        monitor = create_system_monitor()
        
        if choice == '1':
            self._run_realtime_monitoring(monitor)
        elif choice == '2':
            self._show_system_summary_detailed(monitor)
        elif choice == '3':
            self._show_temperature_info(monitor)
        elif choice == '4':
            self._show_process_info(monitor)
        elif choice == '5':
            return
        
        input("\nPress Enter to continue...")
    
    def _run_realtime_monitoring(self, monitor):
        """Run real-time system monitoring"""
        print("\nStarting real-time monitoring. Press Ctrl+C to stop...\n")
        
        try:
            while True:
                metrics = monitor.get_current_metrics()
                
                self._clear_screen()
                print("=" * 60)
                print("            REAL-TIME SYSTEM MONITOR")
                print("=" * 60)
                print()
                
                # CPU
                cpu_bar = create_progress_bar(int(metrics.cpu_percent), 100, 30)
                print(f"CPU Usage:    {cpu_bar} {metrics.cpu_percent:.1f}%")
                
                # Memory
                memory_bar = create_progress_bar(int(metrics.memory_percent), 100, 30)
                print(f"Memory Usage: {memory_bar} {metrics.memory_percent:.1f}%")
                
                # Disk
                disk_bar = create_progress_bar(int(metrics.disk_percent), 100, 30)
                print(f"Disk Usage:   {disk_bar} {metrics.disk_percent:.1f}%")
                
                print(f"\nMemory: {self._format_bytes(metrics.memory_used)} / {self._format_bytes(metrics.memory_total)}")
                print(f"Disk:   {self._format_bytes(metrics.disk_used)} / {self._format_bytes(metrics.disk_total)}")
                print(f"Network: ↑{self._format_bytes(metrics.network_sent)} ↓{self._format_bytes(metrics.network_recv)}")
                
                print(f"\nLast updated: {time.strftime('%H:%M:%S')}")
                print("Press Ctrl+C to stop")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nReal-time monitoring stopped.")
    
    def _show_system_summary(self):
        """Show basic system summary"""
        monitor = create_system_monitor()
        summary = monitor.get_system_summary()
        
        self._clear_screen()
        print("=" * 60)
        print("                SYSTEM SUMMARY")
        print("=" * 60)
        
        # System Info
        sys_info = summary['system_info']
        print(f"\nSystem: {sys_info['platform']} {sys_info['architecture']}")
        print(f"Hostname: {sys_info['hostname']}")
        print(f"Processor: {sys_info['processor']}")
        
        # Current metrics
        cpu_info = summary['cpu']
        if 'error' not in cpu_info:
            print(f"\nCPU Usage: {cpu_info['usage_percent']:.1f}%")
            print(f"CPU Cores: {cpu_info['count_logical']} logical, {cpu_info['count_physical']} physical")
        
        memory_info = summary['memory']
        if 'error' not in memory_info:
            mem = memory_info['virtual']
            print(f"\nMemory: {mem['percent_formatted']} used")
            print(f"Memory: {mem['used_formatted']} / {mem['total_formatted']}")
        
        disk_info = summary['disk']
        if 'error' not in disk_info:
            disk = disk_info['usage']
            print(f"\nDisk: {disk['percent_formatted']} used")
            print(f"Disk: {disk['used_formatted']} / {disk['total_formatted']}")
        
        input("\nPress Enter to continue...")
    
    def _show_system_summary_detailed(self, monitor):
        """Show detailed system summary"""
        print("Loading system information...")
        summary = monitor.get_system_summary()
        
        self._clear_screen()
        print("=" * 60)
        print("            DETAILED SYSTEM SUMMARY")
        print("=" * 60)
        
        # System Info
        sys_info = summary['system_info']
        print(f"\nSystem Information:")
        print(f"  Platform: {sys_info['platform']} {sys_info['platform_version']}")
        print(f"  Architecture: {sys_info['architecture']}")
        print(f"  Hostname: {sys_info['hostname']}")
        print(f"  Processor: {sys_info['processor']}")
        
        # CPU
        cpu_info = summary['cpu']
        if 'error' not in cpu_info:
            print(f"\nCPU Information:")
            print(f"  Usage: {cpu_info['usage_percent']:.1f}%")
            print(f"  Cores: {cpu_info['count_logical']} logical, {cpu_info['count_physical']} physical")
            if cpu_info['frequency']:
                freq = cpu_info['frequency']
                print(f"  Frequency: {freq['current']:.0f} MHz (min: {freq['min']:.0f}, max: {freq['max']:.0f})")
        
        # Memory
        memory_info = summary['memory']
        if 'error' not in memory_info:
            virtual = memory_info['virtual']
            swap = memory_info['swap']
            print(f"\nMemory Information:")
            print(f"  Virtual: {virtual['percent_formatted']} used ({virtual['used_formatted']} / {virtual['total_formatted']})")
            print(f"  Swap: {swap['percent_formatted']} used ({swap['used_formatted']} / {swap['total_formatted']})")
        
        # Temperature
        temp_info = summary['temperature']
        if 'error' not in temp_info and not temp_info.get('disabled'):
            print(f"\nTemperature Information:")
            if 'temperatures' in temp_info:
                for temp in temp_info['temperatures'][:5]:  # Show first 5
                    print(f"  {temp['name']}: {temp['value']:.1f}{temp['unit']}")
        
        input("\nPress Enter to continue...")
    
    def _show_temperature_info(self, monitor):
        """Show temperature information"""
        print("Reading temperature sensors...")
        temp_info = monitor.get_temperature_info()
        
        self._clear_screen()
        print("=" * 60)
        print("              TEMPERATURE INFO")
        print("=" * 60)
        
        if 'error' in temp_info:
            print(f"\nError: {temp_info['error']}")
        elif temp_info.get('disabled'):
            print("\nTemperature monitoring is disabled.")
        else:
            if temp_info.get('temperatures'):
                print("\nTemperatures:")
                for temp in temp_info['temperatures']:
                    print(f"  {temp['name']}: {temp['value']:.1f}{temp['unit']}")
            
            if temp_info.get('fan_speeds'):
                print("\nFan Speeds:")
                for fan in temp_info['fan_speeds']:
                    print(f"  {fan['name']}: {fan['value']:.0f} {fan['unit']}")
            
            if temp_info.get('note'):
                print(f"\nNote: {temp_info['note']}")
    
    def _show_process_info(self, monitor):
        """Show process information"""
        print("Reading process information...")
        proc_info = monitor.get_process_info(20)
        
        self._clear_screen()
        print("=" * 60)
        print("               PROCESS INFO")
        print("=" * 60)
        
        if 'error' in proc_info:
            print(f"\nError: {proc_info['error']}")
        else:
            print(f"\nTotal Processes: {proc_info['total_processes']}")
            
            print("\nTop CPU Consumers:")
            for proc in proc_info['cpu_intensive'][:10]:
                print(f"  {proc['name']} (PID: {proc['pid']}): {proc['cpu_percent']:.1f}% CPU")
            
            print("\nTop Memory Consumers:")
            for proc in proc_info['memory_intensive'][:10]:
                print(f"  {proc['name']} (PID: {proc['pid']}): {proc['memory_rss_formatted']} ({proc['memory_percent']:.1f}%)")
    
    def _run_package_manager(self):
        """Run package manager"""
        self._clear_screen()
        print("=" * 60)
        print("               PACKAGE MANAGER")
        print("=" * 60)
        
        manager = create_package_manager()
        
        if not manager.is_available():
            print("\nWinget is not available on this system.")
            print("Package management is only supported on Windows with winget installed.")
            input("Press Enter to continue...")
            return
        
        while True:
            print("\n1. List Installed Packages")
            print("2. List Upgradable Packages")
            print("3. Search Packages")
            print("4. Install Package")
            print("5. Uninstall Package")
            print("6. Upgrade Package")
            print("7. Upgrade All Packages")
            print("8. Back to Main Menu")
            print()
            
            choice = input("Select option (1-8): ").strip()
            
            if choice == '1':
                self._list_installed_packages(manager)
            elif choice == '2':
                self._list_upgradable_packages(manager)
            elif choice == '3':
                self._search_packages(manager)
            elif choice == '4':
                self._install_package(manager)
            elif choice == '5':
                self._uninstall_package(manager)
            elif choice == '6':
                self._upgrade_package(manager)
            elif choice == '7':
                self._upgrade_all_packages(manager)
            elif choice == '8':
                break
            else:
                print("Invalid choice.")
    
    def _list_installed_packages(self, manager):
        """List installed packages"""
        print("\nFetching installed packages...")
        packages = manager.get_installed_packages()
        
        if packages:
            print(f"\nInstalled Packages ({len(packages)}):")
            print("-" * 60)
            for pkg in packages[:20]:  # Show first 20
                print(f"{pkg.name} ({pkg.id}) - v{pkg.version}")
            
            if len(packages) > 20:
                print(f"... and {len(packages) - 20} more packages")
        else:
            print("No packages found or failed to retrieve package list.")
        
        input("\nPress Enter to continue...")
    
    def _list_upgradable_packages(self, manager):
        """List upgradable packages"""
        print("\nChecking for upgradable packages...")
        packages = manager.get_upgradable_packages()
        
        if packages:
            print(f"\nUpgradable Packages ({len(packages)}):")
            print("-" * 60)
            for pkg in packages:
                print(f"{pkg.name} ({pkg.id})")
                print(f"  Current: v{pkg.version} → Available: v{pkg.available_version}")
                print()
        else:
            print("No upgrades available or failed to check for updates.")
        
        input("\nPress Enter to continue...")
    
    def _search_packages(self, manager):
        """Search for packages"""
        query = input("\nEnter search query: ").strip()
        if not query:
            return
        
        print(f"Searching for '{query}'...")
        packages = manager.search_packages(query, 10)
        
        if packages:
            print(f"\nSearch Results ({len(packages)}):")
            print("-" * 60)
            for pkg in packages:
                print(f"{pkg.name} ({pkg.id}) - v{pkg.version}")
        else:
            print("No packages found.")
        
        input("\nPress Enter to continue...")
    
    def _install_package(self, manager):
        """Install a package"""
        package_id = input("\nEnter package ID to install: ").strip()
        if not package_id:
            return
        
        print(f"Installing {package_id}...")
        result = manager.install_package(package_id)
        
        if result.success:
            print(f"✓ Successfully installed {package_id}")
        else:
            print(f"✗ Failed to install {package_id}: {result.message}")
        
        input("\nPress Enter to continue...")
    
    def _uninstall_package(self, manager):
        """Uninstall a package"""
        package_id = input("\nEnter package ID to uninstall: ").strip()
        if not package_id:
            return
        
        confirm = input(f"Are you sure you want to uninstall {package_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            return
        
        print(f"Uninstalling {package_id}...")
        result = manager.uninstall_package(package_id)
        
        if result.success:
            print(f"✓ Successfully uninstalled {package_id}")
        else:
            print(f"✗ Failed to uninstall {package_id}: {result.message}")
        
        input("\nPress Enter to continue...")
    
    def _upgrade_package(self, manager):
        """Upgrade a specific package"""
        package_id = input("\nEnter package ID to upgrade: ").strip()
        if not package_id:
            return
        
        print(f"Upgrading {package_id}...")
        result = manager.upgrade_package(package_id)
        
        if result.success:
            print(f"✓ Successfully upgraded {package_id}")
        else:
            print(f"✗ Failed to upgrade {package_id}: {result.message}")
        
        input("\nPress Enter to continue...")
    
    def _upgrade_all_packages(self, manager):
        """Upgrade all packages"""
        confirm = input("\nAre you sure you want to upgrade all packages? This may take a while. (y/N): ").strip().lower()
        if confirm != 'y':
            return
        
        print("Upgrading all packages...")
        results = manager.upgrade_all_packages()
        
        for result in results:
            if result.success:
                print("✓ All packages upgraded successfully")
            else:
                print(f"✗ Failed to upgrade packages: {result.message}")
        
        input("\nPress Enter to continue...")
    
    def _clear_screen(self):
        """Clear the console screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes for display"""
        from core.common.utils import format_bytes
        return format_bytes(bytes_value)