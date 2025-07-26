from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Create database engine using the DATABASE_URL from settings
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 