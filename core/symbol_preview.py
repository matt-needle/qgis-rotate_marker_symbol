# -*- coding: utf-8 -*-
"""
Symbol preview canvas item for the Rotate Marker Symbol plugin.

This module provides a custom QgsMapCanvasItem that renders a symbol
preview with dynamic rotation directly on the map canvas, eliminating
the need for a separate preview layer.
"""

from typing import Optional
from qgis.core import (
    QgsFeature,
    QgsPointXY,
    QgsRenderContext,
    QgsSymbol,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsRuleBasedRenderer,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas, QgsMapCanvasItem
from qgis.PyQt.QtCore import QPointF, QRectF
from qgis.PyQt.QtGui import QPainter


class SymbolPreviewCanvasItem(QgsMapCanvasItem):
    """
    A canvas item that renders a symbol preview with dynamic rotation.
    
    This class provides real-time visual feedback during rotation operations
    by rendering a symbol directly on the map canvas. It supports transparency
    to indicate that it's a preview, not the actual feature.
    
    The symbol is rendered using QgsSymbol.renderPoint() for accurate
    representation of all symbol properties including size, color, and
    complex symbol layers.
    """
    
    DEFAULT_OPACITY = 0.45  # Match the previous preview layer opacity
    
    def __init__(self, canvas: QgsMapCanvas, symbol: QgsSymbol, point: QgsPointXY):
        """
        Initialize the symbol preview canvas item.
        
        Args:
            canvas: The QGIS map canvas to render on
            symbol: The symbol to render (will be cloned internally)
            point: The map coordinates where the symbol should be rendered
        """
        super().__init__(canvas)
        
        self.canvas = canvas
        self._symbol = symbol.clone()  # Clone to avoid modifying original
        self._point = point
        self._rotation = 0.0
        self._opacity = self.DEFAULT_OPACITY
        
        # Apply initial opacity to symbol layers
        self._apply_opacity_to_symbol()
        
        # Set initial position
        self._update_position()
        
        # Make sure item is visible
        self.setVisible(True)
        self.show()
    
    def _update_position(self):
        """Update the canvas item position based on map coordinates."""
        if self._point:
            # Convert map point to canvas coordinates
            canvas_point = self.toCanvasCoordinates(self._point)
            self.setPos(canvas_point)
    
    def _apply_opacity_to_symbol(self):
        """
        Apply the current opacity to the symbol.
        
        This ensures the opacity is preserved during rendering, as the
        painter opacity can be overridden by the symbol's own rendering.
        """
        if not self._symbol:
            return
        
        # QgsSymbol has setOpacity at the symbol level
        self._symbol.setOpacity(self._opacity)
    
    def setRotation(self, angle: float):
        """
        Set the rotation angle for the symbol preview.
        
        Args:
            angle: The rotation angle in degrees (azimuth)
        """
        self._rotation = angle
        
        # Apply rotation to the symbol
        # For marker symbols, we can set the angle directly
        if hasattr(self._symbol, 'setAngle'):
            self._symbol.setAngle(angle)
        
        # Request repaint
        self.update()
    
    def setOpacity(self, opacity: float):
        """
        Set the opacity of the symbol preview.
        
        Args:
            opacity: Opacity value between 0.0 (transparent) and 1.0 (opaque)
        """
        self._opacity = max(0.0, min(1.0, opacity))
        self._apply_opacity_to_symbol()
        self.update()
    
    def boundingRect(self) -> QRectF:
        """
        Return the bounding rectangle for the canvas item.
        
        This determines the area that needs to be repainted when the
        item is updated. We use a generous size to accommodate large symbols.
        """
        # Use a reasonable size that should cover most symbols
        # The actual symbol size is determined by the render context
        size = 100  # pixels - should be enough for most marker symbols
        return QRectF(-size, -size, size * 2, size * 2)
    
    def paint(self, painter: QPainter, option=None, widget=None):
        """
        Paint the symbol on the canvas.
        
        This method is called by Qt whenever the item needs to be redrawn.
        It creates a render context and uses QgsSymbol.renderPoint() to
        draw the symbol with the current rotation.
        
        Args:
            painter: The QPainter to draw with
            option: Style options (unused)
            widget: The widget being painted on (unused)
        """
        if not self._symbol or not self._point:
            return
        
        # Save painter state
        painter.save()
        
        # Apply opacity
        painter.setOpacity(self._opacity)
        
        # Create render context from painter
        render_context = QgsRenderContext.fromQPainter(painter)
        
        if render_context:
            # Start rendering the symbol
            self._symbol.startRender(render_context)
            
            try:
                # Render at origin (0, 0) since we've already positioned the item
                self._symbol.renderPoint(QPointF(0, 0), None, render_context)
            finally:
                # Always stop rendering
                self._symbol.stopRender(render_context)
        
        # Restore painter state
        painter.restore()
    
    def updatePosition(self):
        """
        Update position when the map canvas is panned or zoomed.
        
        This is called automatically by the canvas when the view changes.
        """
        self._update_position()


class SymbolPreviewManager:
    """
    Manages the symbol preview canvas item lifecycle.
    
    This class handles creating, updating, and removing the symbol preview
    during rotation operations. It also provides methods for extracting
    the appropriate symbol from different renderer types.
    """
    
    def __init__(self, canvas: QgsMapCanvas):
        """
        Initialize the symbol preview manager.
        
        Args:
            canvas: The QGIS map canvas
        """
        self.canvas = canvas
        self.preview_item: Optional[SymbolPreviewCanvasItem] = None
    
    def create_preview(self, point: QgsPointXY, symbol: QgsSymbol, 
                       initial_rotation: float = 0.0) -> SymbolPreviewCanvasItem:
        """
        Create a new symbol preview at the specified point.
        
        Args:
            point: Map coordinates for the preview
            symbol: The symbol to preview
            initial_rotation: Initial rotation angle in degrees
            
        Returns:
            The created SymbolPreviewCanvasItem
        """
        # Remove any existing preview
        self.remove_preview()
        
        # Create new preview item
        self.preview_item = SymbolPreviewCanvasItem(self.canvas, symbol, point)
        self.preview_item.setRotation(initial_rotation)
        
        return self.preview_item
    
    def update_rotation(self, angle: float):
        """
        Update the preview symbol rotation.
        
        Args:
            angle: The new rotation angle in degrees
        """
        if self.preview_item:
            self.preview_item.setRotation(angle)
    
    def remove_preview(self):
        """Remove the current symbol preview from the canvas."""
        if self.preview_item:
            # Remove from canvas scene
            scene = self.canvas.scene()
            if scene and self.preview_item in scene.items():
                scene.removeItem(self.preview_item)
            self.preview_item = None
    
    @staticmethod
    def get_feature_symbol(layer: QgsVectorLayer, feature: QgsFeature) -> Optional[QgsSymbol]:
        """
        Get the symbol used to render a specific feature.
        
        This method handles different renderer types (single symbol,
        categorized, graduated, rule-based) to return the correct symbol
        for the given feature.
        
        Args:
            layer: The layer containing the feature
            feature: The feature to get the symbol for
            
        Returns:
            The QgsSymbol used for this feature, or None if not found
        """
        if not layer or not feature:
            return None
        
        renderer = layer.renderer()
        if not renderer:
            return None
        
        # Create a render context for symbol resolution
        render_context = QgsRenderContext()
        
        # Single symbol renderer
        if isinstance(renderer, QgsSingleSymbolRenderer):
            return renderer.symbol().clone()
        
        # Categorized renderer
        elif isinstance(renderer, QgsCategorizedSymbolRenderer):
            # Get the symbol for this feature's category
            symbol = renderer.symbolForFeature(feature, render_context)
            return symbol.clone() if symbol else None
        
        # Graduated renderer
        elif isinstance(renderer, QgsGraduatedSymbolRenderer):
            symbol = renderer.symbolForFeature(feature, render_context)
            return symbol.clone() if symbol else None
        
        # Rule-based renderer
        elif isinstance(renderer, QgsRuleBasedRenderer):
            symbol = renderer.symbolForFeature(feature, render_context)
            return symbol.clone() if symbol else None
        
        # Fallback: try generic symbolForFeature
        elif hasattr(renderer, 'symbolForFeature'):
            symbol = renderer.symbolForFeature(feature, render_context)
            return symbol.clone() if symbol else None
        
        # Last resort: try to get any symbol
        elif hasattr(renderer, 'symbol'):
            return renderer.symbol().clone()
        
        return None
