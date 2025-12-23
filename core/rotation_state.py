# -*- coding: utf-8 -*-
"""
State management for the Rotate Marker Symbol plugin.

This module provides a clean way to manage the state during rotation operations,
making it easier to track and reset state between operations.
"""

from dataclasses import dataclass, field
from typing import Optional
from qgis.core import QgsFeature, QgsPointXY


@dataclass
class RotationState:
    """
    Encapsulates the state during a rotation operation.
    
    This data class holds all the state information needed during an
    active rotation operation, making it easy to reset and manage state.
    
    Attributes:
        feature: The feature currently being rotated
        feature_id: The ID of the feature being rotated
        src_point: The source point (center of rotation)
        drawing_guide: Whether the guide line is currently being drawn
        azimuth: The current rotation angle in degrees
        rotation_field_index: The index of the rotation field in the layer
        is_active: Whether a rotation operation is currently active
    """
    
    feature: Optional[QgsFeature] = None
    feature_id: Optional[int] = None
    src_point: Optional[QgsPointXY] = None
    drawing_guide: bool = False
    azimuth: Optional[float] = None
    rotation_field_index: int = -1
    is_active: bool = False
    
    def reset(self):
        """
        Reset all state to initial values.
        
        This should be called when completing or canceling a rotation operation.
        """
        self.feature = None
        self.feature_id = None
        self.src_point = None
        self.drawing_guide = False
        self.azimuth = None
        self.rotation_field_index = -1
        self.is_active = False
    
    def start_rotation(self, feature: QgsFeature, field_index: int):
        """
        Initialize state for a new rotation operation.
        
        Args:
            feature: The feature to rotate
            field_index: The index of the rotation field
        """
        self.feature = feature
        self.feature_id = feature.id()
        self.src_point = feature.geometry().asPoint()
        self.rotation_field_index = field_index
        self.drawing_guide = True
        self.is_active = True
    
    def set_azimuth(self, raw_azimuth: float):
        """
        Set the azimuth, normalizing from -180 to 180 range to 0 to 360 range.
        
        QgsPointXY.azimuth() returns values from -180 to 180,
        but we want to store rotation as 0 to 360.
        
        Args:
            raw_azimuth: The raw azimuth value from QgsPointXY.azimuth()
        """
        # Normalize from -180..180 to 0..360
        if raw_azimuth < 0:
            self.azimuth = raw_azimuth + 360.0
        else:
            self.azimuth = raw_azimuth
    
    def finish_rotation(self):
        """
        Complete the current rotation operation and reset state.
        """
        self.reset()
