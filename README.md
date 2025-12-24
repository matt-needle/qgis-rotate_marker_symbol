# Rotate Marker Symbol
This tool is designed to be an improvement on the native Rotate Point Symbols tool. Rotation using this tool follows the mouse cursor exactly and a guideline appears to assist in precise rotation towards another feature or location on the map canvas  
![rotate_marker_symbol_demo](https://github.com/user-attachments/assets/48e66b66-e783-4248-a2c2-a6f3797d7dcb)

### How to use
- Find the tool in the Advanced Digitizing toolbar (editing does *not* need to be active)
<img width="712" height="51" alt="image" src="https://github.com/user-attachments/assets/6992aa35-e337-42cc-b6ed-ccc5552c9606" />

- Select a point layer from the Layers Panel (with a Single Symbol, Categorized, Graduated, or Rule-based renderer)
- Left-click a point to begin rotating
- Use the guideline to rotate exactly where desired
- Left-click again to modify its rotation -- Or -- Right-click to cancel

### How it works
- A field named `_rotation_` is added to the original point layer. This field is updated with the rotation angle
- The clicked feature's symbol is cloned and rendered on the the map canvas as a [QgsMapCanvasItem](https://qgis.org/pyqgis/master/gui/QgsMapCanvasItem.html) to create the semi-transparent preview symbol
- A guide line appears between the symbol and the mouse cursor to assist in precise rotation towards another feature or location on the map canvas
- The preview and guide line are removed when the rotation is set, the rotate operation is cancelled, or the tool is deactivated


### [Report a bug](https://github.com/matt-needle/qgis-rotate_marker_symbol/issues)
