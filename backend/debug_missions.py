from core.database import get_db
from core.models import Mission
from core.schemas import MissionSchema

def debug_missions():
    """Debug the missions query issue."""
    try:
        db = next(get_db())
        
        print("Mission model type:", type(Mission))
        print("Mission model:", Mission)
        
        # Check if Mission is actually the model or schema
        if hasattr(Mission, '__tablename__'):
            print("Mission is a SQLAlchemy model")
        else:
            print("Mission is NOT a SQLAlchemy model")
        
        # Try the query
        try:
            missions = db.query(Mission).all()
            print(f"Query successful, found {len(missions)} missions")
        except Exception as e:
            print(f"Query failed: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_missions() 