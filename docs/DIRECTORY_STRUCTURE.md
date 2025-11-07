# Directory Structure

## Overview

This document describes the reorganized directory structure of the Rotate Marker Symbol plugin. The structure follows Python best practices for plugin development and provides clear separation of concerns.

## Structure

```
rotate_marker_symbol/
├── __init__.py                    # Plugin entry point (QGIS plugin interface)
├── rotate_marker_symbol.py        # Main plugin class
├── metadata.txt                   # Plugin metadata (QGIS plugin repository)
├── icon.png                       # Plugin icon
├── resources.py                   # Compiled Qt resources
├── resources.qrc                  # Qt resource configuration
├── README.md                      # User-facing documentation
├── pyqgis.cmd                     # Windows QGIS Python launcher
│
├── core/                          # Core functionality modules
│   ├── __init__.py                # Core package initialization
│   ├── helpers.py                 # Utility classes (LayerEditingContext, MessageHelper, MouseButton)
│   ├── validators.py              # Layer and renderer validation
│   ├── field_manager.py           # Rotation field management
│   ├── visual_feedback.py         # Visual feedback (rubber bands, snap indicators)
│   ├── preview_layer.py           # Preview layer management
│   ├── rotation_state.py          # State management (dataclass)
│   ├── snapping_config.py         # Snapping configuration
│   └── rotate_marker_symbol_worker.py  # Main map tool implementation
│
├── build/                         # Build and deployment tools
│   ├── README.md                  # Build tools documentation
│   ├── plugin_upload.py           # Upload plugin to repository
│   ├── Makefile                   # Build automation
│   ├── pb_tool.cfg                # Plugin Builder tool configuration
│   └── pylintrc                   # Python linting rules
│
├── docs/                          # Documentation
│   ├── REFACTORING.md             # Refactoring documentation
│   ├── PREVIEW_LAYER_FIX.md       # Preview layer fix documentation
│   ├── DIRECTORY_STRUCTURE.md     # This file
│   └── help/                      # Sphinx documentation
│       ├── Makefile
│       ├── make.bat
│       └── source/
│           ├── conf.py
│           └── index.rst
│
├── resources/                     # Plugin resources and assets
│   ├── demo_point_data.gpkg       # Demo data (GeoPackage)
│   └── rotate_marker_symbol_demo.gif  # Demo animation
│
├── scripts/                       # Utility scripts
│   ├── compile-strings.sh         # Compile translation strings
│   ├── run-env-linux.sh           # Setup Linux environment
│   └── update-strings.sh          # Update translation strings
│
├── i18n/                          # Internationalization
│   └── af.ts                      # Translation files (Qt Linguist format)
│
└── test/                          # Unit tests
    ├── __init__.py
    ├── qgis_interface.py          # Mock QGIS interface
    ├── test_init.py               # Plugin initialization tests
    ├── test_qgis_environment.py   # Environment tests
    ├── test_resources.py          # Resource tests
    ├── test_rotate_marker_symbol_dialog.py  # Dialog tests
    ├── test_translations.py       # Translation tests
    ├── utilities.py               # Test utilities
    └── tenbytenraster.*           # Test data files
```

## Directory Purposes

### Root Directory
Contains only essential plugin files that QGIS needs to load and display the plugin:
- Plugin metadata and configuration
- Plugin entry point and main class
- Compiled resources
- User-facing README

### `core/`
Contains all the core functionality modules. This is where the actual plugin logic lives:
- **helpers.py**: Reusable utility classes
  - `LayerEditingContext`: Context manager for safe layer editing
  - `MessageHelper`: Consistent user messaging
  - `MouseButton`: Enum for mouse button constants
  
- **validators.py**: Validation logic
  - `LayerValidator`: Validates layers and renderers
  
- **field_manager.py**: Rotation field operations
  - `RotationFieldManager`: Manages rotation field lifecycle
  
- **visual_feedback.py**: Visual indicators
  - `VisualFeedbackManager`: Manages rubber bands and snap indicators
  
- **preview_layer.py**: Preview layer management
  - `PreviewLayerManager`: Handles temporary preview layer
  
- **rotation_state.py**: State management
  - `RotationState`: Dataclass for rotation operation state
  
- **snapping_config.py**: Snapping configuration
  - `SnappingConfigManager`: Configures snapping behavior
  
- **rotate_marker_symbol_worker.py**: Main map tool
  - `PointSymbolRotator`: The main map tool class

### `build/`
Contains build, deployment, and development tools:
- Plugin upload scripts
- Build automation (Makefile)
- Linting configuration
- Plugin Builder configuration

### `docs/`
Contains all documentation:
- Technical documentation
- Help files
- API documentation

### `resources/`
Contains static resources:
- Demo data
- Icons (other than main icon.png)
- Images and animations

