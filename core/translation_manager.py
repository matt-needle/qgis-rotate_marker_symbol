# -*- coding: utf-8 -*-
"""
Translation Manager - Reusable Translation Handler for QGIS Plugins

A reusable class for handling translations in QGIS plugins. This module
provides a simple, consistent way to add internationalization support to
any QGIS plugin.

Usage:
    from .core.translation_manager import TranslationManager
    
    class YourPlugin:
        def __init__(self, iface):
            self.translation_manager = TranslationManager(
                plugin_name='YourPluginName',
                plugin_dir=os.path.dirname(__file__)
            )
        
        def tr(self, message):
            return self.translation_manager.tr(message)

Author: Matt Needle
License: GPL v2+
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication


class TranslationManager:
    """
    Manages translations for QGIS plugins.
    
    This class handles loading translation files (.qm) based on the user's
    locale settings in QGIS. It provides a simple interface for translating
    strings throughout the plugin.
    
    Translation files should be placed in an 'i18n' directory within the
    plugin folder, named with the language code (e.g., nl.qm, de.qm, fr.qm).
    
    Attributes:
        plugin_name: The name of the plugin (used as translation context)
        plugin_dir: Path to the plugin directory
        translator: The QTranslator instance for this plugin
        locale: The current locale code (e.g., 'nl', 'de', 'fr')
    
    Example:
        >>> tm = TranslationManager('MyPlugin', '/path/to/plugin')
        >>> translated = tm.tr('Hello World')
    """
    
    def __init__(self, plugin_name, plugin_dir):
        """
        Initialize the translation manager.
        
        Args:
            plugin_name: Name of the plugin (used as translation context)
            plugin_dir: Absolute path to the plugin directory
        """
        self.plugin_name = plugin_name
        self.plugin_dir = plugin_dir
        self.translator = None
        self.locale = None
        
        # Automatically load translations on initialization
        self._load_translation()
    
    def _load_translation(self):
        """
        Load the translation file for the current locale.
        
        This method:
        1. Gets the user's locale from QGIS settings
        2. Looks for a matching .qm file in the i18n directory
        3. Loads and installs the translator if found
        
        Translation files should be named: <locale>.qm
        Examples: nl.qm, de.qm, fr.qm, es.qm
        """
        # Get the locale from QGIS settings (e.g., 'nl_NL' -> 'nl')
        locale_setting = QSettings().value('locale/userLocale', 'en')
        self.locale = locale_setting[0:2] if locale_setting else 'en'
        
        # Build path to translation file
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            f'{self.locale}.qm'
        )
        
        # Load translation if file exists
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)
                return True
        
        # No translation file found - plugin will use English source strings
        return False
    
    def tr(self, message):
        """
        Translate a string using the loaded translation.
        
        This method should be called for all user-facing strings in the plugin.
        If no translation is available, the original English string is returned.
        
        Args:
            message: The English string to translate
        
        Returns:
            str: The translated string, or the original if no translation exists
        
        Example:
            >>> tm.tr('Please select a layer')
            'Selecteer een laag'  # if using Dutch (nl) translation
        """
        return QCoreApplication.translate(self.plugin_name, message)
    
    def get_locale(self):
        """
        Get the current locale code.
        
        Returns:
            str: The two-letter locale code (e.g., 'nl', 'de', 'fr')
        """
        return self.locale
    
    def is_translation_loaded(self):
        """
        Check if a translation file was successfully loaded.
        
        Returns:
            bool: True if a translation is loaded, False otherwise
        """
        return self.translator is not None
    
    def unload(self):
        """
        Unload the translator.
        
        This should be called when the plugin is unloaded to clean up resources.
        """
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None


# Convenience function for simple use cases
def create_translator(plugin_name, plugin_dir):
    """
    Create and return a translation manager instance.
    
    This is a convenience function for simple plugins that don't need
    to store the TranslationManager as an instance variable.
    
    Args:
        plugin_name: Name of the plugin
        plugin_dir: Path to the plugin directory
    
    Returns:
        TranslationManager: A configured translation manager instance
    
    Example:
        >>> from .core.translation_manager import create_translator
        >>> tm = create_translator('MyPlugin', os.path.dirname(__file__))
        >>> print(tm.tr('Hello'))
    """
    return TranslationManager(plugin_name, plugin_dir)
