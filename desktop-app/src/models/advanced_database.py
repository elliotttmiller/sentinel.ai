"""
Advanced Database Management for Cognitive Forge v5.0
Dual-database architecture with SQLite and ChromaDB
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from loguru import logger
from datetime import datetime
import chromadb
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Database configuration
DATABASE_URL = "sqlite:///../db/sentinel_missions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Mission(Base):
    """Enhanced mission model with advanced tracking"""
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True)
    mission_id_str = Column(String, unique=True, index=True)
    title = Column(String)
    prompt = Column(Text)
    description = Column(Text, nullable=True)
    agent_type = Column(String, default="developer")
    status = Column(String, default="pending")
    result = Column(Text, nullable=True)  # JSON string
    plan = Column(JSON, nullable=True)
    execution_path = Column(String, nullable=True)  # "golden_path" or "full_workflow"
    complexity_score = Column(Float, nullable=True)
    decision_metadata = Column(JSON, nullable=True)  # Hybrid decision data
    execution_time = Column(Float, nullable=True)
    user_satisfaction = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class MissionUpdate(Base):
    """Real-time mission updates"""
    __tablename__ = "mission_updates"
    
    id = Column(Integer, primary_key=True)
    mission_id_str = Column(String, index=True)
    phase = Column(String)  # planning, execution, validation, etc.
    message = Column(Text)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """System-wide logging"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    level = Column(String)  # INFO, WARNING, ERROR, DEBUG
    source = Column(String)  # main, cognitive_engine, hybrid_engine
    message = Column(Text)
    log_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PerformanceMetric(Base):
    """Performance tracking for hybrid system"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    execution_path = Column(String)  # golden_path, full_workflow
    complexity_score = Column(Float)
    execution_time = Column(Float)
    success = Column(Boolean)
    user_satisfaction = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserPreference(Base):
    """User preference learning"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, default="default")
    preferred_path = Column(String)  # golden_path, full_workflow
    speed_preference = Column(Float)  # 0.0 = quality, 1.0 = speed
    complexity_preference = Column(Float)  # 0.0 = simple, 1.0 = complex
    satisfaction_history = Column(JSON)  # List of satisfaction scores
    last_updated = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Advanced database manager with dual-database support"""
    
    def __init__(self):
        # Ensure database directory exists
        db_dir = Path("../db")
        db_dir.mkdir(exist_ok=True)
        
        # Create SQLite tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize ChromaDB for vector memory
        chroma_path = "../db/chroma_memory"
        os.makedirs(chroma_path, exist_ok=True)
        
        try:
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            self.memory_collection = self.chroma_client.get_or_create_collection(
                "mission_memory",
                metadata={"description": "Cognitive Forge mission memory"}
            )
            logger.info("✅ ChromaDB memory system initialized successfully")
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            self.memory_collection = None
        
        logger.info("✅ Database system initialized successfully")
    
    def create_mission(self, **kwargs) -> Mission:
        """Create a new mission"""
        db = SessionLocal()
        try:
            mission = Mission(**kwargs)
            db.add(mission)
            db.commit()
            db.refresh(mission)
            logger.info(f"📝 Created mission: {mission.mission_id_str}")
            return mission
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create mission: {e}")
            raise
        finally:
            db.close()
    
    def update_mission_status(self, mission_id_str: str, status: str, 
                            result: str = None, error_message: str = None,
                            execution_time: float = None, user_satisfaction: float = None,
                            execution_path: str = None, complexity_score: float = None):
        """Update mission status with comprehensive tracking"""
        db = SessionLocal()
        try:
            mission = db.query(Mission).filter(Mission.mission_id_str == mission_id_str).first()
            if mission:
                mission.status = status
                mission.updated_at = datetime.utcnow()
                
                if result:
                    mission.result = result
                if error_message:
                    mission.error_message = error_message
                if execution_time is not None:
                    mission.execution_time = execution_time
                if user_satisfaction is not None:
                    mission.user_satisfaction = user_satisfaction
                
                if execution_path is not None:
                    mission.execution_path = execution_path
                
                if complexity_score is not None:
                    mission.complexity_score = complexity_score
                
                if status in ["completed", "failed"]:
                    mission.completed_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"📊 Updated mission {mission_id_str}: {status}")
            else:
                logger.warning(f"⚠️  Mission not found: {mission_id_str}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update mission {mission_id_str}: {e}")
            raise
        finally:
            db.close()
    
    def add_mission_update(self, mission_id_str: str, phase: str, message: str, data: Dict = None):
        """Add real-time mission update"""
        db = SessionLocal()
        try:
            update = MissionUpdate(
                mission_id_str=mission_id_str,
                phase=phase,
                message=message,
                data=data
            )
            db.add(update)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to add mission update: {e}")
        finally:
            db.close()
    
    def list_missions(self, limit: int = 50, status: str = None) -> List[Mission]:
        """List missions with optional filtering"""
        db = SessionLocal()
        try:
            query = db.query(Mission)
            if status:
                query = query.filter(Mission.status == status)
            return query.order_by(Mission.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    def get_mission(self, mission_id_str: str) -> Optional[Mission]:
        """Get specific mission"""
        db = SessionLocal()
        try:
            return db.query(Mission).filter(Mission.mission_id_str == mission_id_str).first()
        finally:
            db.close()
    
    def get_mission_updates(self, mission_id_str: str, limit: int = 50) -> List[MissionUpdate]:
        """Get mission updates"""
        db = SessionLocal()
        try:
            return db.query(MissionUpdate).filter(
                MissionUpdate.mission_id_str == mission_id_str
            ).order_by(MissionUpdate.timestamp.desc()).limit(limit).all()
        finally:
            db.close()
    
    def record_performance_metric(self, execution_path: str, complexity_score: float,
                                execution_time: float, success: bool, 
                                user_satisfaction: float = None):
        """Record performance metric for hybrid learning"""
        db = SessionLocal()
        try:
            metric = PerformanceMetric(
                execution_path=execution_path,
                complexity_score=complexity_score,
                execution_time=execution_time,
                success=success,
                user_satisfaction=user_satisfaction
            )
            db.add(metric)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to record performance metric: {e}")
        finally:
            db.close()
    
    def update_user_preferences(self, user_id: str, preferred_path: str,
                              speed_preference: float, complexity_preference: float,
                              satisfaction_score: float):
        """Update user preferences for learning"""
        db = SessionLocal()
        try:
            user_pref = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if user_pref:
                # Update existing preferences
                user_pref.preferred_path = preferred_path
                user_pref.speed_preference = speed_preference
                user_pref.complexity_preference = complexity_preference
                user_pref.last_updated = datetime.utcnow()
                
                # Update satisfaction history
                history = user_pref.satisfaction_history or []
                history.append(satisfaction_score)
                if len(history) > 100:  # Keep last 100 scores
                    history = history[-100:]
                user_pref.satisfaction_history = history
            else:
                # Create new user preferences
                user_pref = UserPreference(
                    user_id=user_id,
                    preferred_path=preferred_path,
                    speed_preference=speed_preference,
                    complexity_preference=complexity_preference,
                    satisfaction_history=[satisfaction_score]
                )
                db.add(user_pref)
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update user preferences: {e}")
        finally:
            db.close()
    
    def get_user_preferences(self, user_id: str = "default") -> Optional[UserPreference]:
        """Get user preferences"""
        db = SessionLocal()
        try:
            return db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
        finally:
            db.close()
    
    def add_to_memory(self, mission_id: str, content: str, metadata: Dict = None):
        """Add content to ChromaDB memory"""
        if not self.memory_collection:
            logger.warning("⚠️  ChromaDB not available for memory storage")
            return
        
        try:
            self.memory_collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[f"{mission_id}_{datetime.utcnow().timestamp()}"]
            )
            logger.info(f"💾 Added to memory: {mission_id}")
        except Exception as e:
            logger.error(f"❌ Failed to add to memory: {e}")
    
    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Search ChromaDB memory"""
        if not self.memory_collection:
            return []
        
        try:
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=limit
            )
            return [
                {
                    "content": doc,
                    "metadata": meta,
                    "distance": distance
                }
                for doc, meta, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]
        except Exception as e:
            logger.error(f"❌ Memory search failed: {e}")
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        db = SessionLocal()
        try:
            total_missions = db.query(Mission).count()
            pending_missions = db.query(Mission).filter(Mission.status == "pending").count()
            executing_missions = db.query(Mission).filter(Mission.status == "executing").count()
            completed_missions = db.query(Mission).filter(Mission.status == "completed").count()
            failed_missions = db.query(Mission).filter(Mission.status == "failed").count()
            
            # Performance metrics
            golden_path_metrics = db.query(PerformanceMetric).filter(
                PerformanceMetric.execution_path == "golden_path"
            ).all()
            full_workflow_metrics = db.query(PerformanceMetric).filter(
                PerformanceMetric.execution_path == "full_workflow"
            ).all()
            
            return {
                "missions": {
                    "total": total_missions,
                    "pending": pending_missions,
                    "executing": executing_missions,
                    "completed": completed_missions,
                    "failed": failed_missions
                },
                "performance": {
                    "golden_path": {
                        "count": len(golden_path_metrics),
                        "avg_time": sum(m.execution_time for m in golden_path_metrics) / len(golden_path_metrics) if golden_path_metrics else 0,
                        "success_rate": sum(1 for m in golden_path_metrics if m.success) / len(golden_path_metrics) if golden_path_metrics else 0
                    },
                    "full_workflow": {
                        "count": len(full_workflow_metrics),
                        "avg_time": sum(m.execution_time for m in full_workflow_metrics) / len(full_workflow_metrics) if full_workflow_metrics else 0,
                        "success_rate": sum(1 for m in full_workflow_metrics if m.success) / len(full_workflow_metrics) if full_workflow_metrics else 0
                    }
                },
                "memory": {
                    "chromadb_available": self.memory_collection is not None,
                    "collection_count": self.memory_collection.count() if self.memory_collection else 0
                }
            }
        finally:
            db.close()


# Global database manager instance
db_manager = DatabaseManager()
