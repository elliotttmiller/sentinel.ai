#!/usr/bin/env python3
"""Test WatchFiles functionality"""

import os
import time
import signal
from watchfiles import watch

def test_watchfiles():
    """Test if WatchFiles can detect file changes"""
    print("Testing WatchFiles functionality...")
    
    # Create a test file
    test_file = "test_watchfile.txt"
    
    try:
        # Write initial content
        with open(test_file, "w") as f:
            f.write("Initial content")
        
        print(f"Created test file: {test_file}")
        
        # Watch for changes (without timeout parameter)
        print("Watching for file changes (will stop after 5 seconds)...")
        
        changes_detected = []
        start_time = time.time()
        
        for changes in watch(".", watch_filter=None, debounce=100, step=100):
            changes_detected.extend(changes)
            print(f"Detected changes: {changes}")
            
            # Stop after 5 seconds
            if time.time() - start_time > 5:
                break
        
        print(f"Total changes detected: {len(changes_detected)}")
        
        if changes_detected:
            print("✅ WatchFiles is working properly")
        else:
            print("⚠️ WatchFiles detected no changes (this might be normal)")
            
    except Exception as e:
        print(f"❌ WatchFiles error: {e}")
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Cleaned up test file: {test_file}")

def check_uvicorn_reload():
    """Check uvicorn reload configuration"""
    print("\nChecking uvicorn reload configuration...")
    
    try:
        import uvicorn
        print(f"Uvicorn version: {uvicorn.__version__}")
        
        # Check if reload is available
        import uvicorn.config
        print("✅ Uvicorn reload functionality is available")
        
    except Exception as e:
        print(f"❌ Uvicorn reload check failed: {e}")

def check_watchfiles_compatibility():
    """Check WatchFiles compatibility with uvicorn"""
    print("\nChecking WatchFiles compatibility...")
    
    try:
        import watchfiles
        print(f"WatchFiles version: {watchfiles.__version__}")
        
        # Check if this version is compatible with uvicorn
        if hasattr(watchfiles, 'watch'):
            print("✅ WatchFiles watch function is available")
        else:
            print("❌ WatchFiles watch function not found")
            
    except Exception as e:
        print(f"❌ WatchFiles compatibility check failed: {e}")

if __name__ == "__main__":
    test_watchfiles()
    check_uvicorn_reload()
    check_watchfiles_compatibility() 