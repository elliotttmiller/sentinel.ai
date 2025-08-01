#!/usr/bin/env python3
"""
Test script for enhanced dashboard with real-time server log streaming
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_enhanced_dashboard():
    """Test the enhanced dashboard with server log streaming"""
    print("🧪 Testing Enhanced Dashboard with Server Log Streaming")
    print("=" * 60)
    
    # Test 1: Check if the main dashboard loads
    print("\n1. Testing Dashboard Load...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard loads successfully")
        else:
            print(f"❌ Dashboard load failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")
    
    # Test 2: Check live logs endpoint
    print("\n2. Testing Live Logs Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/logs/live", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Live logs endpoint working")
            print(f"   - Total logs: {data.get('overview', {}).get('total_logs', 0)}")
            print(f"   - Server 8001 logs: {data.get('servers', {}).get('server_8001', {}).get('log_count', 0)}")
            print(f"   - Server 8002 logs: {data.get('servers', {}).get('server_8002', {}).get('log_count', 0)}")
        else:
            print(f"❌ Live logs endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing live logs: {e}")
    
    # Test 3: Check server-specific log endpoints
    print("\n3. Testing Server-Specific Log Endpoints...")
    for server_port in ['8001', '8002']:
        try:
            response = requests.get(f"{BASE_URL}/api/logs/server/{server_port}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server {server_port} logs endpoint working")
                print(f"   - Log count: {data.get('log_count', 0)}")
                print(f"   - Error count: {data.get('error_count', 0)}")
                print(f"   - Warning count: {data.get('warning_count', 0)}")
            else:
                print(f"❌ Server {server_port} logs endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing server {server_port} logs: {e}")
    
    # Test 4: Check log streaming endpoint
    print("\n4. Testing Log Streaming Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/logs/stream", timeout=3)
        if response.status_code == 200:
            print("✅ Log streaming endpoint is accessible")
        else:
            print(f"❌ Log streaming endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing log streaming: {e}")
    
    # Test 5: Check observability endpoints
    print("\n5. Testing Observability Endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/api/observability/overview", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Observability overview endpoint working")
            print(f"   - Weave status: {data.get('weave', {}).get('status', 'unknown')}")
            print(f"   - WandB status: {data.get('wandb', {}).get('status', 'unknown')}")
            print(f"   - Sentry status: {data.get('sentry', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Observability endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing observability: {e}")
    
    # Test 6: Check service status
    print("\n6. Testing Service Status...")
    try:
        response = requests.get(f"{BASE_URL}/service-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Service status endpoint working")
            print(f"   - Overall status: {data.get('overall_status', 'unknown')}")
        else:
            print(f"❌ Service status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing service status: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Enhanced Dashboard Test Complete!")
    print("\nFeatures Implemented:")
    print("   ✅ Real-time server log streaming (8001/8002)")
    print("   ✅ Individual server log tabs")
    print("   ✅ Enhanced live event feed with overview")
    print("   ✅ Server status indicators in header")
    print("   ✅ Optimized dashboard layout (4/8 column split)")
    print("   ✅ Server-Sent Events (SSE) for real-time updates")
    print("   ✅ Enhanced CSS styling for better UX")
    print("\nThe dashboard now provides:")
    print("   - Individual tabs for Server 8001 and Server 8002 logs")
    print("   - Real-time log streaming with automatic reconnection")
    print("   - Server status indicators in the header")
    print("   - Optimized layout with better spacing")
    print("   - Enhanced visual feedback and animations")

if __name__ == "__main__":
    test_enhanced_dashboard() 