from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Checks connection validity before use
    pool_recycle=300,    # Recycles connections every 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get a new database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.info("Closing database session for this request.")
        db.close() 