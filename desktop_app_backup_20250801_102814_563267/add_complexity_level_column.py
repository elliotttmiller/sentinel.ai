#!/usr/bin/env python3
"""
Database migration script to add complexity_level column to missions table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.advanced_database import SessionLocal

def add_complexity_level_column():
    """Add complexity_level column to missions table"""
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:LSvFcJSLjYBxsWrcTtgBUgLlLYBdPqiS@trolley.proxy.rlwy.net:44667/railway')
    
    print(f"🔧 Adding complexity_level column to missions table...")
    print(f"📊 Database URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Check if column already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'missions' 
                AND column_name = 'complexity_level'
            """))
            
            if result.fetchone():
                print("✅ Column 'complexity_level' already exists in missions table")
                return True
            else:
                print("📝 Column 'complexity_level' does not exist, adding it...")
        
        # Add the column
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE missions 
                ADD COLUMN complexity_level VARCHAR(20) DEFAULT 'standard'
            """))
            conn.commit()
            
        print("✅ Successfully added complexity_level column to missions table")
        
        # Verify the column was added
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = 'missions' 
                AND column_name = 'complexity_level'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Column verified: {row[0]} ({row[1]}) with default '{row[2]}'")
                return True
            else:
                print("❌ Column was not added successfully")
                return False
                
    except ProgrammingError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def update_existing_missions():
    """Update existing missions to have a default complexity_level"""
    
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:LSvFcJSLjYBxsWrcTtgBUgLlLYBdPqiS@trolley.proxy.rlwy.net:44667/railway')
    
    print(f"🔄 Updating existing missions with default complexity_level...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Update missions that don't have complexity_level set
            result = conn.execute(text("""
                UPDATE missions 
                SET complexity_level = 'standard' 
                WHERE complexity_level IS NULL
            """))
            
            updated_count = result.rowcount
            conn.commit()
            
            print(f"✅ Updated {updated_count} existing missions with default complexity_level")
            
            # Show current mission count
            result = conn.execute(text("SELECT COUNT(*) FROM missions"))
            total_missions = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) FROM missions WHERE complexity_level IS NOT NULL"))
            missions_with_complexity = result.fetchone()[0]
            
            print(f"📊 Total missions: {total_missions}")
            print(f"📊 Missions with complexity_level: {missions_with_complexity}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error updating missions: {e}")
        return False

def main():
    """Run the database migration"""
    print("🚀 Starting Database Migration for Parallel Execution")
    print("=" * 60)
    
    # Step 1: Add complexity_level column
    print("\n1. Adding complexity_level column...")
    column_added = add_complexity_level_column()
    
    if not column_added:
        print("❌ Failed to add complexity_level column")
        return False
    
    # Step 2: Update existing missions
    print("\n2. Updating existing missions...")
    missions_updated = update_existing_missions()
    
    if not missions_updated:
        print("❌ Failed to update existing missions")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Database migration completed successfully!")
    print("🎉 Parallel execution is now ready to use")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 