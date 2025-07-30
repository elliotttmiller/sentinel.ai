#!/usr/bin/env python3
"""
Test script for ONNX Runtime Fix
"""

import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.dirname(__file__))

try:
    from onnxruntime_fix import (
        get_onnxruntime,
        is_onnxruntime_available,
        get_onnxruntime_error
    )
    
    print("🔧 Testing ONNX Runtime Fix...")
    
    # Test availability
    if is_onnxruntime_available():
        print("✅ ONNX Runtime is available")
        ort = get_onnxruntime()
        print(f"✅ Successfully imported: {type(ort)}")
    else:
        error_msg = get_onnxruntime_error()
        print(f"⚠️ ONNX Runtime not available: {error_msg}")
        print("💡 This is expected on Windows with DLL issues")
    
    print("✅ ONNX Runtime fix test completed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 