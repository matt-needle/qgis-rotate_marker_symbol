# -*- coding: utf-8 -*-
"""
Rotation field management for the Rotate Marker Symbol plugin.

This module handles creation, validation, and updates of the rotation field
used to store feature rotation angles.
"""

from qgis.core import QgsField, QgsProperty
from qgis.PyQt.QtCore import QVariant
from .helpers import LayerEditingContext


class RotationFieldManager:
    """
    Manages the rotation field for storing feature rotation angles.
    
    This class handles all operations related to the rotation field including:
    - Checking if the field exists
    - Creating the field if needed
    - Updating rotation values
    - Setting up data-defined symbol rotation
    """
    
    ROTATION_FIELD = '__rotation__'
    
    def __init__(self, layer):
        """
        Initialize the field manager.
        
        Args:
            layer: The QgsVectorLayer to manage rotation fields for
        """
        self.layer = layer
    
    def get_field_index(self) -> int:
        """
        Get the index of the rotation field.
        
        Returns:
            int: Field index, or -1 if the field doesn't exist
        """
        return self.layer.fields().indexOf(self.ROTATION_FIELD)
    
    def field_exists(self) -> bool:
        """
        Check if the rotation field already exists in the layer.
        
        Returns:
            bool: True if the field exists, False otherwise
        """
        return self.get_field_index() >= 0
    
    def ensure_rotation_field_exists(self) -> int:
        """
        Ensure the rotation field exists, creating it if necessary.
        
        Returns:
            int: The index of the rotation field
        """
        field_index = self.get_field_index()
        
        if field_index < 0:
            self._create_rotation_field()
            field_index = self.get_field_index()
        
        return field_index
    
    def _create_rotation_field(self):
        """
        Create the rotation field in the layer.
        
        This is a private method called by ensure_rotation_field_exists.
        Uses LayerEditingContext for safe editing operations.
        """
        with LayerEditingContext(self.layer) as lyr:
            lyr.addAttribute(QgsField(self.ROTATION_FIELD, QVariant.Double))
            lyr.updateFields()
    
    def update_rotation(self, feature_id: int, field_index: int, azimuth: float):
        """
        Update the rotation value for a specific feature.
        
        Args:
            feature_id: The ID of the feature to update
            field_index: The index of the rotation field
            azimuth: The new rotation angle in degrees
        """
        with LayerEditingContext(self.layer) as lyr:
            lyr.changeAttributeValue(feature_id, field_index, azimuth)
    
    def set_data_defined_rotation(self, symbols: list):
        """
        Configure symbols to use data-defined rotation from the rotation field.
        
        This sets up the symbols to read their rotation angle from the
        rotation field attribute.
        
        Args:
            symbols: List of QgsSymbol objects to configure
        """
        property_expression = QgsProperty.fromExpression(
            f'"{self.ROTATION_FIELD}"'
        )
        
        for symbol in symbols:
            symbol.setDataDefinedAngle(property_expression)
    
    def set_dynamic_rotation(self, symbols: list, rotation: float):
        """
        Set a dynamic rotation value for symbols (used during preview).
        
        This sets a fixed rotation value that updates in real-time,
        used for visual feedback before committing the rotation.
        
        Args:
            symbols: List of QgsSymbol objects to update
            rotation: The rotation angle in degrees
        """
        prop = QgsProperty()
        prop.setExpressionString(f'{rotation}')
        
        for symbol in symbols:
            symbol.setDataDefinedAngle(prop)
