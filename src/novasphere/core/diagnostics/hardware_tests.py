"""
Hardware Diagnostics Core Module
Extracted and refactored from DeviceDiagnosticTool
"""

import asyncio
import subprocess
import platform
from typing import Dict, Any, List, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum
from novasphere.utils.utils import safe_execute, is_windows, is_linux, is_macos

class TestResult(Enum):
    """Test result status"""
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"

class DiagnosticResult(NamedTuple):
    """Diagnostic test result"""
    test_name: str
    status: TestResult
    message: str
    details: Dict[str, Any]
    duration: float

@dataclass
class DiagnosticConfig:
    """Diagnostic configuration"""
    timeout: int = 30
    auto_fix: bool = False
    generate_report: bool = True
    skip_lengthy_tests: bool = False

class HardwareDiagnostics:
    """Core hardware diagnostics functionality"""
    
    def __init__(self, config: Optional[DiagnosticConfig] = None):
        self.config = config or DiagnosticConfig()
        self.results: List[DiagnosticResult] = []
    
    def run_all_tests(self) -> List[DiagnosticResult]:
        """Run all available diagnostic tests"""
        self.results.clear()
        
        tests = [
            self._test_bluetooth,
            self._test_wifi,
            self._test_camera,
            self._test_microphone,
            self._test_speaker,
            self._test_keyboard,
            self._test_mouse
        ]
        
        for test in tests:
            try:
                result = safe_execute(test, default_return=None)
                if result:
                    self.results.append(result)
            except Exception as e:
                error_result = DiagnosticResult(
                    test_name=test.__name__.replace('_test_', ''),
                    status=TestResult.ERROR,
                    message=f"Test execution failed: {str(e)}",
                    details={},
                    duration=0.0
                )
                self.results.append(error_result)
        
        return self.results
    
    def run_single_test(self, test_name: str) -> Optional[DiagnosticResult]:
        """Run a single diagnostic test"""
        test_methods = {
            'bluetooth': self._test_bluetooth,
            'wifi': self._test_wifi,
            'camera': self._test_camera,
            'microphone': self._test_microphone,
            'speaker': self._test_speaker,
            'keyboard': self._test_keyboard,
            'mouse': self._test_mouse
        }
        
        if test_name.lower() not in test_methods:
            return DiagnosticResult(
                test_name=test_name,
                status=TestResult.ERROR,
                message=f"Unknown test: {test_name}",
                details={},
                duration=0.0
            )
        
        return safe_execute(test_methods[test_name.lower()], default_return=None)
    
    def _test_bluetooth(self) -> DiagnosticResult:
        """Test Bluetooth functionality"""
        import time
        start_time = time.time()
        
        try:
            # Try to use bleak for Bluetooth scanning
            try:
                import bleak
                
                async def scan_bluetooth():
                    scanner = bleak.BleakScanner()
                    devices = await scanner.discover(timeout=5.0)
                    return devices
                
                # Run the async scan
                devices = asyncio.run(scan_bluetooth())
                
                if devices:
                    device_list = [{"name": d.name or "Unknown", "address": d.address} for d in devices]
                    return DiagnosticResult(
                        test_name="bluetooth",
                        status=TestResult.SUCCESS,
                        message=f"Found {len(devices)} Bluetooth device(s)",
                        details={"devices": device_list},
                        duration=time.time() - start_time
                    )
                else:
                    return DiagnosticResult(
                        test_name="bluetooth",
                        status=TestResult.WARNING,
                        message="No Bluetooth devices found",
                        details={"devices": []},
                        duration=time.time() - start_time
                    )
                    
            except ImportError:
                return DiagnosticResult(
                    test_name="bluetooth",
                    status=TestResult.SKIPPED,
                    message="Bluetooth library (bleak) not available",
                    details={},
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            return DiagnosticResult(
                test_name="bluetooth",
                status=TestResult.FAILED,
                message=f"Bluetooth test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def _test_wifi(self) -> DiagnosticResult:
        """Test Wi-Fi functionality"""
        import time
        start_time = time.time()
        
        try:
            if is_windows():
                # Use netsh on Windows
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    if any(
                        line.split(":", 1)[0].strip().lower() == "state"
                        and line.split(":", 1)[1].strip().lower() == "connected"
                        for line in output.splitlines()
                        if ":" in line
                    ):
                        return DiagnosticResult(
                            test_name="wifi",
                            status=TestResult.SUCCESS,
                            message="Wi-Fi is connected",
                            details={"connected": True},
                            duration=time.time() - start_time
                        )
                    else:
                        return DiagnosticResult(
                            test_name="wifi",
                            status=TestResult.WARNING,
                            message="Wi-Fi is not connected",
                            details={"connected": False},
                            duration=time.time() - start_time
                        )
                
            elif is_linux():
                # Use nmcli on Linux
                result = subprocess.run(
                    ["nmcli", "dev", "wifi"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    networks = result.stdout.count('\n') - 1  # Subtract header
                    return DiagnosticResult(
                        test_name="wifi",
                        status=TestResult.SUCCESS,
                        message=f"Found {networks} Wi-Fi network(s)",
                        details={"networks_found": networks},
                        duration=time.time() - start_time
                    )
            
            return DiagnosticResult(
                test_name="wifi",
                status=TestResult.SKIPPED,
                message="Wi-Fi test not supported on this platform",
                details={},
                duration=time.time() - start_time
            )
            
        except subprocess.TimeoutExpired:
            return DiagnosticResult(
                test_name="wifi",
                status=TestResult.FAILED,
                message="Wi-Fi test timed out",
                details={},
                duration=time.time() - start_time
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="wifi",
                status=TestResult.FAILED,
                message=f"Wi-Fi test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def _test_camera(self) -> DiagnosticResult:
        """Test camera functionality"""
        import time
        start_time = time.time()
        
        try:
            import cv2
            
            # Try to open the default camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return DiagnosticResult(
                    test_name="camera",
                    status=TestResult.FAILED,
                    message="Cannot access camera",
                    details={},
                    duration=time.time() - start_time
                )
            
            # Try to read a frame
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                height, width = frame.shape[:2]
                return DiagnosticResult(
                    test_name="camera",
                    status=TestResult.SUCCESS,
                    message="Camera is working",
                    details={"resolution": f"{width}x{height}"},
                    duration=time.time() - start_time
                )
            else:
                return DiagnosticResult(
                    test_name="camera",
                    status=TestResult.FAILED,
                    message="Failed to capture image from camera",
                    details={},
                    duration=time.time() - start_time
                )
                
        except ImportError:
            return DiagnosticResult(
                test_name="camera",
                status=TestResult.SKIPPED,
                message="Camera library (opencv-python) not available",
                details={},
                duration=time.time() - start_time
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="camera",
                status=TestResult.FAILED,
                message=f"Camera test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def _test_microphone(self) -> DiagnosticResult:
        """Test microphone functionality"""
        import time
        start_time = time.time()
        
        try:
            import sounddevice as sd
            
            # Try to record for 1 second
            duration = 1
            sample_rate = 44100
            
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float64'
            )
            sd.wait()
            
            # Check if we got some audio data
            if recording is not None and len(recording) > 0:
                # Simple check for non-zero audio data
                max_amplitude = float(max(abs(recording.max()), abs(recording.min())))
                
                return DiagnosticResult(
                    test_name="microphone",
                    status=TestResult.SUCCESS,
                    message="Microphone is working",
                    details={
                        "sample_rate": sample_rate,
                        "duration": duration,
                        "max_amplitude": max_amplitude
                    },
                    duration=time.time() - start_time
                )
            else:
                return DiagnosticResult(
                    test_name="microphone",
                    status=TestResult.FAILED,
                    message="No audio data recorded",
                    details={},
                    duration=time.time() - start_time
                )
                
        except ImportError:
            return DiagnosticResult(
                test_name="microphone",
                status=TestResult.SKIPPED,
                message="Audio library (sounddevice) not available",
                details={},
                duration=time.time() - start_time
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="microphone",
                status=TestResult.FAILED,
                message=f"Microphone test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def _test_speaker(self) -> DiagnosticResult:
        """Test speaker functionality"""
        import time
        start_time = time.time()
        
        try:
            import pygame
            
            # Initialize pygame mixer
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Generate a simple beep sound
            import numpy as np
            
            # Create a simple sine wave
            sample_rate = 22050
            duration = 0.5  # seconds
            frequency = 440  # A4 note
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(frequency * 2 * np.pi * t)
            
            # Convert to pygame sound format
            sound_array = (wave * 32767).astype(np.int16)
            sound_array = np.repeat(sound_array.reshape(len(sound_array), 1), 2, axis=1)
            
            sound = pygame.sndarray.make_sound(sound_array)
            
            # Play the sound
            channel = sound.play()
            
            # Wait for it to finish
            while channel.get_busy():
                pygame.time.wait(100)
            
            pygame.mixer.quit()
            
            return DiagnosticResult(
                test_name="speaker",
                status=TestResult.SUCCESS,
                message="Speaker test completed (sound played)",
                details={"frequency": frequency, "duration": duration},
                duration=time.time() - start_time
            )
            
        except ImportError as e:
            missing_lib = "pygame" if "pygame" in str(e) else "numpy"
            return DiagnosticResult(
                test_name="speaker",
                status=TestResult.SKIPPED,
                message=f"Audio library ({missing_lib}) not available",
                details={},
                duration=time.time() - start_time
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="speaker",
                status=TestResult.FAILED,
                message=f"Speaker test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def _test_keyboard(self) -> DiagnosticResult:
        """Test keyboard functionality (non-interactive)"""
        import time
        start_time = time.time()
        
        try:
            from pynput import keyboard
            
            # For non-interactive testing, we'll just check if we can create a listener
            # In a real interactive test, this would wait for keypresses
            
            def on_press(key):
                pass  # Dummy callback
            
            # Test if we can create a keyboard listener
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            listener.stop()
            
            return DiagnosticResult(
                test_name="keyboard",
                status=TestResult.WARNING,
                message="Keyboard listener can start; physical key input requires an interactive test",
                details={"interactive_test_required": True},
                duration=time.time() - start_time
            )
            
        except ImportError:
            return DiagnosticResult(
                test_name="keyboard",
                status=TestResult.SKIPPED,
                message="Input library (pynput) not available",
                details={},
                duration=time.time() - start_time
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="keyboard",
                status=TestResult.FAILED,
                message=f"Keyboard test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def _test_mouse(self) -> DiagnosticResult:
        """Test mouse functionality (non-interactive)"""
        import time
        start_time = time.time()
        
        try:
            from pynput import mouse
            
            # For non-interactive testing, we'll just check if we can create a listener
            # In a real interactive test, this would wait for mouse clicks
            
            def on_click(x, y, button, pressed):
                pass  # Dummy callback
            
            # Test if we can create a mouse listener
            listener = mouse.Listener(on_click=on_click)
            listener.start()
            listener.stop()
            
            # Also test if we can get current mouse position
            current_pos = mouse.Controller().position
            
            return DiagnosticResult(
                test_name="mouse",
                status=TestResult.WARNING,
                message="Mouse listener can start; physical movement and clicks require an interactive test",
                details={
                    "current_position": list(current_pos),
                    "interactive_test_required": True
                },
                duration=time.time() - start_time
            )
            
        except ImportError:
            return DiagnosticResult(
                test_name="mouse",
                status=TestResult.SKIPPED,
                message="Input library (pynput) not available",
                details={},
                duration=time.time() - start_time
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="mouse",
                status=TestResult.FAILED,
                message=f"Mouse test failed: {str(e)}",
                details={"error": str(e)},
                duration=time.time() - start_time
            )
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results"""
        if not self.results:
            return {"error": "No tests have been run"}
        
        summary = {
            "total_tests": len(self.results),
            "successful": len([r for r in self.results if r.status == TestResult.SUCCESS]),
            "failed": len([r for r in self.results if r.status == TestResult.FAILED]),
            "warnings": len([r for r in self.results if r.status == TestResult.WARNING]),
            "skipped": len([r for r in self.results if r.status == TestResult.SKIPPED]),
            "errors": len([r for r in self.results if r.status == TestResult.ERROR]),
            "total_duration": sum(r.duration for r in self.results),
            "results": [
                {
                    "test": r.test_name,
                    "status": r.status.value,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in self.results
            ]
        }
        
        return summary
    
    def generate_report(self) -> str:
        """Generate a text report of diagnostic results"""
        if not self.results:
            return "No diagnostic tests have been run."
        
        report = ["Hardware Diagnostic Report", "=" * 30, ""]
        
        summary = self.get_test_summary()
        report.extend([
            f"Total Tests: {summary['total_tests']}",
            f"Successful: {summary['successful']}",
            f"Failed: {summary['failed']}",
            f"Warnings: {summary['warnings']}",
            f"Skipped: {summary['skipped']}",
            f"Errors: {summary['errors']}",
            f"Total Time: {summary['total_duration']:.2f}s",
            "",
            "Detailed Results:",
            "-" * 20
        ])
        
        for result in self.results:
            status_symbol = {
                TestResult.SUCCESS: "✓",
                TestResult.FAILED: "✗",
                TestResult.WARNING: "⚠",
                TestResult.SKIPPED: "⏭",
                TestResult.ERROR: "❌"
            }.get(result.status, "?")
            
            report.extend([
                f"{status_symbol} {result.test_name.upper()}",
                f"   Status: {result.status.value}",
                f"   Message: {result.message}",
                f"   Duration: {result.duration:.2f}s",
                ""
            ])
        
        return "\n".join(report)

# Factory function for easy instantiation
def create_diagnostics(timeout: int = 30, **kwargs) -> HardwareDiagnostics:
    """Create a hardware diagnostics instance with specified configuration"""
    config = DiagnosticConfig(timeout=timeout, **kwargs)
    return HardwareDiagnostics(config)