### `scripts/`
Contains utility scripts for development:
- Translation management
- Environment setup
- Build helpers

### `i18n/`
Contains internationalization files:
- Translation files for different languages
- Qt Linguist format (.ts files)

### `test/`
Contains all unit tests:
- Test modules
- Test utilities
- Mock objects
- Test data

## Import Patterns

### Importing from core modules (in main plugin file):
```python
# In rotate_marker_symbol.py
from .core.rotate_marker_symbol_worker import PointSymbolRotator
```

### Importing within core modules (relative imports):
```python
# In core/rotate_marker_symbol_worker.py
from .helpers import LayerEditingContext, MessageHelper
from .validators import LayerValidator
# etc.
```

### Importing from parent plugin:
```python
# In any core module that needs resources
from ..resources import *
```

## Benefits of This Structure

### 1. **Clarity**
- Clear separation between core code, tests, docs, and build tools
- Easy to find any file based on its purpose
- Newcomers can quickly understand the structure

### 2. **Maintainability**
- Related code is grouped together
- Changes to one area don't require searching the entire codebase
- Clean root directory makes the plugin look professional

### 3. **Scalability**
- Easy to add new core modules to `core/`
- Easy to add new tests to `test/`
- Easy to add new documentation to `docs/`

### 4. **Build Efficiency**
- Build tools are separate from runtime code
- Can exclude `build/`, `docs/`, `test/` from plugin distribution if needed
- Faster plugin loading (fewer files in root to scan)

### 5. **Testing**
- All tests in one place
- Easy to run all tests or specific test suites
- Test data and utilities clearly organized

### 6. **Collaboration**
- Contributors know where to put new code
- Clear structure reduces merge conflicts
- Documentation is easy to find and update

## Migration from Old Structure

### What Changed
**Before:**
```
rotate_marker_symbol/
├── helpers.py
├── validators.py
├── field_manager.py
├── visual_feedback.py
├── preview_layer.py
├── rotation_state.py
├── snapping_config.py
├── rotate_marker_symbol_worker.py
├── plugin_upload.py
├── Makefile
├── pylintrc
├── pb_tool.cfg
├── REFACTORING.md
├── [many other files...]
```

**After:**
```
rotate_marker_symbol/
├── core/                    # All core modules
├── build/                   # All build tools
├── docs/                    # All documentation
├── [clean root with only essentials]
```

### Import Updates Required
Only one file needed import updates:
- `rotate_marker_symbol.py`: Changed `from .rotate_marker_symbol_worker` to `from .core.rotate_marker_symbol_worker`

All other imports within core modules use relative imports (`.helpers`, `.validators`, etc.) which remain unchanged.

## File Count

### Before Reorganization
- Root directory: ~20-25 files
- Hard to navigate
- Mixed concerns

### After Reorganization
- Root directory: 7 files
- Everything organized into purpose-specific subdirectories
- Professional appearance

## Standards Followed

This structure follows:
- **Python Package Layout**: PEP 420 (Implicit Namespace Packages)
- **QGIS Plugin Standards**: Required files in root
- **Best Practices**: Separation of concerns
- **Clean Code**: Single Responsibility Principle applied to directories

## Adding New Files

### New Core Module
```bash
# Add to core/
touch core/new_module.py

# Update core/__init__.py if needed
# Update imports in files that use it
```

### New Test
```bash
# Add to test/
touch test/test_new_feature.py
```

### New Documentation
```bash
# Add to docs/
touch docs/NEW_FEATURE.md
```

### New Build Tool
```bash
# Add to build/
touch build/new_build_tool.sh
chmod +x build/new_build_tool.sh
```

## Excluded from Version Control

The following are typically excluded (add to .gitignore):
```
__pycache__/
*.pyc
*.pyo
.idea/
.vscode/
*.egg-info/
build/dist/
*.zip
```

## Packaging for Distribution

When creating a plugin ZIP for distribution:

**Include:**
- Root files (required by QGIS)
- `core/` directory (functionality)
- `resources/` directory (assets)
- `i18n/` directory (translations)
- `docs/help/` (user documentation)

**Exclude:**
- `.git/`
- `.idea/`
- `__pycache__/`
- `build/` (not needed at runtime)
- `scripts/` (not needed at runtime)
- `test/` (not needed at runtime)
- `docs/` except `docs/help/`

## Summary

This reorganization transforms a messy root directory with 20+ files into a clean, professional structure with:
- ✅ Clear purpose for each directory
- ✅ Easy to navigate and understand
- ✅ Professional appearance
- ✅ Follows Python and QGIS best practices
- ✅ Easier to maintain and extend
- ✅ Better for collaboration

The structure is inspired by successful open-source QGIS plugins and Python packages, providing a solid foundation for long-term development.
