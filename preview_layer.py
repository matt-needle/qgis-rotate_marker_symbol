# -*- coding: utf-8 -*-
"""
Preview layer management for the Rotate Marker Symbol plugin.

This module handles the creation and management of a temporary preview layer
that shows the rotation effect in real-time before committing changes.
"""

from typing import Optional
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsMapLayer,
    QgsProject,
    QgsRenderContext,
    QgsVectorLayer,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsRuleBasedRenderer
)
from .helpers import LayerEditingContext


class PreviewLayerManager:
    """
    Manages a temporary preview layer for real-time rotation feedback.
    
    The preview layer is a memory layer that mirrors the source layer's
    symbology and shows how the rotation will look before it's applied.
    
    This manager also handles cleanup when the project is closed or saved,
    preventing the preview layer from persisting in the project file.
    """
    
    UUID = 'rotate_points_tool-c848-4cd7-924d-1e9522d3aef4'
    DEFAULT_OPACITY = 0.45
    
    def __init__(self, project: QgsProject, iface):
        """
        Initialize the preview layer manager.
        
        Connects to project signals to ensure cleanup when:
        - Project is saved (writeProject)
        - Project is closed (aboutToBeCleared)
        
        Args:
            project: The QGIS project instance
            iface: The QGIS interface instance
        """
        self.project = project
        self.iface = iface
        self.preview_layer: Optional[QgsVectorLayer] = None
        self._signals_connected = False
        
        # Connect to project signals for cleanup
        self._connect_project_signals()
    
    def get_or_create_preview_layer(self, source_layer: QgsVectorLayer) -> QgsVectorLayer:
        """
        Get the existing preview layer or create a new one.
        
        Args:
            source_layer: The source layer to create a preview for
        
        Returns:
            QgsVectorLayer: The preview layer
        """
        # Check if preview layer already exists
        existing_layers = self.project.mapLayersByName(self.UUID)
        
        if existing_layers:
            self.preview_layer = existing_layers[0]
        else:
            self.preview_layer = self._create_preview_layer(source_layer)
            self.project.addMapLayer(self.preview_layer)
        
        return self.preview_layer
    
    def _create_preview_layer(self, source_layer: QgsVectorLayer) -> QgsVectorLayer:
        """
        Create a new preview layer.
        
        Args:
            source_layer: The source layer to base the preview on
        
        Returns:
            QgsVectorLayer: The newly created preview layer
        """
        layer = QgsVectorLayer("Point", self.UUID, "memory")
        layer.setCrs(source_layer.crs())
        layer.setFlags(QgsMapLayer.Private | QgsMapLayer.Removable)
        layer.setOpacity(self.DEFAULT_OPACITY)
        
        return layer
    
    def update_fields(self, source_layer: QgsVectorLayer):
        """
        Update the preview layer's fields to match the source layer.
        
        Args:
            source_layer: The source layer to copy fields from
        """
        if not self.preview_layer:
            return
        
        with LayerEditingContext(self.preview_layer) as lyr:
            # Remove all existing fields
            field_count = len(lyr.fields())
            if field_count > 0:
                lyr.deleteAttributes(list(range(field_count)))
            lyr.updateFields()
        
        # Add fields from source layer
        with LayerEditingContext(self.preview_layer) as lyr:
            lyr.dataProvider().addAttributes(source_layer.fields())
            lyr.updateFields()
    
    def clear_features(self):
        """
        Remove all features from the preview layer.
        """
        if not self.preview_layer:
            return
        
        with LayerEditingContext(self.preview_layer) as lyr:
            feature_ids = [f.id() for f in lyr.getFeatures()]
            if feature_ids:
                lyr.deleteFeatures(feature_ids)
    
    def set_preview_feature(self, feature: QgsFeature):
        """
        Set or update the preview feature in the preview layer.
        
        Args:
            feature: The feature to preview
        """
        if not self.preview_layer:
            return
        
        with LayerEditingContext(self.preview_layer) as lyr:
            # Check if there's already a preview feature
            existing_features = list(lyr.getFeatures())
            
            if existing_features:
                # Update existing feature
                preview_feature = existing_features[0]
                preview_feature.setGeometry(feature.geometry())
                lyr.updateFeature(preview_feature)
            else:
                # Add new feature
                new_feature = QgsFeature()
                new_feature.setAttributes(feature.attributes())
                new_feature.setGeometry(feature.geometry())
                lyr.dataProvider().addFeatures([new_feature])
        
        self.iface.mapCanvas().refresh()
    
    def copy_renderer(self, source_layer: QgsVectorLayer):
        """
        Copy the renderer from the source layer to the preview layer.
        
        Args:
            source_layer: The layer to copy the renderer from
        """
        if not self.preview_layer or not source_layer.renderer():
            return
        
        renderer_clone = source_layer.renderer().clone()
        self.preview_layer.setRenderer(renderer_clone)
        self.preview_layer.triggerRepaint()
    
    def get_symbols(self) -> list:
        """
        Get all symbols from the preview layer's renderer.
        
        Returns:
            list: List of QgsSymbol objects
        """
        if not self.preview_layer:
            return []
        
        renderer = self.preview_layer.renderer()
        symbols = []
        
        if isinstance(renderer, (QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer)):
            symbols = renderer.symbols(QgsRenderContext())
        elif isinstance(renderer, QgsRuleBasedRenderer):
            root_rule = renderer.rootRule()
            symbols = root_rule.symbols()
        elif hasattr(renderer, "symbol"):
            symbols = [renderer.symbol()]
        
        return symbols
    
    def remove_from_project(self):
        """
        Remove the preview layer from the project.
        
        This should be called when the tool is deactivated.
        """
        if self.preview_layer:
            try:
                self.project.removeMapLayer(self.preview_layer)
            except RuntimeError as e:
                # Layer may have already been removed
                # Log this but don't fail
                pass
            finally:
                self.preview_layer = None
    
    def get_layer(self) -> Optional[QgsVectorLayer]:
        """
        Get the current preview layer.
        
        Returns:
            QgsVectorLayer or None: The preview layer if it exists
        """
        return self.preview_layer
    
    def _connect_project_signals(self):
        """
        Connect to project signals for automatic cleanup.
        
        This ensures the preview layer is removed before:
        - The project is saved (prevents it from being saved in the project file)
        - The project is closed (cleanup)
        """
        if not self._signals_connected:
            # Remove preview layer before project is saved
            self.project.writeProject.connect(self._cleanup_before_save)
            
            # Remove preview layer when project is about to be cleared/closed
            self.project.aboutToBeCleared.connect(self._cleanup_on_close)
            
            self._signals_connected = True
    
    def _disconnect_project_signals(self):
        """
        Disconnect from project signals.
        
        Should be called when the manager is no longer needed.
        """
        if self._signals_connected:
            try:
                self.project.writeProject.disconnect(self._cleanup_before_save)
                self.project.aboutToBeCleared.disconnect(self._cleanup_on_close)
            except TypeError:
                # Signal was already disconnected
                pass
            
            self._signals_connected = False
    
    def _cleanup_before_save(self):
        """
        Clean up preview layer before project is saved.
        
        This prevents the temporary preview layer from being saved
        in the project file. Called automatically when writeProject signal fires.
        """
        if self.preview_layer:
            # Remove the preview layer so it doesn't get saved
            self.remove_from_project()
    
    def _cleanup_on_close(self):
        """
        Clean up preview layer when project is closing.
        
        Called automatically when aboutToBeCleared signal fires.
        """
        if self.preview_layer:
            # Clean up the preview layer
            self.remove_from_project()
    
    def cleanup(self):
        """
        Complete cleanup of the preview layer manager.
        
        Removes the preview layer and disconnects all signals.
        Should be called when the tool is completely finished.
        """
        self.remove_from_project()
        self._disconnect_project_signals()
