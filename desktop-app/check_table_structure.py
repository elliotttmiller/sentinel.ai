#!/usr/bin/env python3
"""
Check PostgreSQL Table Structure
"""

import os
from sqlalchemy import create_engine, text

def check_table_structure():
    """Check the missions table structure"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
        
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Get table structure
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'missions' 
            ORDER BY ordinal_position
        """))
        
        print("📋 Missions table structure:")
        print("=" * 50)
        for row in result.fetchall():
            print(f"{row[0]}: {row[1]} ({row[2]}) - Default: {row[3]}")

if __name__ == "__main__":
    check_table_structure() 