import requests

BACKEND_URL = "http://localhost:8080"
ENGINE_URL = "http://localhost:8001"

endpoints = [
    ("Backend Health", f"{BACKEND_URL}/health"),
    ("GenAI Status", f"{BACKEND_URL}/genai/status"),
    ("Agent List", f"{BACKEND_URL}/agents"),
    ("Agent Test", f"{BACKEND_URL}/agents/test"),
    ("Engine Health", f"{ENGINE_URL}/health"),
]

def test_endpoint(name, url, method="get"):
    print(f"\nTesting: {name} -> {url}")
    try:
        if method == "get":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            # Try to print the full error/traceback if present
            try:
                print("Error Response:", resp.json())
            except Exception:
                print("Error Response (non-JSON):", resp.text)
            print(f"❌ {name} FAILED!")
        else:
            try:
                print("Response:", resp.json())
            except Exception:
                print("Response (non-JSON):", resp.text)
            print(f"✅ {name} OK!")
    except Exception as e:
        print(f"❌ {name} ERROR: {e}")

def main():
    print("\n=== Sentinel Integration Test ===\n")
    test_endpoint("Backend Health", f"{BACKEND_URL}/health")
    test_endpoint("GenAI Status", f"{BACKEND_URL}/genai/status")
    test_endpoint("Agent List", f"{BACKEND_URL}/agents")
    test_endpoint("Agent Test", f"{BACKEND_URL}/agents/test")
    test_endpoint("Engine Health", f"{ENGINE_URL}/health")
    print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    main() 