# -*- coding: utf-8 -*-
"""
Validation logic for the Rotate Marker Symbol plugin.

This module handles validation of layers and renderers to ensure they are
compatible with the rotation tool.
"""

from qgis.core import (
    Qgis,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsRuleBasedRenderer,
    QgsGraduatedSymbolRenderer
)
from .helpers import MessageHelper


class LayerValidator:
    """
    Validates layers and renderers for rotation tool compatibility.
    
    This class encapsulates all validation logic, providing clear separation
    of concerns from the main tool logic.
    """
    
    def __init__(self, message_helper: MessageHelper):
        """
        Initialize the validator.
        
        Args:
            message_helper: MessageHelper instance for displaying validation errors
        """
        self.message_helper = message_helper
    
    def validate_layer(self, layer) -> bool:
        """
        Validate that the layer exists and has point geometry.
        
        Args:
            layer: The layer to validate (can be None)
        
        Returns:
            bool: True if the layer is valid, False otherwise
        """
        if not layer:
            self.message_helper.show_warning(
                'There is no active layer in the Layers panel'
            )
            return False
        
        is_valid = (
            isinstance(layer, QgsVectorLayer) and 
            layer.wkbType() == QgsWkbTypes.Point
        )
        
        if not is_valid:
            self.message_helper.show_critical(
                'The active layer must have Point geometry'
            )
        
        return is_valid
    
    def validate_renderer(self, renderer) -> bool:
        """
        Validate that the renderer is compatible with rotation.
        
        Compatible renderers are: Single Symbol, Categorized, Graduated, 
        and Rule-based renderers.
        
        Args:
            renderer: The renderer to validate
        
        Returns:
            bool: True if the renderer is compatible, False otherwise
        """
        is_valid = isinstance(
            renderer,
            (QgsSingleSymbolRenderer,
             QgsCategorizedSymbolRenderer,
             QgsRuleBasedRenderer,
             QgsGraduatedSymbolRenderer)
        )
        
        if not is_valid:
            self.message_helper.show_critical(
                'The active layer does not have a compatible Marker renderer. '
                'Supported types: Single Symbol, Categorized, Graduated, Rule-based'
            )
        
        return is_valid
    
    def validate(self, layer) -> bool:
        """
        Perform complete validation of layer and renderer.
        
        Args:
            layer: The layer to validate
        
        Returns:
            bool: True if both layer and renderer are valid, False otherwise
        """
        if not layer:
            return False
            
        if not self.validate_layer(layer):
            return False
        
        if not self.validate_renderer(layer.renderer()):
            return False
        
        return True
