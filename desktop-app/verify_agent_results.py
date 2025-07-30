#!/usr/bin/env python3
"""
Verify Agent Results
Comprehensive verification of what agents are actually producing
"""

import requests
import json
import os
from datetime import datetime

def verify_agent_results():
    """Comprehensive verification of agent results"""
    print("🔍 VERIFYING AGENT RESULTS")
    print("=" * 60)
    
    try:
        # Get all missions
        response = requests.get("http://localhost:8001/missions", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get missions: {response.status_code}")
            return
        
        missions = response.json()
        print(f"📊 Total missions in database: {len(missions)}")
        
        # Analyze recent missions
        recent_missions = missions[-4:] if len(missions) >= 4 else missions
        print(f"\n🔍 Analyzing {len(recent_missions)} most recent missions:")
        
        success_count = 0
        failed_count = 0
        executing_count = 0
        
        for i, mission in enumerate(recent_missions, 1):
            mission_id = mission.get('mission_id_str', mission.get('id'))
            status = mission.get('status', 'unknown')
            title = mission.get('title', 'N/A')
            
            print(f"\n📋 Mission {i}: {mission_id}")
            print(f"   Title: {title}")
            print(f"   Status: {status}")
            
            if status == 'completed':
                success_count += 1
                print("   ✅ STATUS: COMPLETED")
            elif status == 'failed':
                failed_count += 1
                print("   ❌ STATUS: FAILED")
            elif status == 'executing':
                executing_count += 1
                print("   ⏳ STATUS: STILL EXECUTING")
            else:
                print(f"   ❓ STATUS: {status}")
            
            # Get detailed mission info
            try:
                mission_response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
                if mission_response.status_code == 200:
                    mission_details = mission_response.json()
                    
                    # Show execution time
                    exec_time = mission_details.get('execution_time')
                    if exec_time:
                        print(f"   ⏱️ Execution Time: {exec_time}s")
                    
                    # Show result
                    result = mission_details.get('result', 'N/A')
                    if result and result != 'N/A':
                        print(f"   📄 Result: {result[:200]}{'...' if len(result) > 200 else ''}")
                    else:
                        print("   📄 Result: No result available")
                    
                    # Show error if any
                    error = mission_details.get('error_message')
                    if error:
                        print(f"   ❌ Error: {error}")
                    
                    # Show plan
                    plan = mission_details.get('plan', {})
                    if plan:
                        steps = plan.get('steps', [])
                        print(f"   📋 Plan: {len(steps)} steps generated")
                    else:
                        print("   📋 Plan: No plan available")
                        
                else:
                    print(f"   ❌ Could not get mission details: {mission_response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error getting mission details: {e}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Completed: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   ⏳ Still Executing: {executing_count}")
        
        # Check for actual file creation
        print(f"\n🔍 CHECKING FOR ACTUAL FILE CREATION:")
        print("-" * 40)
        
        # Check desktop for sentinel files
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            desktop_files = os.listdir(desktop_path)
            sentinel_files = [f for f in desktop_files if 'sentinel' in f.lower()]
            if sentinel_files:
                print(f"✅ Found on Desktop: {sentinel_files}")
            else:
                print("❌ No Sentinel files found on Desktop")
        
        # Check current directory for generated files
        current_files = os.listdir('.')
        generated_files = []
        for f in current_files:
            if any(keyword in f.lower() for keyword in ['test', 'random', 'system', 'flask', 'requirements', 'sentinel']):
                generated_files.append(f)
        
        if generated_files:
            print(f"✅ Found in current directory: {generated_files}")
        else:
            print("❌ No generated files found in current directory")
        
        # Check for specific test files mentioned in prompts
        test_files_to_check = [
            'sentinel_test.txt',
            'test_random_generator.py',
            'random_number.txt',
            'system_analysis_report.txt',
            'sentinel_multi_agent_demo'
        ]
        
        print(f"\n🔍 CHECKING FOR SPECIFIC TEST FILES:")
        print("-" * 40)
        
        for test_file in test_files_to_check:
            if os.path.exists(test_file):
                print(f"✅ {test_file} - EXISTS")
                if os.path.isfile(test_file):
                    size = os.path.getsize(test_file)
                    print(f"   Size: {size} bytes")
            else:
                print(f"❌ {test_file} - NOT FOUND")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        print("-" * 40)
        
        if success_count > 0:
            print("✅ Some missions completed successfully")
        else:
            print("❌ No missions completed successfully")
        
        if failed_count > 0:
            print("❌ Some missions failed")
        
        if executing_count > 0:
            print("⏳ Some missions are still running")
        
        if not any(os.path.exists(f) for f in test_files_to_check):
            print("❌ No test files were actually created")
            print("💡 CONCLUSION: Agents are generating plans but not executing actual file operations")
        else:
            print("✅ Some test files were created")
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    verify_agent_results() 