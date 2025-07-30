# Backend Database Schema Fix
# This should be applied to the Railway backend

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)
    source = Column(String, nullable=True)  # Add this column
    created_at = Column(DateTime, default=datetime.utcnow)  # Use created_at instead of timestamp
    log_metadata = Column(JSON, nullable=True)  # Use log_metadata instead of metadata


# Update the logging function


def log_system_event(level: str, message: str, component: str = None, metadata: dict = None):
    db = SessionLocal()
    try:
        log_entry = SystemLog(
            level=level,
            message=message,
            component=component,
            source=component,  # Use component as source
            log_metadata=metadata,  # Use log_metadata
        )
        db.add(log_entry)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error logging system event: {e}")
        return False
    finally:
        db.close()
