#!/usr/bin/env python3
"""
Test script to verify mission integration with database
"""

import requests
import json
import time

def test_mission_creation():
    """Test creating a mission via the API"""
    print("🚀 Testing Mission Creation...")
    
    # Test mission data
    mission_data = {
        "title": "Real-Time Streaming Integration Test",
        "prompt": "Create a comprehensive test that validates the real-time log streaming integration between Server 8001 (Main API) and Server 8002 (Cognitive Engine). The mission should generate HTTP requests, cognitive processing activities, background tasks, and demonstrate cross-server communication while monitoring the live event feed for proper log categorization and real-time updates.",
        "agent_type": "developer"
    }
    
    try:
        # Create mission
        response = requests.post(
            "http://localhost:8001/api/missions",
            json=mission_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mission created successfully!")
            print(f"   Mission ID: {result['mission_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Status: {result['status']}")
            return result['mission_id']
        else:
            print(f"❌ Failed to create mission: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating mission: {e}")
        return None

def test_mission_listing():
    """Test listing missions"""
    print("\n📋 Testing Mission Listing...")
    
    try:
        response = requests.get("http://localhost:8001/missions")
        
        if response.status_code == 200:
            missions = response.json()
            print(f"✅ Found {len(missions)} missions")
            
            for i, mission in enumerate(missions[:3]):  # Show first 3
                print(f"   {i+1}. {mission['title']} ({mission['status']})")
                print(f"      ID: {mission['mission_id_str']}")
                print(f"      Created: {mission['created_at']}")
            
            return missions
        else:
            print(f"❌ Failed to list missions: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error listing missions: {e}")
        return []

def test_mission_updates(mission_id):
    """Test getting mission updates"""
    print(f"\n📊 Testing Mission Updates for {mission_id}...")
    
    try:
        response = requests.get(f"http://localhost:8001/api/missions/{mission_id}/updates")
        
        if response.status_code == 200:
            updates = response.json()
            print(f"✅ Found {len(updates)} updates")
            
            for update in updates:
                print(f"   [{update['type'].upper()}] {update['message']}")
                print(f"      Time: {update['timestamp']}")
                if update.get('step_number'):
                    print(f"      Step: {update['step_number']}")
            
            return updates
        else:
            print(f"❌ Failed to get updates: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return []

def test_server_8002():
    """Test server 8002 endpoints"""
    print("\n🔧 Testing Server 8002...")
    
    endpoints = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/api/cognitive/status", "Cognitive Status"),
        ("/api/cognitive/process", "Cognitive Process")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8002{endpoint}")
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def main():
    """Run all tests"""
    print("🧪 Mission Integration Test Suite")
    print("=" * 50)
    
    # Test server 8002 first
    test_server_8002()
    
    # Test mission creation
    mission_id = test_mission_creation()
    
    if mission_id:
        # Wait a moment for background processing
        print("\n⏳ Waiting for background processing...")
        time.sleep(2)
        
        # Test mission updates
        test_mission_updates(mission_id)
        
        # Wait a bit more for completion
        print("\n⏳ Waiting for mission completion...")
        time.sleep(5)
        
        # Test mission updates again
        test_mission_updates(mission_id)
    
    # Test mission listing
    test_mission_listing()
    
    print("\n🎉 Test suite completed!")
    print("\n💡 Check the Live Event Feed in your browser to see real-time logs!")

if __name__ == "__main__":
    main() 