#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get('http://localhost:8001/api/logs/live', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("✅ Logs endpoint working")
        print(f"Total logs: {data.get('overview', {}).get('total_logs', 0)}")
        
        servers = data.get('servers', {})
        for server_name, server_data in servers.items():
            print(f"\n{server_name}:")
            print(f"  - Log count: {server_data.get('log_count', 0)}")
            print(f"  - Error count: {server_data.get('error_count', 0)}")
            print(f"  - Warning count: {server_data.get('warning_count', 0)}")
            print(f"  - Status: {server_data.get('status', 'unknown')}")
            
            logs = server_data.get('logs', [])
            print(f"  - Sample logs:")
            for log in logs[:3]:  # Show first 3 logs
                print(f"    {log.get('timestamp', 'N/A')} [{log.get('level', 'INFO')}] {log.get('message', 'No message')}")
        
        system = data.get('system', {})
        print(f"\nSystem:")
        print(f"  - Log count: {system.get('log_count', 0)}")
        print(f"  - Error count: {system.get('error_count', 0)}")
        print(f"  - Warning count: {system.get('warning_count', 0)}")
        
        logs = system.get('logs', [])
        print(f"  - Sample logs:")
        for log in logs[:3]:  # Show first 3 logs
            print(f"    {log.get('timestamp', 'N/A')} [{log.get('level', 'INFO')}] {log.get('message', 'No message')}")
            
    else:
        print(f"❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}") 