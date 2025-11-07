# Build Tools

This directory contains build and deployment tools for the plugin.

## Files

- **plugin_upload.py** - Upload plugin to QGIS plugin repository
- **Makefile** - Build automation
- **pb_tool.cfg** - Plugin Builder tool configuration
- **pylintrc** - Python linting configuration

## Usage

### Upload to Plugin Repository
```bash
python build/plugin_upload.py
```

### Build plugin zip
```bash
make zip
```
