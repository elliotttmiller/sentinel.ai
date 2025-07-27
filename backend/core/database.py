from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger
from config import settings

# Create database engine using the DATABASE_URL from settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Checks connection before using
    pool_recycle=300,    # Recycle connections every 5 minutes
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency to get a new database session for each request.
    Ensures the session is always closed, even if errors occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.info("Closing database session")
        db.close() 