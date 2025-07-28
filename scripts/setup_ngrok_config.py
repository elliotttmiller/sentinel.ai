#!/usr/bin/env python3
"""
Setup ngrok configuration for Sentinel
Creates the proper ngrok.yml file with static backend domain and dynamic engine tunnel.
"""
import os
import yaml
from pathlib import Path

def setup_ngrok_config():
    """Set up the ngrok configuration file with the correct static domain."""
    
    # Get the ngrok config directory
    ngrok_config_dir = Path.home() / "AppData" / "Local" / "ngrok"
    ngrok_config_file = ngrok_config_dir / "ngrok.yml"
    
    print(f"Setting up ngrok configuration at: {ngrok_config_file}")
    
    # Create the directory if it doesn't exist
    ngrok_config_dir.mkdir(parents=True, exist_ok=True)
    
    # The configuration with static backend domain and dynamic engine tunnel
    config = {
        "version": "2",
        "authtoken": "2zgUnM4yVIVtl8IyB31dGqMROT3_3NEzyX7Vb2RjAZCbqnZTp",
        "tunnels": {
            "backend": {
                "proto": "http",
                "addr": 8080,
                "domain": "thrush-real-lacewing.ngrok-free.app"
            },
            "engine": {
                "proto": "http", 
                "addr": 8001
            }
        }
    }
    
    # Write the configuration file
    with open(ngrok_config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ ngrok configuration created successfully!")
    print(f"📁 Location: {ngrok_config_file}")
    print("\n📋 Configuration:")
    print("   - Backend: Static domain 'thrush-real-lacewing.ngrok-free.app' → localhost:8080")
    print("   - Engine: Dynamic tunnel → localhost:8001")
    print("\n💡 Next steps:")
    print("   1. Install ngrok as a Windows service: ngrok service install")
    print("   2. Start the service: ngrok service start")
    print("   3. Use the manage_services.py script to start your local servers")

if __name__ == "__main__":
    setup_ngrok_config() 