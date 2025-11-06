# -*- coding: utf-8 -*-
"""
Snapping configuration for the Rotate Marker Symbol plugin.

This module handles the setup and management of snapping behavior for
precise feature selection and rotation operations.
"""

from qgis.core import QgsProject, QgsSnappingConfig, QgsTolerance


class SnappingConfigManager:
    """
    Manages snapping configuration for the rotation tool.
    
    Configures snapping to allow users to precisely select features
    and align rotation angles with other features.
    """
    
    # Snapping tolerance in pixels
    SNAP_TOLERANCE = 11
    
    def __init__(self, project: QgsProject):
        """
        Initialize the snapping configuration manager.
        
        Args:
            project: The QGIS project instance
        """
        self.project = project
    
    def configure_snapping(self):
        """
        Configure snapping settings for the rotation tool.
        
        Sets up snapping to work with the active layer, targeting vertices
        with a tolerance specified in pixels.
        """
        snap_config = QgsSnappingConfig(self.project)
        snap_config.setEnabled(True)
        snap_config.setMode(QgsSnappingConfig.ActiveLayer)
        snap_config.setType(QgsSnappingConfig.Vertex)
        snap_config.setTolerance(self.SNAP_TOLERANCE)
        snap_config.setUnits(QgsTolerance.Pixels)
        
        self.project.setSnappingConfig(snap_config)
    
    def get_snap_config(self) -> QgsSnappingConfig:
        """
        Get the current snapping configuration.
        
        Returns:
            QgsSnappingConfig: The current snapping configuration
        """
        return self.project.snappingConfig()
