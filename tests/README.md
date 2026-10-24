# NovaSphere Test Suite

Comprehensive unit tests for NovaSphere v2.0 modules using pytest in Jupyter notebooks.

## Overview

All tests are written in `.ipynb` (Jupyter Notebook) format for interactive testing and documentation. Each test notebook focuses on a specific module and can be run independently or as part of the complete test suite.

## Test Files

| Notebook | Module Tested | Description |
|----------|---------------|-------------|
| `test_dependency_checker.ipynb` | `core/common/dependency_checker.py` | Tests dependency validation and auto-installation |
| `test_performance_monitor.ipynb` | `core/common/performance_monitor.py` | Tests metrics tracking, health scoring, and trends |
| `test_report_exporter.ipynb` | `core/common/report_exporter.py` | Tests JSON/CSV/TXT export functionality |
| `test_theme_manager.ipynb` | `core/common/theme_manager.py` | Tests dark/light themes and config persistence |
| `test_notifications.ipynb` | `core/common/notifications.py` | Tests cross-platform desktop notifications |
| `run_all_tests.ipynb` | All modules | Master test runner with coverage reports |

## Installation

Install testing dependencies:

```powershell
pip install pytest pytest-cov pytest-mock
```

Or install all requirements including testing:

```powershell
pip install -r ../requirements.txt
```

## Running Tests

### Option 1: Jupyter Notebook (Interactive)

1. Open any test notebook in Jupyter:
   ```powershell
   jupyter notebook test_dependency_checker.ipynb
   ```

2. Run all cells sequentially (Cell → Run All)

3. View results inline with detailed output

### Option 2: Master Test Runner

Run the complete test suite:

```powershell
jupyter notebook run_all_tests.ipynb
```

This will:
- Run all test suites
- Generate coverage reports
- Create HTML coverage report in `../htmlcov/`

### Option 3: pytest Command Line

Run pytest directly on modules:

```powershell
# Run all tests in core/common
pytest ../core/common/ -v

# Run with coverage
pytest ../core/common/ --cov=../core/common --cov-report=html

# Run specific module tests
pytest ../core/common/dependency_checker.py -v
```

### Option 4: VS Code

1. Open any `.ipynb` file in VS Code
2. Select Python kernel
3. Click "Run All" or run cells individually

## Test Structure

Each test notebook follows this structure:

```
1. Imports and Setup
   - Add parent directory to path
   - Import pytest and target module

2. Test Categories
   - Initialization tests
   - Functionality tests
   - Edge case tests
   - Integration tests

3. pytest Runner
   - Run with pytest.main([])
   - Generate reports
```

## Writing New Tests

To add a new test notebook:

1. Create `test_<module_name>.ipynb`
2. Follow the template structure:

```python
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import pytest
from core.common.<module> import <Class>

def test_feature():
    """Test description"""
    # Arrange
    obj = Class()
    
    # Act
    result = obj.method()
    
    # Assert
    assert result == expected
    print("✅ Test passed")

test_feature()
```

3. Add to `run_all_tests.ipynb`

## Test Coverage

Current coverage targets:

- **Dependency Checker**: 90%+ coverage
  - Package checking
  - Installation
  - Validation

- **Performance Monitor**: 85%+ coverage
  - Metric snapshots
  - History tracking
  - Health scoring
  - Trend detection

- **Report Exporter**: 90%+ coverage
  - JSON export
  - CSV export
  - Text export
  - File naming

- **Theme Manager**: 80%+ coverage
  - Theme switching
  - Config persistence
  - Window geometry

- **Notifications**: 75%+ coverage
  - Platform detection
  - Alert methods
  - Fallback mechanism

## CI/CD Integration

To run tests in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Run tests with pytest
  run: pytest core/common/ -v --cov=core/common --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Jupyter Kernel Issues

```powershell
# Install Jupyter kernel
python -m ipykernel install --user --name nova

# List kernels
jupyter kernelspec list

# Use specific kernel
jupyter notebook --kernel=nova
```

### Import Errors

Ensure the parent directory is in path:
```python
sys.path.insert(0, os.path.abspath('..'))
```

### Missing Dependencies

Install all test dependencies:
```powershell
pip install pytest pytest-cov pytest-mock jupyter
```

### Platform-Specific Tests

Some tests may be skipped on certain platforms:
- Windows notification tests on Linux/macOS
- Linux notification tests on Windows
- Tkinter tests in headless environments

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use `tempfile.TemporaryDirectory()` for file tests
3. **Mocking**: Mock external dependencies (subprocess, platform)
4. **Assertions**: Include descriptive messages
5. **Documentation**: Add markdown cells explaining test purposes
6. **Coverage**: Aim for 80%+ coverage per module

## Reporting Issues

If tests fail:

1. Note the failing test name
2. Check the traceback in notebook output
3. Run with verbose output: `pytest -vv`
4. Create issue with:
   - Test name
   - Expected vs actual behavior
   - Full traceback
   - Platform (Windows/Linux/macOS)

## Contributing

When adding new features to NovaSphere:

1. Create corresponding test notebook
2. Aim for 80%+ coverage
3. Test all edge cases
4. Update `run_all_tests.ipynb`
5. Update this README

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Jupyter Notebook Testing](https://jupyter.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Happy Testing! 🧪**
