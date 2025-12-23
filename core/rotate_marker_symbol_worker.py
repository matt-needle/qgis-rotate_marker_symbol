# -*- coding: utf-8 -*-
"""
Main map tool for the Rotate Marker Symbol plugin.

This module provides the PointSymbolRotator map tool, which allows users to
interactively rotate point marker symbols by clicking a point and dragging
to set the rotation angle.
"""

from qgis.core import QgsProject
from qgis.gui import QgsMapToolIdentifyFeature, QgsMapToolIdentify
from qgis.PyQt.QtCore import QVariant

from .helpers import LayerEditingContext, MessageHelper, MouseButton
from .validators import LayerValidator
from .field_manager import RotationFieldManager
from .visual_feedback import VisualFeedbackManager
from .rotation_state import RotationState
from .snapping_config import SnappingConfigManager
from .symbol_preview import SymbolPreviewManager


class PointSymbolRotator(QgsMapToolIdentifyFeature):
    """
    A QGIS map tool for manually rotating point marker symbols.
    
    This tool allows users to:
    1. Click on a point feature to select it
    2. Move the mouse to visually set the rotation angle
    3. Click again to apply the rotation
    4. Right-click to cancel
    
    The rotation is stored in a field named '__rotation__' and applied
    via data-defined symbol rotation.
    
    The tool provides real-time visual feedback through:
    - A highlighted point showing the selected feature
    - A guide line showing the rotation direction
    - A symbol preview showing the rotated symbol directly on canvas
    - Snapping to allow precise angle alignment
    """
    
    def __init__(self, canvas, iface, project=None):
        """
        Initialize the rotation tool.
        
        Args:
            canvas: The QGIS map canvas
            iface: The QGIS interface instance
            project: The QGIS project (defaults to current project)
        """
        super().__init__(canvas)
        
        self.canvas = canvas
        self.iface = iface
        self.project = project or QgsProject.instance()
        self.layer = iface.activeLayer()
        
        # Initialize component managers
        self.message_helper = MessageHelper(iface)
        self.validator = LayerValidator(self.message_helper)
        self.visual_manager = VisualFeedbackManager(canvas)
        self.snapping_manager = SnappingConfigManager(self.project)
        
        # State management
        self.state = RotationState()
        
        # Field manager will be created when we have a valid layer
        self.field_manager = None
        
        # Validate initial layer
        self.is_valid = self.validator.validate(self.layer) if self.layer else False
        
        # Set up snapping
        self.snapping_manager.configure_snapping()
        self.snap_indicator = self.visual_manager.initialize_snap_indicator()
        self.snap_utils = canvas.snappingUtils()
        
        # Connect to layer selection changes
        self.iface.layerTreeView().currentLayerChanged.connect(self.on_layer_changed)
        
        # Connect deactivation signal
        self.deactivated.connect(self.on_deactivate)
    
    def canvasPressEvent(self, event):
        """
        Handle mouse press events on the canvas.
        
        This method is called when the user clicks on the canvas.
        It validates the active layer and prepares for rotation.
        
        Args:
            event: The mouse event
        """
        # Update layer reference in case it changed
        self.layer = self.iface.activeLayer()
        
        # Revalidate if layer changed
        self.is_valid = self.validator.validate(self.layer) if self.layer else False
        
        if not self.is_valid:
            return
        
        # Initialize field manager for this layer
        if not self.field_manager or self.field_manager.layer != self.layer:
            self.field_manager = RotationFieldManager(self.layer)
    
    def canvasReleaseEvent(self, event):
        """
        Handle mouse release events on the canvas.
        
        This method handles three cases:
        1. Left/middle click when not drawing: Start rotation operation
        2. Left/middle click when drawing: Commit rotation
        3. Right click: Cancel rotation
        
        Args:
            event: The mouse event
        """
        if not self.is_valid:
            return
        
        button = event.button()
        
        # Case 1: Start rotation operation
        if button in (MouseButton.LEFT, MouseButton.MIDDLE) and not self.state.drawing_guide:
            self._start_rotation(event)
        
        # Case 2: Commit rotation
        elif button in (MouseButton.LEFT, MouseButton.MIDDLE) and self.state.drawing_guide:
            self._commit_rotation()
        
        # Case 3: Cancel rotation
        elif button == MouseButton.RIGHT:
            self._cancel_rotation()
    
    def canvasMoveEvent(self, event):
        """
        Handle mouse move events on the canvas.
        
        This method updates the visual feedback (guide line and preview)
        as the user moves the mouse during rotation.
        
        Args:
            event: The mouse event
        """
        if not self.is_valid:
            return
        
        # Update snap indicator
        snap_match = self.snap_utils.snapToMap(event.pos())
        self.visual_manager.update_snap_indicator(snap_match)
        
        # Update guide line and preview if actively rotating
        if self.state.drawing_guide and self.state.src_point:
            # Update guide line
            end_point = event.mapPoint()
            self.visual_manager.update_guide_line(self.state.src_point, end_point)
            
            # Calculate and store azimuth (normalized to 0-360)
            raw_azimuth = self.state.src_point.azimuth(end_point)
            self.state.set_azimuth(raw_azimuth)
            
            # Update preview with current rotation
            self.visual_manager.update_symbol_rotation(self.state.azimuth)
    
    def _start_rotation(self, event):
        """
        Start a new rotation operation.
        
        This identifies the clicked feature, sets up visual feedback,
        and prepares the preview layer.
        
        Args:
            event: The mouse event
        """
        # Identify feature at click location
        identify_results = self.identify(
            event.x(),
            event.y(),
            QgsMapToolIdentify.ActiveLayer,
            QgsMapToolIdentify.VectorLayer
        )
        
        if not identify_results:
            return
        
        # Get the feature
        feature = identify_results[0].mFeature
        
        # Ensure rotation field exists
        field_index = self.field_manager.ensure_rotation_field_exists()
        
        # Set up data-defined rotation on the original layer
        layer_symbols = self._get_layer_symbols()
        self.field_manager.set_data_defined_rotation(layer_symbols)
        
        # Initialize state
        self.state.start_rotation(feature, field_index)
        
        # Set up visual feedback
        self.visual_manager.create_point_rubber_band(self.state.src_point)
        self.visual_manager.create_guide_line()
        
        # Create symbol preview with the feature's symbol
        symbol = self._get_feature_symbol(feature)
        if symbol:
            self.visual_manager.create_symbol_preview(self.state.src_point, symbol)
    
    def _commit_rotation(self):
        """
        Commit the current rotation to the layer.
        
        This saves the rotation angle to the rotation field and
        cleans up the visual feedback.
        """
        if not self.state.is_active or self.state.azimuth is None:
            return
        
        # Update the rotation attribute
        self.field_manager.update_rotation(
            self.state.feature_id,
            self.state.rotation_field_index,
            self.state.azimuth
        )
        
        # Clean up
        self._cleanup_after_rotation()
        self.canvas.refresh()
    
    def _cancel_rotation(self):
        """
        Cancel the current rotation operation without saving changes.
        """
        self._cleanup_after_rotation()
    
    def _cleanup_after_rotation(self):
        """
        Clean up visual feedback and state after rotation is complete or canceled.
        """
        self.visual_manager.clear()
        self.state.reset()
    
    def _get_layer_symbols(self) -> list:
        """
        Get all symbols from the current layer's renderer.
        
        Returns:
            list: List of QgsSymbol objects
        """
        from qgis.core import (
            QgsRenderContext,
            QgsCategorizedSymbolRenderer,
            QgsGraduatedSymbolRenderer,
            QgsRuleBasedRenderer
        )
        
        if not self.layer:
            return []
        
        renderer = self.layer.renderer()
        symbols = []
        
        if isinstance(renderer, (QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer)):
            symbols = renderer.symbols(QgsRenderContext())
        elif isinstance(renderer, QgsRuleBasedRenderer):
            root_rule = renderer.rootRule()
            symbols = root_rule.symbols()
        elif hasattr(renderer, "symbol"):
            symbols = [renderer.symbol()]
        
        return symbols
    
    def _get_feature_symbol(self, feature):
        """
        Get the symbol used to render a specific feature.
        
        This method handles different renderer types (single symbol,
        categorized, graduated, rule-based) to return the correct symbol
        for the given feature.
        
        Args:
            feature: The QgsFeature to get the symbol for
            
        Returns:
            QgsSymbol: The symbol for this feature, or None if not found
        """
        return SymbolPreviewManager.get_feature_symbol(self.layer, feature)
    
    def on_layer_changed(self, layer):
        """
        Handle layer selection changes in the layer tree.
        
        This method is called when the user selects a different layer
        in the layer tree, updating the active layer for the plugin.
        
        Args:
            layer: The newly selected layer
        """
        # Only update if we actually have a layer
        if layer is None:
            self.layer = None
            self.is_valid = False
            return
        
        # Update the active layer reference
        self.layer = layer
        
        # Validate the new layer
        self.is_valid = self.validator.validate(self.layer) if self.layer else False
        
        # Reset field manager if layer changed
        if self.layer and (not self.field_manager or self.field_manager.layer != self.layer):
            self.field_manager = RotationFieldManager(self.layer)
        
        # Cancel any active rotation when layer changes
        if self.state.is_active:
            self._cleanup_after_rotation()
    
    def on_deactivate(self):
        """
        Handle tool deactivation.
        
        This cleans up all visual feedback and disconnects layer change signal.
        """
        # Disconnect layer change signal
        try:
            self.iface.layerTreeView().currentLayerChanged.disconnect(self.on_layer_changed)
        except (TypeError, RuntimeError):
            # Signal was already disconnected
            pass
        
        self.visual_manager.clear()
        self.state.reset()
    
    def __del__(self):
        """
        Destructor to ensure cleanup even if tool is garbage collected.
        
        This handles the case where QGIS is closed while the tool is active,
        ensuring the preview layer doesn't persist in the project file.
        """
        try:
            self.preview_manager.cleanup()
            self.visual_manager.clear()
        except (AttributeError, RuntimeError):
            # Objects may already be destroyed
            pass
    
    def remove_rubber_bands(self):
        """
        Remove all rubber bands from the canvas.
        
        Public method for external cleanup if needed.
        """
        self.visual_manager.clear()
    
    def get_uuid(self) -> str:
        """
        Get the UUID used for the preview layer.
        
        Returns:
            str: The UUID string
        """
        return self.preview_manager.UUID


# Backwards compatibility: Keep old method names as aliases
# This ensures existing code that uses the old worker still functions
class PointSymbolRotatorLegacy(PointSymbolRotator):
    """
    Legacy compatibility class.
    
    This class maintains the old interface for backwards compatibility
    while using the new refactored implementation internally.
    """
    
    def get_identify_results(self):
        """Legacy method - returns current feature."""
        return [self.state.feature] if self.state.feature else None
    
    def get_layer(self):
        """Legacy method - returns current layer."""
        return self.layer
    
    def get_preview_layer(self):
        """Legacy method - returns preview layer."""
        return self.preview_manager.get_layer()
