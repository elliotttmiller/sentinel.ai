import urllib.request
import json
import time
import threading

def test_server_8001():
    """Test server 8001 (main dashboard)"""
    try:
        # Test main dashboard endpoints
        urllib.request.urlopen('http://localhost:8001/health')
        print("✅ Server 8001 health check successful")
        
        urllib.request.urlopen('http://localhost:8001/api/test-8002')
        print("✅ Server 8001 test endpoint successful")
        
        urllib.request.urlopen('http://localhost:8001/missions')
        print("✅ Server 8001 missions endpoint successful")
        
    except Exception as e:
        print(f"❌ Server 8001 error: {e}")

def test_server_8002():
    """Test server 8002 (cognitive engine)"""
    try:
        # Test cognitive engine endpoints
        urllib.request.urlopen('http://localhost:8002/health')
        print("✅ Server 8002 health check successful")
        
        urllib.request.urlopen('http://localhost:8002/api/cognitive/status')
        print("✅ Server 8002 cognitive status successful")
        
        urllib.request.urlopen('http://localhost:8002/api/cognitive/process')
        print("✅ Server 8002 cognitive process successful")
        
    except Exception as e:
        print(f"❌ Server 8002 error: {e}")

def continuous_test():
    """Run continuous tests on both servers"""
    print("🚀 Starting continuous server tests...")
    print("📊 This will generate live logs for both servers")
    print("🌐 Check your dashboard at http://localhost:8001")
    print("=" * 50)
    
    while True:
        print(f"\n⏰ {time.strftime('%H:%M:%S')} - Testing both servers...")
        
        # Test both servers in parallel
        thread1 = threading.Thread(target=test_server_8001)
        thread2 = threading.Thread(target=test_server_8002)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        print("💤 Waiting 10 seconds before next test...")
        time.sleep(10)

if __name__ == "__main__":
    try:
        continuous_test()
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}") 