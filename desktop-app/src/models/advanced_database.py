"""
Advanced Database System for Cognitive Forge
Implements SQLite persistence and ChromaDB vector memory
"""

from dotenv import load_dotenv
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import chromadb
from chromadb.config import Settings

# Ensure database directory exists
os.makedirs("db", exist_ok=True)

# Database Configuration - Supports both SQLite and PostgreSQL

load_dotenv()

# Get database URL from environment, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/sentinel_missions.db")

# Configure engine based on database type
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration
    engine = create_engine(DATABASE_URL)
else:
    # SQLite configuration
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Mission(Base):
    """Mission tracking with comprehensive metadata"""

    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    mission_id_str = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    agent_type = Column(String, default="developer")
    status = Column(String, default="pending")  # pending, planning, executing, completed, failed
    result = Column(Text, nullable=True)
    plan = Column(JSON, nullable=True)
    execution_time = Column(Integer, nullable=True)  # seconds
    tokens_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)


class MissionUpdate(Base):
    """Real-time mission updates for observability"""

    __tablename__ = "mission_updates"

    id = Column(Integer, primary_key=True, index=True)
    mission_id_str = Column(String, index=True)
    update_message = Column(Text, nullable=False)
    update_type = Column(String, default="info")  # info, warning, error, success
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_role = Column(String, nullable=True)
    step_number = Column(Integer, nullable=True)


class SystemLog(Base):
    """System-level logging and monitoring"""

    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)  # agent_core, database, api, etc.
    source = Column(String, nullable=True)  # source field for database compatibility
    created_at = Column(DateTime, default=datetime.utcnow)  # Changed from timestamp to created_at
    log_metadata = Column(
        JSON, nullable=True
    )  # Renamed from 'metadata' to avoid SQLAlchemy conflict


class DatabaseManager:
    """Advanced database management with ChromaDB integration"""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.Base = Base

        # Initialize ChromaDB for vector memory (optional)
        self.memory_collection = None
        try:
            # Initialize ChromaDB for vector memory
            self.chroma_client = chromadb.PersistentClient(
                path="db/chroma_memory",
                settings=Settings(anonymized_telemetry=False)
            )
            self.memory_collection = self.chroma_client.get_or_create_collection(
                name="mission_memory",
                metadata={"description": "Long-term mission memory and learnings"}
            )
            logger.info("ChromaDB memory system initialized successfully")
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed (memory features disabled): {e}")
            self.memory_collection = None

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database system initialized successfully with {DATABASE_URL}")

    def get_db(self):
        """Get database session with proper cleanup"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_mission(
        self, mission_id_str: str, title: str, prompt: str, agent_type: str
    ) -> Mission:
        """Create a new mission record"""
        db = SessionLocal()
        try:
            mission = Mission(
                mission_id_str=mission_id_str,
                title=title,
                prompt=prompt,
                agent_type=agent_type,
                status="pending",
            )
            db.add(mission)
            db.commit()
            db.refresh(mission)
            logger.info(f"Created mission: {mission_id_str}")
            return mission
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating mission: {e}")
            raise
        finally:
            db.close()

    def update_mission_status(
        self,
        mission_id_str: str,
        status: str,
        result: str = None,
        plan: Dict = None,
        execution_time: int = None,
        error_message: str = None,
    ) -> bool:
        """Update mission status and metadata"""
        db = SessionLocal()
        try:
            mission = db.query(Mission).filter(Mission.mission_id_str == mission_id_str).first()
            if not mission:
                logger.error(f"Mission not found: {mission_id_str}")
                return False

            mission.status = status
            mission.updated_at = datetime.utcnow()

            if result is not None:
                mission.result = result
            if plan is not None:
                mission.plan = plan
            if execution_time is not None:
                mission.execution_time = execution_time
            if error_message is not None:
                mission.error_message = error_message

            if status in ["completed", "failed"]:
                mission.completed_at = datetime.utcnow()

            db.commit()
            logger.info(f"Updated mission {mission_id_str} status to {status}")
            return True

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating mission: {e}")
            return False
        finally:
            db.close()

    def add_mission_update(
        self,
        mission_id_str: str,
        message: str,
        update_type: str = "info",
        agent_role: str = None,
        step_number: int = None,
    ) -> bool:
        """Add a real-time update to a mission"""
        db = SessionLocal()
        try:
            update = MissionUpdate(
                mission_id_str=mission_id_str,
                update_message=message,
                update_type=update_type,
                agent_role=agent_role,
                step_number=step_number,
            )
            db.add(update)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error adding mission update: {e}")
            return False
        finally:
            db.close()

    def get_mission_updates(self, mission_id_str: str, limit: int = 100) -> List[MissionUpdate]:
        """Get recent updates for a mission"""
        db = SessionLocal()
        try:
            updates = (
                db.query(MissionUpdate)
                .filter(MissionUpdate.mission_id_str == mission_id_str)
                .order_by(MissionUpdate.timestamp.desc())
                .limit(limit)
                .all()
            )
            return updates
        finally:
            db.close()

    def get_mission(self, mission_id_str: str) -> Optional[Mission]:
        """Get a mission by ID"""
        db = SessionLocal()
        try:
            return db.query(Mission).filter(Mission.mission_id_str == mission_id_str).first()
        finally:
            db.close()

    def list_missions(self, limit: int = 50, include_archived: bool = False) -> List[Mission]:
        """List recent missions"""
        db = SessionLocal()
        try:
            query = db.query(Mission)
            if not include_archived:
                query = query.filter(Mission.is_archived == False)
            return query.order_by(Mission.created_at.desc()).limit(limit).all()
        finally:
            db.close()

    def store_memory(
        self, mission_id_str: str, prompt: str, result: str, success: bool, metadata: Dict = None
    ) -> bool:
        """Store mission outcome in ChromaDB for long-term memory"""
        if self.memory_collection is None:
            logger.warning(f"ChromaDB memory collection not initialized, skipping memory storage for mission: {mission_id_str}")
            return False

        try:
            # Create a comprehensive memory entry
            memory_text = f"""Mission ID: {mission_id_str}
