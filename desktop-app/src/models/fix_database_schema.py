#!/usr/bin/env python3
"""
Database Schema Fix Script
Adds missing columns to existing tables
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))


def fix_database_schema():
    """Fix database schema issues"""
    print("🔧 Fixing Database Schema...")

    # Load environment variables
    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False

    try:
        # Create engine
        engine = create_engine(database_url)

        # Create inspector
        inspector = inspect(engine)

        # Check if system_logs table exists
        if not inspector.has_table("system_logs"):
            print("❌ system_logs table does not exist")
            return False

        # Get existing columns
        columns = [col["name"] for col in inspector.get_columns("system_logs")]
        print(f"📋 Existing columns: {columns}")

        # Check if component column exists
        if "component" not in columns:
            print("➕ Adding missing 'component' column...")
            with engine.connect() as conn:
                conn.execute(
                    text("ALTER TABLE system_logs ADD COLUMN component VARCHAR(255)")
                )
                conn.commit()
            print("✅ 'component' column added successfully")
        else:
            print("✅ 'component' column already exists")

        # Check if log_metadata column exists
        if "log_metadata" not in columns:
            print("➕ Adding missing 'log_metadata' column...")
            with engine.connect() as conn:
                conn.execute(
                    text("ALTER TABLE system_logs ADD COLUMN log_metadata JSONB")
                )
                conn.commit()
            print("✅ 'log_metadata' column added successfully")
        else:
            print("✅ 'log_metadata' column already exists")

        # Verify the fix
        updated_columns = [col["name"] for col in inspector.get_columns("system_logs")]
        print(f"📋 Updated columns: {updated_columns}")

        # Test insert
        print("🧪 Testing database insert...")
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                INSERT INTO system_logs (level, message, component, source, created_at, log_metadata) 
                VALUES ('INFO', 'Database schema fix test', 'schema_fix', 'schema_fix', NOW(), '{"test": true}')
                RETURNING id
            """
                )
            )
            test_id = result.fetchone()[0]
            print(f"✅ Test insert successful (ID: {test_id})")

            # Clean up test record
            conn.execute(
                text("DELETE FROM system_logs WHERE id = :id"), {"id": test_id}
            )
            conn.commit()
            print("🧹 Test record cleaned up")

        print("🎉 Database schema fix completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        return False


if __name__ == "__main__":
    success = fix_database_schema()
    sys.exit(0 if success else 1)
