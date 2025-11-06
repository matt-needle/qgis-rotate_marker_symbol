# -*- coding: utf-8 -*-
"""
Helper classes and utilities for the Rotate Marker Symbol plugin.

This module provides reusable components for layer editing, messaging,
and common operations.
"""

from contextlib import contextmanager
from enum import IntEnum
from qgis.core import Qgis


class MouseButton(IntEnum):
    """Mouse button constants for better code readability."""
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class LayerEditingContext:
    """
    Context manager for safe layer editing operations.
    
    Automatically handles starting/committing edits and rolls back on errors.
    Only starts editing if the layer wasn't already in edit mode.
    
    Example:
        with LayerEditingContext(layer) as lyr:
            lyr.addAttribute(QgsField("new_field", QVariant.Double))
            lyr.updateFields()
    """
    
    def __init__(self, layer):
        """
        Initialize the context manager.
        
        Args:
            layer: The QgsVectorLayer to manage editing for
        """
        self.layer = layer
        self.was_editing = layer.isEditable()
    
    def __enter__(self):
        """Start editing if not already editing."""
        if not self.was_editing:
            self.layer.startEditing()
        return self.layer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Commit or rollback changes based on whether an exception occurred.
        
        Returns:
            False to propagate any exceptions that occurred
        """
        if not self.was_editing:
            if exc_type is None:
                self.layer.commitChanges()
            else:
                self.layer.rollBack()
        return False


class MessageHelper:
    """
    Helper class for displaying consistent user messages.
    
    Provides convenient methods for showing errors, warnings, and info messages
    through the QGIS message bar.
    """
    
    DEFAULT_DURATION = 5
    
    def __init__(self, iface):
        """
        Initialize the message helper.
        
        Args:
            iface: The QGIS interface instance
        """
        self.iface = iface
    
    def show_error(self, message, level=Qgis.Warning, duration=None):
        """
        Display an error message in the QGIS message bar.
        
        Args:
            message (str): The error message to display
            level (Qgis.MessageLevel): The severity level of the message
            duration (int): How long to show the message in seconds
        """
        if duration is None:
            duration = self.DEFAULT_DURATION
            
        self.iface.messageBar().pushMessage(
            "Error",
            message,
            level=level,
            duration=duration
        )
    
    def show_warning(self, message, duration=None):
        """
        Display a warning message.
        
        Args:
            message (str): The warning message to display
            duration (int): How long to show the message in seconds
        """
        self.show_error(message, level=Qgis.Warning, duration=duration)
    
    def show_critical(self, message, duration=None):
        """
        Display a critical error message.
        
        Args:
            message (str): The critical error message to display
            duration (int): How long to show the message in seconds
        """
        self.show_error(message, level=Qgis.Critical, duration=duration)
    
    def show_info(self, message, duration=None):
        """
        Display an informational message.
        
        Args:
            message (str): The info message to display
            duration (int): How long to show the message in seconds
        """
        if duration is None:
            duration = self.DEFAULT_DURATION
            
        self.iface.messageBar().pushMessage(
            "Info",
            message,
            level=Qgis.Info,
            duration=duration
        )
