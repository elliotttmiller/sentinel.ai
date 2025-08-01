#!/usr/bin/env python3
"""
Simple diagnostic script to test server connectivity
"""

import requests
import socket
import time

def test_port(host, port):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error testing port {port}: {e}")
        return False

def test_endpoint(url, timeout=5):
    """Test a specific endpoint"""
    try:
        print(f"Testing: {url}")
        response = requests.get(url, timeout=timeout)
        print(f"  Status: {response.status_code}")
        print(f"  Response time: {response.elapsed.total_seconds():.3f}s")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Data keys: {list(data.keys())}")
            except:
                print(f"  Response: {response.text[:100]}...")
        return True
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout after {timeout}s")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection refused")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🔍 Server Connectivity Diagnostic")
    print("=" * 50)
    
    # Test if ports are open
    print("\n📡 Testing Port Connectivity:")
    ports = [8001, 8002]
    for port in ports:
        is_open = test_port('localhost', port)
        status = "✅ OPEN" if is_open else "❌ CLOSED"
        print(f"  Port {port}: {status}")
    
    # Test basic endpoints
    print("\n🌐 Testing Basic Endpoints:")
    basic_endpoints = [
        "http://localhost:8001/health",
        "http://localhost:8001/",
        "http://localhost:8001/api/status"
    ]
    
    for endpoint in basic_endpoints:
        test_endpoint(endpoint)
        time.sleep(1)  # Small delay between tests
    
    # Test observability endpoints with shorter timeout
    print("\n📊 Testing Observability Endpoints (5s timeout):")
    obs_endpoints = [
        "http://localhost:8001/api/system/vitals",
        "http://localhost:8001/api/observability/overview",
        "http://localhost:8001/observability/weave",
        "http://localhost:8001/observability/sentry",
        "http://localhost:8001/observability/wandb"
    ]
    
    for endpoint in obs_endpoints:
        test_endpoint(endpoint, timeout=5)
        time.sleep(1)
    
    print("\n💡 Recommendations:")
    print("  - If ports are closed, start your servers")
    print("  - If basic endpoints work but observability fails, check the specific endpoints")
    print("  - If all timeouts, there might be a server issue")

if __name__ == "__main__":
    main() 