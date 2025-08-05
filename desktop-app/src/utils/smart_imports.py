"""
Smart Import Helper - Handles both package and script import contexts
This module provides a robust way to import modules that works whether
the code is run as a script from the desktop-app directory or imported
as a package from elsewhere.
"""

import sys
import os
from pathlib import Path


def setup_import_path():
    """
    Set up the Python path to support both package and script imports.
    
    This function:
    1. Adds the desktop-app directory to sys.path for script execution
    2. Adds the src directory to sys.path for absolute imports
    3. Returns the detected context ('package' or 'script')
    """
    # Get the current file's directory
    current_dir = Path(__file__).parent.absolute()
    
    # Determine if we're in the desktop-app directory
    desktop_app_dir = current_dir.parent if current_dir.name == 'src' else current_dir
    
    # Add desktop-app directory to path if not already there
    desktop_app_str = str(desktop_app_dir)
    if desktop_app_str not in sys.path:
        sys.path.insert(0, desktop_app_str)
    
    # Add src directory to path if not already there
    src_dir = desktop_app_dir / 'src'
    src_dir_str = str(src_dir)
    if src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)
    
    # Detect context
    if os.getcwd().endswith('desktop-app'):
        return 'script'
    else:
        return 'package'


def safe_import(module_path, fallback_path=None, fallback_class=None):
    """
    Safely import a module with fallback options.
    
    Args:
        module_path: Primary import path (e.g., 'src.config.settings')
        fallback_path: Alternative import path (e.g., 'config.settings')
        fallback_class: Class to return if all imports fail
    
    Returns:
        The imported module or fallback class
    """
    # Try primary import path
    try:
        parts = module_path.split('.')
        module = __import__(module_path, fromlist=[parts[-1]])
        return module
    except ImportError:
        pass
    
    # Try fallback path
    if fallback_path:
        try:
            parts = fallback_path.split('.')
            module = __import__(fallback_path, fromlist=[parts[-1]])
            return module
        except ImportError:
            pass
    
    # Return fallback class or None
    return fallback_class


def smart_import_from(module_path, item_names, fallback_path=None, fallback_items=None):
    """
    Smart import specific items from a module with fallback.
    
    Args:
        module_path: Primary module path
        item_names: List of item names to import
        fallback_path: Alternative module path
        fallback_items: Dictionary of fallback items
    
    Returns:
        Dictionary of imported items
    """
    result = {}
    
    # Try primary import
    try:
        parts = module_path.split('.')
        module = __import__(module_path, fromlist=item_names)
        for name in item_names:
            if hasattr(module, name):
                result[name] = getattr(module, name)
        return result
    except ImportError:
        pass
    
    # Try fallback path
    if fallback_path:
        try:
            parts = fallback_path.split('.')
            module = __import__(fallback_path, fromlist=item_names)
            for name in item_names:
                if hasattr(module, name):
                    result[name] = getattr(module, name)
            return result
        except ImportError:
            pass
    
    # Use fallback items
    if fallback_items:
        result.update(fallback_items)
    
    return result


# Initialize the import path when this module is imported
context = setup_import_path()