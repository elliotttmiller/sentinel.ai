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
    
    # Get the database path
    db_path = Path(__file__).parent.parent / "db" / "sentinel_missions.db"
    
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