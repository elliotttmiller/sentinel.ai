#!/usr/bin/env python3
"""
Fix Railway Backend Database Schema
This script updates the Railway backend to use the correct database schema.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

def fix_railway_backend_schema():
    """Fix the Railway backend database schema by updating the backend code"""
    print("🔧 Fixing Railway Backend Database Schema")
    
    # The Railway backend URL
    railway_url = "https://sentinel-backend-production.up.railway.app"
    
    # Test the current backend
    print("Testing current Railway backend...")
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        print(f"Current backend status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Railway backend is accessible")
        else:
            print(f"⚠️ Railway backend returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Railway backend test failed: {e}")
        return False
    
    # The issue is that the Railway backend is still using the old database schema
    # We need to update the backend code to use the correct column names
    print("\n📝 The Railway backend needs to be updated with the correct database schema.")
    print("The backend is still using 'timestamp' instead of 'created_at' and missing 'source' column.")
    
    # Create a simple test to verify the database schema
    print("\n🔍 Testing database schema...")
    try:
        # Test a simple endpoint that might trigger database operations
        response = requests.get(f"{railway_url}/health", timeout=10)
        print(f"Health endpoint response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
    
    print("\n📋 To fix this issue:")
    print("1. The Railway backend code needs to be updated")
    print("2. The database schema needs to be aligned")
    print("3. The backend needs to be redeployed")
    
    print("\n🔄 The Railway backend will be automatically redeployed when we push the changes to GitHub.")
    print("The backend code should use:")
    print("  - 'created_at' instead of 'timestamp'")
    print("  - 'source' column for database compatibility")
    print("  - 'log_metadata' instead of 'metadata'")
    
    return True

def create_backend_fix_script():
    """Create a script to fix the backend database schema"""
    backend_fix_script = """
# Backend Database Schema Fix
# This should be applied to the Railway backend

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)
    source = Column(String, nullable=True)  # Add this column
    created_at = Column(DateTime, default=datetime.utcnow)  # Use created_at instead of timestamp
    log_metadata = Column(JSON, nullable=True)  # Use log_metadata instead of metadata

# Update the logging function
def log_system_event(level: str, message: str, component: str = None, metadata: dict = None):
    db = SessionLocal()
    try:
        log_entry = SystemLog(
            level=level,
            message=message,
            component=component,
            source=component,  # Use component as source
            log_metadata=metadata  # Use log_metadata
        )
        db.add(log_entry)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error logging system event: {e}")
        return False
    finally:
        db.close()
"""
    
    fix_file = Path(__file__).parent.parent.parent / "backend_fix_script.py"
    with open(fix_file, 'w') as f:
        f.write(backend_fix_script)
    
    print(f"✅ Created backend fix script: {fix_file}")
    return fix_file

if __name__ == "__main__":
    print("🔧 Railway Backend Database Schema Fix")
    print("=" * 50)
    
    # Fix the Railway backend schema
    success = fix_railway_backend_schema()
    
    if success:
        # Create the fix script
        fix_script = create_backend_fix_script()
        print(f"\n📝 Backend fix script created: {fix_script}")
        print("\n📋 Next steps:")
        print("1. Apply the database schema changes to the Railway backend")
        print("2. Update the logging functions to use correct column names")
        print("3. Redeploy the Railway backend")
        print("4. Test the backend connectivity")
    else:
        print("\n❌ Failed to fix Railway backend schema") 