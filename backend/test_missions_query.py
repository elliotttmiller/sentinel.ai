from core.database import get_db
from core.models import Mission
from sqlalchemy import text

def test_missions_query():
    """Test the missions query directly."""
    try:
        db = next(get_db())
        
        # Test basic query
        print("Testing basic query...")
        missions = db.query(Mission).all()
        print(f"Found {len(missions)} missions")
        
        # Test with raw SQL
        print("Testing raw SQL query...")
        result = db.execute(text("SELECT COUNT(*) FROM missions"))
        count = result.scalar()
        print(f"Raw SQL count: {count}")
        
        # Test the actual query that's failing
        print("Testing the exact query from the API...")
        missions = db.query(Mission).all()
        print(f"Query successful, found {len(missions)} missions")
        
        db.close()
        print("Database test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_missions_query() 