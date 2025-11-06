# -*- coding: utf-8 -*-
"""
Visual feedback management for the Rotate Marker Symbol plugin.

This module handles all visual feedback elements including rubber bands,
snap indicators, and visual guides shown during rotation operations.
"""

from typing import List, Tuple
from qgis.core import Qgis, QgsGeometry, QgsPointXY
from qgis.gui import QgsRubberBand, QgsSnapIndicator
from qgis.PyQt.QtGui import QColor


class VisualFeedbackManager:
    """
    Manages visual feedback elements during rotation operations.
    
    This class handles:
    - Rubber bands for highlighting selected points
    - Guide lines showing rotation direction
    - Snap indicators for precise positioning
    """
    
    # Visual appearance constants
    POINT_COLOR = (0, 255, 0, 255)  # Green RGBA
    GUIDE_COLOR = (0, 0, 255, 255)  # Blue RGBA
    POINT_WIDTH = 2
    GUIDE_WIDTH = 1
    
    def __init__(self, canvas):
        """
        Initialize the visual feedback manager.
        
        Args:
            canvas: The QGIS map canvas
        """
        self.canvas = canvas
        self.rubber_bands: List[QgsRubberBand] = []
        self.guide_rubber_band: QgsRubberBand = None
        self.snap_indicator: QgsSnapIndicator = None
    
    def create_point_rubber_band(self, point: QgsPointXY):
        """
        Create a rubber band to highlight a selected point.
        
        Args:
            point: The point coordinates to highlight
        """
        rb = QgsRubberBand(self.canvas, Qgis.GeometryType.Point)
        rb.setColor(QColor(*self.POINT_COLOR))
        rb.setWidth(self.POINT_WIDTH)
        rb.addPoint(point)
        self.rubber_bands.append(rb)
    
    def create_guide_line(self):
        """
        Create a rubber band for the rotation guide line.
        
        This line shows the direction and angle of rotation as the user
        moves the mouse.
        """
        self.guide_rubber_band = QgsRubberBand(
            self.canvas, 
            Qgis.GeometryType.Line
        )
        self.guide_rubber_band.setColor(QColor(*self.GUIDE_COLOR))
        self.guide_rubber_band.setWidth(self.GUIDE_WIDTH)
        self.rubber_bands.append(self.guide_rubber_band)
    
    def update_guide_line(self, start_point: QgsPointXY, end_point: QgsPointXY):
        """
        Update the guide line to show current rotation direction.
        
        Args:
            start_point: The center point (feature location)
            end_point: The current cursor position
        """
        if self.guide_rubber_band and start_point:
            geometry = QgsGeometry.fromPolylineXY([start_point, end_point])
            self.guide_rubber_band.setToGeometry(geometry)
    
    def initialize_snap_indicator(self):
        """
        Initialize the snap indicator for precise cursor positioning.
        
        Returns:
            QgsSnapIndicator: The initialized snap indicator
        """
        self.snap_indicator = QgsSnapIndicator(self.canvas)
        return self.snap_indicator
    
    def update_snap_indicator(self, snap_match):
        """
        Update the snap indicator with the current snap match.
        
        Args:
            snap_match: The QgsPointLocator.Match object from snapping utils
        """
        if self.snap_indicator:
            self.snap_indicator.setMatch(snap_match)
    
    def remove_all_rubber_bands(self):
        """
        Remove all rubber bands from the canvas.
        
        This should be called when the tool is deactivated or when
        starting a new rotation operation.
        """
        for rubber_band in self.rubber_bands:
            self.canvas.scene().removeItem(rubber_band)
        
        self.rubber_bands.clear()
        self.guide_rubber_band = None
    
    def clear(self):
        """
        Alias for remove_all_rubber_bands for convenience.
        """
        self.remove_all_rubber_bands()
