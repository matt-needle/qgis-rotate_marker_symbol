# Rotate Marker Symbol
![rotate_marker_symbol_demo](https://github.com/user-attachments/assets/379220eb-beab-42fd-b1ed-d5acc01c68db)

### How to use
- Activate the tool from the tool bar
- Select a point layer from the Layers Panel (with a Single Symbol, Categorized, Graduated, or Rule-based renderer)
- Left-click a point to begin rotating
- Use the guideline to rotate exactly where desired
- Left-click again to modify its rotation -- Or -- Right-click to cancel

### How it works
- A field named `__rotation__` is added to the original point layer. This field is updated with the chosen rotation angle
- The clicked feature is copied to a private temporary layer to create the semi-transparent preview symbol
- The preview layer is removed from the project when the tool is deactivated

### Known issues
- If the QGIS application is closed while the symbol preview is visible, the (empty) temporary preview layer will persist in the project

### [Report a bug](https://github.com/matt-needle/qgis-rotate_marker_symbol/issues)
