#!/usr/bin/env python3
"""
ONNX Runtime Import Fix
Handles DLL loading issues and provides graceful fallbacks for Windows systems
"""

import sys
import os
import importlib
from typing import Optional, Any
from loguru import logger

def safe_import_onnxruntime() -> Optional[Any]:
    """
    Safely import onnxruntime with comprehensive error handling
    Returns the module if successful, None if failed
    """
    try:
        # First, try direct import
        import onnxruntime
        logger.info("ONNX Runtime imported successfully")
        return onnxruntime
    except ImportError as e:
        logger.warning(f"ONNX Runtime not installed: {e}")
        return None
    except Exception as e:
        logger.error(f"ONNX Runtime import failed: {e}")
        
        # Try to diagnose the issue
        if "DLL" in str(e) or "dynamic link library" in str(e).lower():
            logger.error("DLL loading issue detected - this is a common Windows problem")
            logger.info("Possible solutions:")
            logger.info("1. Install Microsoft Visual C++ Redistributable")
            logger.info("2. Try a different onnxruntime version")
            logger.info("3. Use CPU-only version: pip install onnxruntime-cpu")
        
        return None

def install_onnxruntime_cpu() -> bool:
    """
    Install CPU-only version of onnxruntime as a fallback
    """
    try:
        import subprocess
        import sys
        
        logger.info("Installing onnxruntime-cpu as fallback...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "onnxruntime-cpu"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.success("onnxruntime-cpu installed successfully")
            return True
        else:
            logger.error(f"Failed to install onnxruntime-cpu: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error installing onnxruntime-cpu: {e}")
        return False

def get_onnxruntime_with_fallback() -> Optional[Any]:
    """
    Get onnxruntime with automatic fallback to CPU version
    """
    # Try original onnxruntime
    ort = safe_import_onnxruntime()
    if ort:
        return ort
    
    # Try CPU version
    try:
        import onnxruntime_cpu
        logger.info("Using onnxruntime-cpu as fallback")
        return onnxruntime_cpu
    except ImportError:
        # Install CPU version and try again
        if install_onnxruntime_cpu():
            try:
                import onnxruntime_cpu
                logger.info("Successfully imported onnxruntime-cpu after installation")
                return onnxruntime_cpu
            except ImportError:
                logger.error("Failed to import onnxruntime-cpu even after installation")
                return None
        else:
            logger.error("Failed to install onnxruntime-cpu")
            return None

def create_onnxruntime_proxy():
    """
    Create a proxy module that handles onnxruntime import gracefully
    """
    class ONNXRuntimeProxy:
        def __init__(self):
            self._ort = None
            self._available = False
            self._error_message = None
            
            # Try to import onnxruntime
            try:
                self._ort = get_onnxruntime_with_fallback()
                if self._ort:
                    self._available = True
                    logger.info("ONNX Runtime proxy initialized successfully")
                else:
                    self._error_message = "ONNX Runtime not available"
                    logger.warning("ONNX Runtime proxy initialized with fallback mode")
            except Exception as e:
                self._error_message = str(e)
                logger.error(f"ONNX Runtime proxy initialization failed: {e}")
        
        def is_available(self) -> bool:
            """Check if onnxruntime is available"""
            return self._available
        
        def get_error_message(self) -> Optional[str]:
            """Get error message if onnxruntime is not available"""
            return self._error_message
        
        def __getattr__(self, name):
            """Proxy attribute access to the actual onnxruntime module"""
            if not self._available:
                raise AttributeError(f"ONNX Runtime not available: {self._error_message}")
            return getattr(self._ort, name)
        
        def __call__(self, *args, **kwargs):
            """Proxy function calls to the actual onnxruntime module"""
            if not self._available:
                raise RuntimeError(f"ONNX Runtime not available: {self._error_message}")
            return self._ort(*args, **kwargs)
    
    return ONNXRuntimeProxy()

# Create a global proxy instance
onnxruntime_proxy = create_onnxruntime_proxy()

def get_onnxruntime():
    """
    Get onnxruntime module with graceful error handling
    """
    return onnxruntime_proxy

def is_onnxruntime_available() -> bool:
    """
    Check if onnxruntime is available
    """
    return onnxruntime_proxy.is_available()

def get_onnxruntime_error() -> Optional[str]:
    """
    Get error message if onnxruntime is not available
    """
    return onnxruntime_proxy.get_error_message() 