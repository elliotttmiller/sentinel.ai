from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import config

engine = create_engine(config.database_url or "sqlite:///sentinel.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 