Prompt: {prompt}
Success: {success}
Result: {result}
Timestamp: {datetime.utcnow().isoformat()}"""

            # Store in ChromaDB
            self.memory_collection.add(
                documents=[memory_text],
                metadatas=[
                    {
                        "mission_id": mission_id_str,
                        "success": success,
                        "timestamp": datetime.utcnow().isoformat(),
                        **(metadata or {}),
                    }
                ],
                ids=[f"memory_{mission_id_str}"],
            )

            logger.info(f"Memory stored for mission: {mission_id_str}")
            return True

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False

    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Search mission memory for relevant past experiences"""
        if self.memory_collection is None:
            logger.warning("ChromaDB memory collection not initialized, skipping memory search.")
            return []

        try:
            results = self.memory_collection.query(query_texts=[query], n_results=limit)

            memories = []
            for i in range(len(results["documents"][0])):
                memory = {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                }
                memories.append(memory)

            logger.info(f"Memory search returned {len(memories)} results")
            return memories

        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []

    def log_system_event(
        self, level: str, message: str, component: str = None, metadata: Dict = None
    ) -> bool:
        """Log system-level events"""
        try:
            db = SessionLocal()
            try:
                log_entry = SystemLog(
                    level=level,
                    message=message,
                    component=component,
                    source=component,  # Use component as source for database compatibility
                    log_metadata=metadata,
                )
                db.add(log_entry)
                db.commit()
                return True
            except SQLAlchemyError as e:
                db.rollback()
                logger.warning(f"Database logging failed (continuing without logging): {e}")
                return False
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"System event logging failed: {e}")
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            db = SessionLocal()
            try:
                total_missions = db.query(Mission).count()
                completed_missions = db.query(Mission).filter(Mission.status == "completed").count()
                failed_missions = db.query(Mission).filter(Mission.status == "failed").count()
                pending_missions = db.query(Mission).filter(Mission.status == "pending").count()

                # Get memory stats
                memory_count = 0
                if self.memory_collection:
                    try:
                        memory_count = self.memory_collection.count()
                    except Exception as e:
                        logger.warning(f"Error getting memory count: {e}")
                        memory_count = 0

                return {
                    "total_missions": total_missions,
                    "completed_missions": completed_missions,
                    "failed_missions": failed_missions,
                    "pending_missions": pending_missions,
                    "success_rate": (
                        (completed_missions / total_missions * 100) if total_missions > 0 else 0
                    ),
                    "memory_entries": memory_count,
                    "last_updated": datetime.utcnow().isoformat(),
                }
            except SQLAlchemyError as e:
                logger.warning(f"Database stats query failed: {e}")
                return {
                    "total_missions": 0,
                    "completed_missions": 0,
                    "failed_missions": 0,
                    "pending_missions": 0,
                    "success_rate": 0,
                    "memory_entries": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "error": "Database connection issue"
                }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {
                "total_missions": 0,
                "completed_missions": 0,
                "failed_missions": 0,
                "pending_missions": 0,
                "success_rate": 0,
                "memory_entries": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global database manager instance
db_manager = DatabaseManager()
