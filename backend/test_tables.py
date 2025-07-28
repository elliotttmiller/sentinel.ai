from core.database import engine, get_db
from core.models import Mission, Agent
from sqlalchemy import text

# Test if tables exist
try:
    with engine.connect() as conn:
        # Check if missions table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'missions')"))
        missions_exists = result.scalar()
        print(f'Missions table exists: {missions_exists}')
        
        # Check if agents table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'agents')"))
        agents_exists = result.scalar()
        print(f'Agents table exists: {agents_exists}')
        
        if missions_exists:
            # Try to query missions
            result = conn.execute(text("SELECT COUNT(*) FROM missions"))
            count = result.scalar()
            print(f'Number of missions in database: {count}')
            
except Exception as e:
    print(f'Error checking tables: {e}') 