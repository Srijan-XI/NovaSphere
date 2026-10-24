# Migration Guide: NovaSphere v1.0 → v2.0

## Overview

NovaSphere v2.0 introduces a complete codebase restructuring following Python packaging best practices. This guide helps you transition from the old structure to the new one.

## What Changed?

### Directory Structure

**Old Structure (v1.0):**
```
NovaSphere/
├── core/
│   ├── battery/
│   ├── common/          # Utils mixed with core
│   ├── diagnostics/
│   └── monitoring/
├── interfaces/           # UI modules
├── test/                 # Singular
├── logs/                 # Root level
├── reports/              # Root level
└── main.py               # Entry point
```

**New Structure (v2.0):**
```
NovaSphere/
├── src/novasphere/        # All source code
│   ├── core/             # Business logic only
│   ├── utils/            # Utilities (was common/)
│   ├── ui/               # User interfaces (was interfaces/)
│   ├── services/         # Service layer (new)
│   └── models/           # Data models (new)
├── tests/                # Plural, organized
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── data/                 # Runtime data
│   ├── logs/
│   └── reports/
├── scripts/              # Utility scripts
├── pyproject.toml        # Modern config
└── setup.py              # Compatibility
```

### Import Changes

**Old Imports:**
```python
from core.common.config import Config
from core.common.logger import Logger
from interfaces.gui.gui_interface import GUIInterface
```

**New Imports:**
```python
from novasphere.utils.config import Config
from novasphere.utils.logger import Logger
from novasphere.ui.gui.gui_interface import GUIInterface
```

### Running the Application

**Old Way:**
```bash
python main.py --gui
python main.py --cli battery
```

**New Ways:**
```bash
# Option 1: Old way still works (backward compatibility)
python main.py --gui

# Option 2: As a module
python -m novasphere --gui

# Option 3: After installation (editable mode)
pip install -e .
nova --gui
```

## Step-by-Step Migration

### For End Users

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Install in editable mode:**
   ```bash
   pip install -e .
   ```

3. **Use new command:**
   ```bash
   nova --gui
   # or
   python -m novasphere --gui
   ```

### For Developers

1. **Update your local repository:**
   ```bash
   git pull origin main
   ```

2. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Update imports in your code:**
   - Replace `core.common` → `novasphere.utils`
   - Replace `interfaces` → `novasphere.ui`
   - Add `novasphere.` prefix to all imports

4. **Run tests:**
   ```bash
   pytest tests/
   ```

### For Contributors

1. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Code formatting:**
   ```bash
   black src/
   isort src/
   ```

3. **Type checking:**
   ```bash
   mypy src/novasphere
   ```

4. **Run full test suite:**
   ```bash
   pytest tests/ --cov=src/novasphere
   ```

## Breaking Changes

### Import Paths
All imports now require the `novasphere.` prefix:
- `core.*` → `novasphere.core.*`
- `interfaces.*` → `novasphere.ui.*`

### Module Locations
- `core/common/` → `src/novasphere/utils/`
- `interfaces/` → `src/novasphere/ui/`
- `test/` → `tests/unit/`

### Configuration Files
- Old config at root still works
- New location: `~/.novasphere/config.json`
- Data files now in `data/` directory

## New Features

### 1. Editable Installation
```bash
pip install -e .
```
Changes in `src/` are immediately available without reinstall.

### 2. CLI Command
```bash
nova --help
```
System-wide command after `pip install`.

### 3. Module Execution
```bash
python -m novasphere
```
Run as a Python module.

### 4. Optional Dependencies
```bash
# Install with GUI features
pip install -e ".[gui]"

# Install all optional features
pip install -e ".[all]"

# Install development tools
pip install -e ".[dev]"
```

### 5. Modern Testing
```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/novasphere

# Specific test file
pytest tests/unit/test_dependency_checker.ipynb
```

## Configuration Updates

### pyproject.toml
New centralized configuration file replaces scattered config:
- Project metadata
- Dependencies
- Build system
- Tool configuration (pytest, black, mypy)

### setup.py
Minimal file for backward compatibility. Most config in `pyproject.toml`.

## Data Migration

### Logs
Old location: `./logs/`
New location: `./data/logs/`

Files are automatically copied during restructure.

### Reports
Old location: `./reports/`
New location: `./data/reports/`

Export functions updated to use new location.

### User Configuration
Old: `./config.json`
New: `~/.novasphere/config.json`

Application migrates settings automatically on first run.

## Testing Updates

### Test Organization
```
tests/
├── unit/              # Unit tests (was test/*.ipynb)
├── integration/       # Integration tests (new)
└── fixtures/          # Test data and fixtures (new)
```

### Running Tests
```bash
# All tests
pytest

# Specific category
pytest tests/unit/
pytest tests/integration/

# With coverage report
pytest --cov=src/novasphere --cov-report=html
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'core'`

**Solution:**
```bash
# Install package in editable mode
pip install -e .
```

### Old Imports Still in Code

**Problem:** Code using old imports breaks

**Solution:**
Run find-replace in your IDE:
- `from core.` → `from novasphere.core.`
- `from interfaces.` → `from novasphere.ui.`
- `import core.` → `import novasphere.core.`

### Tests Not Found

**Problem:** `pytest` can't find tests

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/NovaSphere

# Run with explicit path
pytest tests/
```

### Command Not Found

**Problem:** `nova` command not available

**Solution:**
```bash
# Reinstall in editable mode
pip uninstall nova
pip install -e .
```

## Backward Compatibility

### main.py Still Works
The old `main.py` remains functional:
```bash
python main.py --gui  # Still works!
```

### Gradual Migration
You can migrate gradually:
1. Keep using `python main.py` while updating imports
2. Switch to `python -m novasphere` when ready
3. Install with `pip install -e .` for `nova` command

### Old Directories
Old directories (`core/`, `interfaces/`, `test/`) can be removed after verifying new structure works:
```bash
# Verify new structure works
python -m novasphere --version

# Then remove old (optional)
# git rm -r core/ interfaces/ test/
```

## FAQ

**Q: Do I need to reinstall dependencies?**
A: Yes, run `pip install -e ".[all]"` for complete installation.

**Q: Will my old config file work?**
A: Yes, `config.json` in root is still supported.

**Q: Can I contribute with the old structure?**
A: No, all new PRs must use the new structure.

**Q: How do I update my fork?**
A: Pull from upstream, resolve conflicts, update imports.

**Q: Is the old `main.py` deprecated?**
A: No, it's maintained for backward compatibility.

## Getting Help

- **Documentation:** `docs/` folder
- **Issues:** https://github.com/Srijan-XI/NovaSphere/issues
- **Discussions:** https://github.com/Srijan-XI/NovaSphere/discussions

## Summary

✅ **New structure is more organized and follows Python standards**
✅ **Backward compatibility maintained via `main.py`**
✅ **Modern packaging with `pyproject.toml`**
✅ **Better testing organization**
✅ **Editable installation for development**
✅ **System-wide CLI command**

**Recommended migration path:**
1. Pull latest changes
2. Run `pip install -e ".[all]"`
3. Test with `python -m novasphere --gui`
4. Update imports in your code
5. Use `nova` command going forward
