# Rotate Marker Symbol

A QGIS plugin for manually rotating point marker symbols.

## Features

- **Interactive Rotation**: Click and drag to visually set rotation angles
- **Real-time Preview**: See the rotation before applying it
- **Data-Driven**: Rotation values stored in a dedicated field
- **Smart Snapping**: Snap to vertices for precise alignment
- **Layer Compatibility**: Works with various renderer types (Single, Categorized, Graduated, Rule-based)

## Installation

1. Download the plugin ZIP file
2. In QGIS, go to **Plugins → Manage and Install Plugins**
3. Click **Install from ZIP**
4. Select the downloaded file
5. Enable the plugin

## Usage

1. **Activate the Tool**: Click the Rotate Marker Symbol icon in the toolbar
2. **Select a Point**: Click on any point feature
3. **Set Rotation**: Move your mouse to adjust the rotation angle
4. **Apply**: Click again to apply the rotation
5. **Cancel**: Right-click to cancel

The rotation is stored in a field called `__rotation__` and applied via data-defined symbol rotation.

## Requirements

- QGIS 3.0 or later
- Point vector layer
- Compatible marker renderer

## Documentation

- **[Directory Structure](docs/DIRECTORY_STRUCTURE.md)** - Detailed structure documentation
- **[Refactoring Guide](docs/REFACTORING.md)** - Technical refactoring details
- **[Preview Layer Fix](docs/PREVIEW_LAYER_FIX.md)** - Bug fix documentation
- **[Help Documentation](docs/help/)** - Complete user guide

## Development

### Project Structure

```
rotate_marker_symbol/
├── core/          # Core functionality modules
├── build/         # Build and deployment tools
├── docs/          # Documentation
├── test/          # Unit tests
├── resources/     # Assets and demo data
├── scripts/       # Utility scripts
└── i18n/          # Translations
```

See **[docs/DIRECTORY_STRUCTURE.md](docs/DIRECTORY_STRUCTURE.md)** for complete structure details.

### Running Tests

```bash
# Run all tests
python -m pytest test/

# Run specific test
python -m pytest test/test_rotate_marker_symbol.py
```

### Building

```bash
# Create plugin ZIP
cd build/
make zip
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## Architecture

This plugin uses a modular architecture with clear separation of concerns:

- **helpers.py**: Utility classes (LayerEditingContext, MessageHelper)
- **validators.py**: Layer and renderer validation
- **field_manager.py**: Rotation field management
- **visual_feedback.py**: Visual indicators (rubber bands, snap indicators)
- **preview_layer.py**: Preview layer management
- **rotation_state.py**: State management
- **snapping_config.py**: Snapping configuration
- **rotate_marker_symbol_worker.py**: Main map tool

See [docs/REFACTORING.md](docs/REFACTORING.md) for detailed architecture documentation.

## Known Issues

None currently! The preview layer persistence bug has been fixed.

## License

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

## Author

Matt Needle (matt.needle.nl@gmail.com)

## Version History

- **1.1.0** - Refactored architecture, bug fixes, improved structure
- **1.0.0** - Initial release

## Support

For issues, questions, or contributions:
- Check the [documentation](docs/)
- Review the [code structure](docs/DIRECTORY_STRUCTURE.md)
- Read the [refactoring guide](docs/REFACTORING.md)

## Acknowledgments

- Built with [Plugin Builder](http://g-sherman.github.io/Qgis-Plugin-Builder/)
- Refactored following SOLID principles and Python best practices
- Uses QGIS PyQt API for GUI integration
