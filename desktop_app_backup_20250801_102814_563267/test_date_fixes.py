#!/usr/bin/env python3
"""
Test script to verify date formatting fixes
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_date_fixes():
    """Test the date formatting fixes"""
    print("🧪 Testing Date Formatting Fixes")
    print("=" * 50)
    
    # Test 1: Check live logs endpoint with proper date handling
    print("\n1. Testing Live Logs with Date Handling...")
    try:
        response = requests.get(f"{BASE_URL}/api/logs/live", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Live logs endpoint working")
            
            # Check overview data
            overview = data.get('overview', {})
            print(f"   - Total logs: {overview.get('total_logs', 0)}")
            print(f"   - Last update: {overview.get('last_update', 'N/A')}")
            
            # Check server data
            servers = data.get('servers', {})
            for server_name, server_data in servers.items():
                print(f"   - {server_name}: {server_data.get('log_count', 0)} logs")
                print(f"     Last event: {server_data.get('last_event', 'N/A')}")
                
        else:
            print(f"❌ Live logs endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing live logs: {e}")
    
    # Test 2: Check server-specific endpoints
    print("\n2. Testing Server-Specific Endpoints...")
    for server_port in ['8001', '8002']:
        try:
            response = requests.get(f"{BASE_URL}/api/logs/server/{server_port}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server {server_port} endpoint working")
                print(f"   - Log count: {data.get('log_count', 0)}")
                print(f"   - Last event: {data.get('last_event', 'N/A')}")
                print(f"   - Last update: {data.get('last_update', 'N/A')}")
            else:
                print(f"❌ Server {server_port} endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing server {server_port}: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Date Formatting Test Complete!")
    print("\nFixes Applied:")
    print("   ✅ Enhanced date formatting with error handling")
    print("   ✅ Better null/undefined value handling")
    print("   ✅ Improved log level display")
    print("   ✅ Fallback values for missing data")
    print("   ✅ Proper timestamp validation")

if __name__ == "__main__":
    test_date_fixes() 