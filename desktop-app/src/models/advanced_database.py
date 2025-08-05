"""
Advanced Database Management for Cognitive Forge v5.4 (Sentience & Multi-Tenancy Update)
Dual-database architecture with SQLite and ChromaDB
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from loguru import logger
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    case,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

# Database configuration
DATABASE_URL = "sqlite:///../db/sentinel_missions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- NEW: Models for Multi-Tenancy ---
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    missions = relationship("Mission", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    status = Column(String, default="pending")  # pending, applied, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    """Enhanced database manager with Phase 5 features"""

    def __init__(self):
        # Ensure database directory exists
        db_dir = Path("../db")
        db_dir.mkdir(exist_ok=True)

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Initialize ChromaDB for memory
        try:
            chroma_client = chromadb.PersistentClient(path="../db/chroma_memory")
            self.memory_collection = chroma_client.get_or_create_collection(
                "mission_memory"
            )
            logger.info("✅ ChromaDB memory system initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB initialization failed: {e}")
            self.memory_collection = None

        logger.info("✅ Database system initialized successfully")

    # --- NEW: User and Organization Management ---
    def get_or_create_default_user_and_org(self) -> User:
        """Get or create default user and organization for multi-tenancy"""
        db = SessionLocal()
        try:
            # Create default organization if it doesn't exist
            org = (
                db.query(Organization)
                .filter(Organization.name == "Default Organization")
                .first()
            )
            if not org:
                org = Organization(name="Default Organization")
                db.add(org)
                db.commit()
                db.refresh(org)

            # Create default user if it doesn't exist
            user = db.query(User).filter(User.username == "default_user").first()
            if not user:
                user = User(
                    username="default_user",
                    email="default@sentinel.ai",
                    organization_id=org.id,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            return user
        finally:
            db.close()

    def create_mission(self, **kwargs) -> Mission:
        """Create a new mission with enhanced tracking and multi-tenancy"""
        db = SessionLocal()
        try:
            # Ensure progress is set if not provided
            kwargs.setdefault("progress", 0)
            mission = Mission(**kwargs)
            db.add(mission)
            db.commit()
            db.refresh(mission)
            logger.info(f"📝 Created mission: {mission.mission_id_str}")
            return mission
        finally:
            db.close()

    def update_mission_status(
        self,
        mission_id_str: str,
        status: str,
        result: Optional[str] = None,
        error_message: Optional[str] = None,
        progress: Optional[int] = None,
        is_healing: Optional[bool] = None,
    ):
        """Update mission status with enhanced tracking"""
        db = SessionLocal()
        try:
            mission = (
                db.query(Mission)
                .filter(Mission.mission_id_str == mission_id_str)
                .first()
            )
            if mission:
                mission.status = status
                mission.updated_at = datetime.utcnow()
                if result is not None:
                    mission.result = result
                if error_message is not None:
                    mission.error_message = error_message
                if progress is not None:
                    mission.progress = progress
                if is_healing is not None:
                    mission.is_healing = is_healing
                if status in ["completed", "failed"]:
                    mission.completed_at = datetime.utcnow()
                db.commit()
            else:
                logger.warning(f"⚠️ Mission not found for update: {mission_id_str}")
        finally:
            db.close()

    def increment_phoenix_retry(self, mission_id_str: str) -> int:
        """Increment Phoenix Protocol retry counter"""
        db = SessionLocal()
        try:
            mission = (
                db.query(Mission)
                .filter(Mission.mission_id_str == mission_id_str)
                .first()
            )
            if mission:
                mission.phoenix_retries = (mission.phoenix_retries or 0) + 1
                db.commit()
                return mission.phoenix_retries
            return 0
        finally:
            db.close()

    def get_mission(self, mission_id_str: str, org_id: int = 1) -> Optional[Mission]:
        """Get mission by ID with organization scoping"""
        db = SessionLocal()
        try:
            return (
                db.query(Mission)
                .filter(
                    Mission.mission_id_str == mission_id_str,
                    Mission.organization_id == org_id,
                )
                .first()
            )
        finally:
            db.close()

    def list_missions(
        self, org_id: int = 1, limit: int = 50, status: Optional[str] = None
    ) -> List[Mission]:
        """List missions with optional status filter and organization scoping"""
        db = SessionLocal()
        try:
            query = db.query(Mission).filter(Mission.organization_id == org_id)
            if status:
                query = query.filter(Mission.status == status)
            return query.order_by(Mission.created_at.desc()).limit(limit).all()
        finally:
            db.close()

    def add_mission_update(
        self, mission_id_str: str, phase: str, message: str, data: Dict = None
    ):
        """Add real-time mission update"""
        db = SessionLocal()
        try:
            update = MissionUpdate(
                mission_id_str=mission_id_str, phase=phase, message=message, data=data
            )
            db.add(update)
            db.commit()
        finally:
            db.close()

    def get_mission_updates(
        self, mission_id_str: str, limit: int = 50
    ) -> List[MissionUpdate]:
        """Get mission updates"""
        db = SessionLocal()
        try:
            return (
                db.query(MissionUpdate)
                .filter(MissionUpdate.mission_id_str == mission_id_str)
                .order_by(MissionUpdate.timestamp.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def record_performance_metric(
        self,
        execution_path: str,
        complexity_score: float,
        execution_time: float,
        success: bool,
        user_satisfaction: float = None,
    ):
        """Record performance metrics"""
        db = SessionLocal()
        try:
            metric = PerformanceMetric(
                execution_path=execution_path,
                complexity_score=complexity_score,
                execution_time=execution_time,
                success=success,
                user_satisfaction=user_satisfaction,
            )
            db.add(metric)
            db.commit()
        finally:
            db.close()

    def update_user_preferences(
        self,
        user_id: str,
        preferred_path: str,
        speed_preference: float,
        complexity_preference: float,
        satisfaction_score: float,
    ):
        """Update user preferences with learning"""
        db = SessionLocal()
        try:
            # Get existing preferences or create new
            prefs = (
                db.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )

            if not prefs:
                prefs = UserPreference(
                    user_id=user_id,
                    preferred_path=preferred_path,
                    speed_preference=speed_preference,
                    complexity_preference=complexity_preference,
                    satisfaction_history=[satisfaction_score],
                )
                db.add(prefs)
            else:
                # Update preferences with learning
                prefs.preferred_path = preferred_path
                prefs.speed_preference = speed_preference
                prefs.complexity_preference = complexity_preference

                # Add to satisfaction history
                if not prefs.satisfaction_history:
                    prefs.satisfaction_history = []
                prefs.satisfaction_history.append(satisfaction_score)

                # Keep only last 10 scores
                if len(prefs.satisfaction_history) > 10:
                    prefs.satisfaction_history = prefs.satisfaction_history[-10:]

            db.commit()
        finally:
            db.close()

    def get_user_preferences(
        self, user_id: str = "default"
    ) -> Optional[UserPreference]:
        """Get user preferences"""
        db = SessionLocal()
        try:
            return (
                db.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
        finally:
            db.close()

    def add_to_memory(self, mission_id: str, content: str, metadata: Dict = None):
        """Add content to ChromaDB memory"""
        if not self.memory_collection:
            return

        try:
            self.memory_collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[f"{mission_id}_{len(self.memory_collection.get()['ids'])}"],
            )
        except Exception as e:
            logger.warning(f"Failed to add to memory: {e}")

    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Search ChromaDB memory"""
        if not self.memory_collection:
            return []

        try:
            results = self.memory_collection.query(query_texts=[query], n_results=limit)
            return [
                {"content": doc, "metadata": meta, "distance": dist}
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        except Exception as e:
            logger.warning(f"Memory search failed: {e}")
            return []

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        db = SessionLocal()
        try:
            total_missions = db.query(Mission).count()
            completed_missions = (
                db.query(Mission).filter(Mission.status == "completed").count()
            )
            failed_missions = (
                db.query(Mission).filter(Mission.status == "failed").count()
            )
            healing_missions = (
                db.query(Mission).filter(Mission.is_healing == True).count()
            )

            # Get recent performance metrics
            recent_metrics = (
                db.query(PerformanceMetric)
                .order_by(PerformanceMetric.timestamp.desc())
                .limit(10)
                .all()
            )

            avg_execution_time = 0
            success_rate = 0
            if recent_metrics:
                avg_execution_time = sum(
                    m.execution_time for m in recent_metrics
                ) / len(recent_metrics)
                success_rate = sum(1 for m in recent_metrics if m.success) / len(
                    recent_metrics
                )

            return {
                "total_missions": total_missions,
                "completed_missions": completed_missions,
                "failed_missions": failed_missions,
                "healing_missions": healing_missions,
                "avg_execution_time": avg_execution_time,
                "success_rate": success_rate,
                "active_optimizations": db.query(OptimizationProposal)
                .filter(OptimizationProposal.status == "pending")
                .count(),
            }
        finally:
            db.close()

    # --- NEW: Analytics Data for Phase 5 ---
    def get_performance_data_for_analytics(self, org_id: int = 1) -> List[Dict]:
        """Get performance data for analytics charts"""
        db = SessionLocal()
        try:
            # Aggregate data for charting
            results = (
                db.query(
                    func.date(Mission.completed_at).label("date"),
                    func.count(Mission.id).label("total"),
                    func.sum(case((Mission.status == "completed", 1), else_=0)).label(
                        "successful"
                    ),
                )
                .filter(Mission.organization_id == org_id, Mission.completed_at != None)
                .group_by("date")
                .order_by("date")
                .all()
            )

            return [
                {"date": r.date, "total": r.total, "successful": r.successful}
                for r in results
            ]
        finally:
            db.close()

    # --- Methods for managing optimization proposals ---
    def create_optimization_proposal(
        self, proposal_type: str, description: str, rationale: str
    ) -> OptimizationProposal:
        """Create a new optimization proposal"""
        db = SessionLocal()
        try:
            proposal = OptimizationProposal(
                proposal_type=proposal_type,
                description=description,
                rationale=rationale,
            )
            db.add(proposal)
            db.commit()
            db.refresh(proposal)
            logger.info(f"💡 New optimization proposal created: {description[:50]}...")
            return proposal
        finally:
            db.close()

    def get_pending_proposals(self) -> List[OptimizationProposal]:
        """Get all pending optimization proposals"""
        db = SessionLocal()
        try:
            return (
                db.query(OptimizationProposal)
                .filter(OptimizationProposal.status == "pending")
                .order_by(OptimizationProposal.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def update_proposal_status(
        self, proposal_id: int, status: str
    ) -> Optional[OptimizationProposal]:
        """Update optimization proposal status"""
        db = SessionLocal()
        try:
            proposal = (
                db.query(OptimizationProposal)
                .filter(OptimizationProposal.id == proposal_id)
                .first()
            )
            if proposal:
                proposal.status = status
                db.commit()
                db.refresh(proposal)
                return proposal
            return None
        finally:
            db.close()


# Global database manager instance
db_manager = DatabaseManager()
