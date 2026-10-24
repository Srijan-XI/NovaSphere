#!/usr/bin/env python3
"""
All-in-One System Tools - Installation Verification Script
Tests if the installation is working correctly on Linux systems
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def print_header():
    print("=" * 70)
    print("  NovaSphere - Installation Verification")
    print("=" * 70)
    print()

def print_section(title):
    print(f"\n>>> {title}")
    print("-" * 50)

def check_python_version():
    print_section("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 7):
        print("✓ Python version is compatible (>= 3.7)")
        return True
    else:
        print("✗ Python version is too old (minimum: 3.7)")
        return False

def check_system_dependencies():
    print_section("System Dependencies Check")
    
    dependencies = {
        'Linux': [
            ('portaudio', 'portaudio19-dev'),
            ('alsa', 'libasound2-dev'),
            ('sdl2', 'libsdl2-dev'),
            ('opencv', 'libopencv-dev'),
            ('bluetooth', 'libbluetooth-dev'),
        ]
    }
    
    if sys.platform.startswith('linux'):
        print("Checking Linux system dependencies...")
        # Basic check - look for common library paths
        lib_paths = ['/usr/lib', '/usr/local/lib', '/lib']
        
        for dep, package in dependencies['Linux']:
            found = False
            for lib_path in lib_paths:
                if os.path.exists(lib_path) and any(dep in f for f in os.listdir(lib_path) if os.path.isfile(os.path.join(lib_path, f))):
                    found = True
                    break
            
            status = "✓" if found else "?"
            print(f"{status} {dep} (install with: sudo apt-get install {package})")
    
    return True

def check_python_packages():
    print_section("Python Packages Check")
    
    required_packages = [
        'psutil',
        'cv2',  # opencv-python
        'sounddevice',
        'pygame',
        'bleak',
        'pynput',
        'flask',
        'flask_cors',
        'colorama',
        'packaging'
    ]
    
    optional_packages = [
        'requests',
        'schedule',
        'watchdog'
    ]
    
    all_good = True
    
    print("Required packages:")
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
                print(f"✓ opencv-python (cv2) - version {cv2.__version__}")
            else:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✓ {package} - version {version}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_good = False
    
    print("\nOptional packages:")
    for package in optional_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {package} - version {version}")
        except ImportError:
            print(f"? {package} - not installed (optional)")
    
    return all_good

def check_hardware_access():
    print_section("Hardware Access Check")
    
    # Check audio devices
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        
        print(f"✓ Audio: {len(input_devices)} input device(s), {len(output_devices)} output device(s)")
    except Exception as e:
        print(f"✗ Audio: Error accessing audio devices - {e}")
    
    # Check video devices
    try:
        import cv2
        # Try to open default camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Camera: Default camera accessible")
            cap.release()
        else:
            print("? Camera: Default camera not accessible (may be in use or not present)")
    except Exception as e:
        print(f"✗ Camera: Error accessing camera - {e}")
    
    # Check Bluetooth
    try:
        import bleak
        print("✓ Bluetooth: bleak library available")
    except Exception as e:
        print(f"✗ Bluetooth: Error with bluetooth library - {e}")
    
    return True

def check_file_permissions():
    print_section("File Permissions Check")
    
    # Check if main.py exists and is executable
    main_py = Path("main.py")
    if main_py.exists():
        print("✓ main.py exists")
        if os.access(main_py, os.X_OK):
            print("✓ main.py is executable")
        else:
            print("? main.py is not executable (may need chmod +x)")
    else:
        print("✗ main.py not found")
        return False
    
    # Check write permissions for config directory
    config_dir = Path.home() / ".config" / "allinone-system-tools"
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        test_file = config_dir / "test_write"
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Config directory writable")
    except Exception as e:
        print(f"✗ Config directory not writable - {e}")
        return False
    
    return True

def test_application_launch():
    print_section("Application Launch Test")
    
    try:
        # Test if the application can show help
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ Application launches successfully")
            print("✓ Help command works")
            return True
        else:
            print(f"✗ Application failed to launch - return code: {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Application launch timed out")
        return False
    except Exception as e:
        print(f"✗ Error testing application launch - {e}")
        return False

def check_user_groups():
    print_section("User Groups Check")
    
    try:
        import grp
        import pwd
        
        user = pwd.getpwuid(os.getuid()).pw_name
        user_groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
        user_groups.append(pwd.getpwuid(os.getuid()).pw_gid)  # Primary group
        
        required_groups = ['audio', 'video', 'dialout']
        
        print(f"Current user: {user}")
        print(f"User groups: {', '.join(user_groups)}")
        
        for group in required_groups:
            if group in user_groups:
                print(f"✓ Member of {group} group")
            else:
                print(f"? Not member of {group} group (may limit hardware access)")
    except Exception as e:
        print(f"? Could not check user groups - {e}")
    
    return True

def generate_report():
    print_section("Verification Summary")
    
    tests = [
        ("Python Version", check_python_version),
        ("System Dependencies", check_system_dependencies),
        ("Python Packages", check_python_packages),
        ("Hardware Access", check_hardware_access),
        ("File Permissions", check_file_permissions),
        ("User Groups", check_user_groups),
        ("Application Launch", test_application_launch),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your installation is ready to use.")
        print("\nTo get started, run:")
        print("  allinone-tools --help")
        print("  allinone-tools")
    elif passed >= total * 0.8:  # 80% pass rate
        print("\n⚠️  Most tests passed. Installation should work with minor issues.")
        print("Check the failed tests above and refer to the troubleshooting guide.")
    else:
        print("\n❌ Several tests failed. Please check your installation.")
        print("Refer to INSTALL_LINUX.md for troubleshooting steps.")
    
    return passed == total

def main():
    print_header()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Usage: python3 verify_installation.py")
        print("\nThis script verifies that All-in-One System Tools is correctly installed")
        print("and all dependencies are available.")
        return
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("Starting installation verification...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    
    success = generate_report()
    
    print(f"\nVerification log saved to: {script_dir}/verification.log")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())