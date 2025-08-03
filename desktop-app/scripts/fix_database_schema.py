#!/usr/bin/env python3
"""
Database Migration Script - Add missing columns to missions table
Fixes the 'no such column: missions.progress' error
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add missing columns to the missions table"""
    
    # Get the database path (matches the DATABASE_URL in advanced_database.py)
    db_path = Path(__file__).parent.parent.parent / "db" / "sentinel_missions.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🔧 Migrating database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(missions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        # Add progress column if it doesn't exist
        if 'progress' not in columns:
            print("➕ Adding 'progress' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN progress INTEGER DEFAULT 0")
            print("✅ 'progress' column added")
        else:
            print("✅ 'progress' column already exists")
        
        # Add priority column if it doesn't exist
        if 'priority' not in columns:
            print("➕ Adding 'priority' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN priority TEXT DEFAULT 'medium'")
            print("✅ 'priority' column added")
        else:
            print("✅ 'priority' column already exists")
        
        # Add execution_path column if it doesn't exist
        if 'execution_path' not in columns:
            print("➕ Adding 'execution_path' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN execution_path TEXT")
            print("✅ 'execution_path' column added")
        else:
            print("✅ 'execution_path' column already exists")
        
        # Add complexity_score column if it doesn't exist
        if 'complexity_score' not in columns:
            print("➕ Adding 'complexity_score' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN complexity_score REAL")
            print("✅ 'complexity_score' column added")
        else:
            print("✅ 'complexity_score' column already exists")
        
        # Add decision_metadata column if it doesn't exist
        if 'decision_metadata' not in columns:
            print("➕ Adding 'decision_metadata' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN decision_metadata TEXT")
            print("✅ 'decision_metadata' column added")
        else:
            print("✅ 'decision_metadata' column already exists")
        
        # Add user_satisfaction column if it doesn't exist
        if 'user_satisfaction' not in columns:
            print("➕ Adding 'user_satisfaction' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN user_satisfaction REAL")
            print("✅ 'user_satisfaction' column added")
        else:
            print("✅ 'user_satisfaction' column already exists")
        
        # Add is_healing column if it doesn't exist
        if 'is_healing' not in columns:
            print("➕ Adding 'is_healing' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN is_healing BOOLEAN DEFAULT 0")
            print("✅ 'is_healing' column added")
        else:
            print("✅ 'is_healing' column already exists")
        
        # Add phoenix_retries column if it doesn't exist
        if 'phoenix_retries' not in columns:
            print("➕ Adding 'phoenix_retries' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN phoenix_retries INTEGER DEFAULT 0")
            print("✅ 'phoenix_retries' column added")
        else:
            print("✅ 'phoenix_retries' column already exists")
        
        # Add owner_id column if it doesn't exist
        if 'owner_id' not in columns:
            print("➕ Adding 'owner_id' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN owner_id INTEGER")
            print("✅ 'owner_id' column added")
        else:
            print("✅ 'owner_id' column already exists")
        
        # Add organization_id column if it doesn't exist
        if 'organization_id' not in columns:
            print("➕ Adding 'organization_id' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN organization_id INTEGER")
            print("✅ 'organization_id' column added")
        else:
            print("✅ 'organization_id' column already exists")
        
        # Add prompt_analysis column if it doesn't exist
        if 'prompt_analysis' not in columns:
            print("➕ Adding 'prompt_analysis' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN prompt_analysis TEXT")
            print("✅ 'prompt_analysis' column added")
        else:
            print("✅ 'prompt_analysis' column already exists")
        
        # Add risk_score column if it doesn't exist
        if 'risk_score' not in columns:
            print("➕ Adding 'risk_score' column...")
            cursor.execute("ALTER TABLE missions ADD COLUMN risk_score REAL")
            print("✅ 'risk_score' column added")
        else:
            print("✅ 'risk_score' column already exists")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_database() 