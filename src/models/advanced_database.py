
"""
Advanced Database Management for Cognitive Forge v6.0
Dual-database architecture with SQLite and ChromaDB
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
# Removed unused imports: func, logger

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../db/sentinel_missions.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Organization and User models are missing, add them:
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    users = relationship("User", back_populates="organization")
    missions = relationship("Mission", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    organization = relationship("Organization", back_populates="users")
    missions = relationship("Mission", back_populates="owner")

class Mission(Base):
    """Enhanced mission model with advanced tracking and multi-tenancy"""
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True)
    mission_id_str = Column(String, unique=True, index=True)
    title = Column(String)
    prompt = Column(Text)
    description = Column(Text, nullable=True)
    agent_type = Column(String, default="developer")
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)  # Progress tracking
    priority = Column(String, default="medium")  # Priority tracking
    result = Column(Text, nullable=True)  # JSON string
    plan = Column(JSON, nullable=True)
    execution_path = Column(String, nullable=True)  # "golden_path" or "full_workflow"
    complexity_score = Column(Float, nullable=True)
    decision_metadata = Column(JSON, nullable=True)  # Hybrid decision data
    execution_time = Column(Float, nullable=True)
    user_satisfaction = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    
    # NEW: Fields for Phoenix Protocol tracking
    is_healing = Column(Boolean, default=False)
    phoenix_retries = Column(Integer, default=0)
    
    # NEW: Columns for Multi-Tenancy and Predictive Analysis
    owner_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    owner = relationship("User", back_populates="missions")
    organization = relationship("Organization", back_populates="missions")
    prompt_analysis = Column(JSON, nullable=True)  # Guardian Protocol analysis
    risk_score = Column(Float, nullable=True)  # Risk assessment score
    
    def as_dict(self):
        # Convert all columns to a dictionary, handling datetime objects
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key, value in d.items():
            if isinstance(value, datetime):
                d[key] = value.isoformat()
        return d


# NEW: Table for Self-Optimization Proposals
class OptimizationProposal(Base):
    __tablename__ = "optimization_proposals"
    
    id = Column(Integer, primary_key=True)
    proposal_type = Column(String)
    description = Column(Text)
    rationale = Column(Text)
    status = Column(String, default="pending") # pending, applied, rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key, value in d.items():
            if isinstance(value, datetime):
                d[key] = value.isoformat()
        return d


class MissionUpdate(Base):
    """Real-time mission updates"""
    __tablename__ = "mission_updates"
    
    id = Column(Integer, primary_key=True)
    mission_id_str = Column(String, index=True)
    phase = Column(String)  # planning, execution, validation, etc.
    message = Column(Text)
    data = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SystemLog(Base):
    """System-wide logging"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    level = Column(String)  # INFO, WARNING, ERROR, DEBUG
    source = Column(String)  # main, cognitive_engine, hybrid_engine
    message = Column(Text)
    log_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserPreference(Base):
    """User preference learning"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, default="default")
    preferred_path = Column(String)  # golden_path, full_workflow
    speed_preference = Column(Float)  # 0.0 = quality, 1.0 = speed
    complexity_preference = Column(Float)  # 0.0 = simple, 1.0 = complex
    satisfaction_history = Column(JSON)  # List of satisfaction scores
    created_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# (Removed duplicate and partial DatabaseManager class and stray __init__ function)

class DatabaseManager:
    def __init__(self):
        db_dir = Path("db")
        db_dir.mkdir(exist_ok=True)
        Base.metadata.create_all(bind=engine)

    def get_or_create_default_user_and_org(self):
        db = SessionLocal()
        try:
            org = db.query(Organization).filter(Organization.name == "Default Organization").first()
            if not org:
                org = Organization(name="Default Organization")
                db.add(org)
                db.commit()
                db.refresh(org)
            
            user = db.query(User).filter(User.username == "default_user").first()
            if not user:
                user = User(username="default_user", email="default@sentinel.ai", organization_id=org.id)
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        finally:
            db.close()

    def create_mission(self, **kwargs) -> Mission:
        db = SessionLocal()
        try:
            kwargs.setdefault('progress', 0)
            kwargs.setdefault('organization_id', 1)
            mission = Mission(**kwargs)
            db.add(mission)
            db.commit()
            db.refresh(mission)
            return mission
        finally:
            db.close()

    def get_mission(self, mission_id_str: str) -> Optional[Mission]:
        db = SessionLocal()
        try:
            return db.query(Mission).filter(Mission.mission_id_str == mission_id_str).first()
        finally:
            db.close()
    
    def get_mission_updates(self, mission_id_str: str) -> List[MissionUpdate]:
        db = SessionLocal()
        try:
            return db.query(MissionUpdate).filter(MissionUpdate.mission_id_str == mission_id_str).all()
        finally:
            db.close()
    
    def add_mission_update(self, mission_id_str: str, phase: str, message: str, metadata: Optional[dict] = None):
        db = SessionLocal()
        try:
            update = MissionUpdate(
                mission_id_str=mission_id_str,
                phase=phase,
                message=message,
                data=metadata or {}
            )
            db.add(update)
            db.commit()
        finally:
            db.close()
    
    def update_mission_status(self, mission_id_str: str, status: str, **kwargs):
        db = SessionLocal()
        try:
            mission = db.query(Mission).filter(Mission.mission_id_str == mission_id_str).first()
            if mission:
                setattr(mission, 'status', status)
                for key, value in kwargs.items():
                    if hasattr(mission, key):
                        setattr(mission, key, value)
                db.commit()
        finally:
            db.close()
    
    def get_pending_proposals(self) -> List[OptimizationProposal]:
        db = SessionLocal()
        try:
            return db.query(OptimizationProposal).filter(OptimizationProposal.status == "pending").all()
        finally:
            db.close()
    
    def update_proposal_status(self, proposal_id: int, status: str) -> Optional[OptimizationProposal]:
        db = SessionLocal()
        try:
            proposal = db.query(OptimizationProposal).filter(OptimizationProposal.id == proposal_id).first()
            if proposal:
                setattr(proposal, 'status', status)
                db.refresh(proposal)
            return proposal
        finally:
            db.close()
    
    def get_system_stats(self) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            total_missions = db.query(Mission).count()
            completed_missions = db.query(Mission).filter(Mission.status == "completed").count()
            failed_missions = db.query(Mission).filter(Mission.status == "failed").count()
            
            return {
                "total_missions": total_missions,
                "completed_missions": completed_missions,
                "failed_missions": failed_missions,
                "healing_missions": 0,
                "avg_execution_time": 30,
                "success_rate": completed_missions / max(total_missions, 1),
                "active_optimizations": 0
            }
        finally:
            db.close()
    
    def get_performance_data_for_analytics(self, org_id: int = 1) -> List[Dict[str, Any]]:
        # org_id parameter is currently unused
        return []
    def list_missions(self, limit: int = 50) -> List[Mission]:
        db = SessionLocal()
        try:
            return db.query(Mission).order_by(Mission.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    def create_optimization_proposal(self, proposal_type: str, description: str, rationale: str) -> OptimizationProposal:
        db = SessionLocal()
        try:
            proposal = OptimizationProposal(
                proposal_type=proposal_type,
                description=description,
                rationale=rationale
            )
            db.add(proposal)
            db.commit()
            db.refresh(proposal)
            return proposal
        finally:
            db.close()


# Global database manager instance
db_manager = DatabaseManager()
