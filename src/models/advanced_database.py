import os
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import chromadb
from chromadb.config import Settings

class AdvancedDatabase:
    """Enhanced database system with Phase 2 support for execution blueprints and task tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize database connection
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/sentinel_missions.db")
        
        if DATABASE_URL.startswith("postgresql"):
            engine = create_engine(DATABASE_URL)
        else:
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        
        self.engine = engine
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        # Initialize ChromaDB for vector memory
        try:
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="db/chroma_memory"
            ))
            self.memory_collection = self.chroma_client.get_or_create_collection("mission_memory")
            self.logger.info("ChromaDB memory system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.memory_collection = None
        
        # Create tables
        self._create_tables()
        self._create_phase2_tables()
        
        self.logger.info(f"Database system initialized successfully with {DATABASE_URL}")
    
    def _create_tables(self):
        """Create basic tables for missions and memory"""
        try:
            # Missions table
            self.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS missions (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    result_data JSONB,
                    metadata JSONB
                )
            """))
            
            # Memory entries table
            self.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id SERIAL PRIMARY KEY,
                    mission_id INTEGER REFERENCES missions(id),
                    content TEXT NOT NULL,
                    context JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    importance_score FLOAT DEFAULT 0.5
                )
            """))
            
            self.logger.info("Basic database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating basic tables: {e}")
            raise
    
    def _create_phase2_tables(self):
        """Create Phase 2 tables for execution blueprints and task tracking"""
        try:
            # Execution Blueprints table
            self.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS execution_blueprints (
                    id SERIAL PRIMARY KEY,
                    mission_id INTEGER REFERENCES missions(id),
                    blueprint_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    status VARCHAR(20) DEFAULT 'draft',
                    validation_score INTEGER,
                    complexity_level VARCHAR(20),
                    estimated_duration_minutes INTEGER
                )
            """))
            
            # Task Executions table
            self.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS task_executions (
                    id SERIAL PRIMARY KEY,
                    blueprint_id INTEGER REFERENCES execution_blueprints(id),
                    mission_id INTEGER REFERENCES missions(id),
                    task_id_in_blueprint VARCHAR(50),
                    agent_used VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'pending',
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    actual_duration_ms INTEGER,
                    estimated_duration_ms INTEGER,
                    memory_usage_mb INTEGER,
                    cpu_usage_percent FLOAT,
                    log_summary TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Resource Monitoring table
            self.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS resource_monitoring (
                    id SERIAL PRIMARY KEY,
                    mission_id INTEGER REFERENCES missions(id),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    memory_usage_mb INTEGER,
                    cpu_usage_percent FLOAT,
                    active_tasks_count INTEGER,
                    completed_tasks_count INTEGER,
                    failed_tasks_count INTEGER,
                    system_load_average FLOAT
                )
            """))
            
            # Performance Analytics table
            self.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS performance_analytics (
                    id SERIAL PRIMARY KEY,
                    mission_id INTEGER REFERENCES missions(id),
                    blueprint_id INTEGER REFERENCES execution_blueprints(id),
                    metric_name VARCHAR(50),
                    metric_value FLOAT,
                    metric_unit VARCHAR(20),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    context JSONB
                )
            """))
            
            self.logger.info("Phase 2 database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating Phase 2 tables: {e}")
            raise
    
    def create_mission(self, title: str, description: str = None, status: str = "pending") -> dict:
        """Create a new mission"""
        try:
            result = self.engine.execute(text("""
                INSERT INTO missions (title, description, status)
                VALUES (%s, %s, %s)
                RETURNING id, created_at
            """), (title, description, status))
            
            mission_id, created_at = result.fetchone()
            
            mission = {
                'id': mission_id,
                'title': title,
                'description': description,
                'status': status,
                'created_at': created_at.isoformat() if created_at else None
            }
            
            self.logger.info(f"Created mission: {title}")
            return mission
            
        except Exception as e:
            self.logger.error(f"Error creating mission: {e}")
            raise
    
    def update_mission_status(self, mission_id: int, status: str, result_data: dict = None):
        """Update mission status and result data"""
        try:
            if result_data:
                self.engine.execute(text("""
                    UPDATE missions 
                    SET status = %s, result_data = %s, updated_at = NOW(),
                        completed_at = CASE WHEN %s IN ('completed', 'failed') THEN NOW() ELSE completed_at END
                    WHERE id = %s
                """), (status, json.dumps(result_data), status, mission_id))
            else:
                self.engine.execute(text("""
                    UPDATE missions 
                    SET status = %s, updated_at = NOW(),
                        completed_at = CASE WHEN %s IN ('completed', 'failed') THEN NOW() ELSE completed_at END
                    WHERE id = %s
                """), (status, status, mission_id))
            
            self.logger.info(f"Updated mission {mission_id} status to {status}")
            
        except Exception as e:
            self.logger.error(f"Error updating mission status: {e}")
            raise
    
    def get_mission(self, mission_id: int) -> dict:
        """Get mission by ID"""
        try:
            result = self.engine.execute(text("""
                SELECT id, title, description, status, created_at, updated_at, completed_at, result_data, metadata
                FROM missions
                WHERE id = %s
            """), (mission_id,))
            
            row = result.fetchone()
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'status': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'updated_at': row[5].isoformat() if row[5] else None,
                    'completed_at': row[6].isoformat() if row[6] else None,
                    'result_data': json.loads(row[7]) if row[7] else None,
                    'metadata': json.loads(row[8]) if row[8] else None
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting mission: {e}")
            raise
    
    def create_execution_blueprint(self, mission_id: int, blueprint_data: dict, 
                                 complexity_level: str = "medium", 
                                 estimated_duration_minutes: int = 60) -> dict:
        """Create a new execution blueprint"""
        try:
            result = self.engine.execute(text("""
                INSERT INTO execution_blueprints 
                (mission_id, blueprint_data, complexity_level, estimated_duration_minutes)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at
            """), (mission_id, json.dumps(blueprint_data), complexity_level, estimated_duration_minutes))
            
            blueprint_id, created_at = result.fetchone()
            
            blueprint = {
                'id': blueprint_id,
                'mission_id': mission_id,
                'blueprint_data': blueprint_data,
                'complexity_level': complexity_level,
                'estimated_duration_minutes': estimated_duration_minutes,
                'status': 'draft',
                'created_at': created_at.isoformat() if created_at else None
            }
            
            self.logger.info(f"Created execution blueprint: {blueprint_id}")
            return blueprint
            
        except Exception as e:
            self.logger.error(f"Error creating execution blueprint: {e}")
            raise
    
    def update_blueprint_status(self, blueprint_id: int, status: str, validation_score: int = None):
        """Update blueprint status and validation score"""
        try:
            if validation_score is not None:
                self.engine.execute(text("""
                    UPDATE execution_blueprints 
                    SET status = %s, validation_score = %s, updated_at = NOW()
                    WHERE id = %s
                """), (status, validation_score, blueprint_id))
            else:
                self.engine.execute(text("""
                    UPDATE execution_blueprints 
                    SET status = %s, updated_at = NOW()
                    WHERE id = %s
                """), (status, blueprint_id))
            
            self.logger.info(f"Updated blueprint {blueprint_id} status to {status}")
            
        except Exception as e:
            self.logger.error(f"Error updating blueprint status: {e}")
            raise
    
    def create_task_execution(self, blueprint_id: int, mission_id: int, 
                            task_id_in_blueprint: str, agent_used: str,
                            estimated_duration_ms: int = None) -> dict:
        """Create a new task execution record"""
        try:
            result = self.engine.execute(text("""
                INSERT INTO task_executions 
                (blueprint_id, mission_id, task_id_in_blueprint, agent_used, estimated_duration_ms)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """), (blueprint_id, mission_id, task_id_in_blueprint, agent_used, estimated_duration_ms))
            
            execution_id, created_at = result.fetchone()
            
            execution = {
                'id': execution_id,
                'blueprint_id': blueprint_id,
                'mission_id': mission_id,
                'task_id_in_blueprint': task_id_in_blueprint,
                'agent_used': agent_used,
                'status': 'pending',
                'estimated_duration_ms': estimated_duration_ms,
                'created_at': created_at.isoformat() if created_at else None
            }
            
            self.logger.info(f"Created task execution: {execution_id}")
            return execution
            
        except Exception as e:
            self.logger.error(f"Error creating task execution: {e}")
            raise
    
    def update_task_execution(self, execution_id: int, status: str, 
                            actual_duration_ms: int = None, memory_usage_mb: int = None,
                            cpu_usage_percent: float = None, log_summary: str = None,
                            error_message: str = None):
        """Update task execution with results"""
        try:
            update_fields = ["status = %s", "updated_at = NOW()"]
            params = [status]
            
            if actual_duration_ms is not None:
                update_fields.append("actual_duration_ms = %s")
                params.append(actual_duration_ms)
            
            if memory_usage_mb is not None:
                update_fields.append("memory_usage_mb = %s")
                params.append(memory_usage_mb)
            
            if cpu_usage_percent is not None:
                update_fields.append("cpu_usage_percent = %s")
                params.append(cpu_usage_percent)
            
            if log_summary is not None:
                update_fields.append("log_summary = %s")
                params.append(log_summary)
            
            if error_message is not None:
                update_fields.append("error_message = %s")
                params.append(error_message)
            
            if status in ['completed', 'failed']:
                update_fields.append("end_time = NOW()")
            
            params.append(execution_id)
            
            query = f"""
                UPDATE task_executions 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            
            self.engine.execute(text(query), params)
            self.logger.info(f"Updated task execution {execution_id} status to {status}")
            
        except Exception as e:
            self.logger.error(f"Error updating task execution: {e}")
            raise
    
    def record_resource_usage(self, mission_id: int, memory_usage_mb: int, 
                            cpu_usage_percent: float, active_tasks_count: int,
                            completed_tasks_count: int, failed_tasks_count: int,
                            system_load_average: float = None):
        """Record resource usage for monitoring"""
        try:
            self.engine.execute(text("""
                INSERT INTO resource_monitoring 
                (mission_id, memory_usage_mb, cpu_usage_percent, active_tasks_count,
                 completed_tasks_count, failed_tasks_count, system_load_average)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """), (mission_id, memory_usage_mb, cpu_usage_percent, active_tasks_count,
                  completed_tasks_count, failed_tasks_count, system_load_average))
            
        except Exception as e:
            self.logger.error(f"Error recording resource usage: {e}")
            raise
    
    def record_performance_metric(self, mission_id: int, blueprint_id: int, 
                                metric_name: str, metric_value: float, 
                                metric_unit: str, context: dict = None):
        """Record performance metrics for analytics"""
        try:
            self.engine.execute(text("""
                INSERT INTO performance_analytics 
                (mission_id, blueprint_id, metric_name, metric_value, metric_unit, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """), (mission_id, blueprint_id, metric_name, metric_value, metric_unit, 
                  json.dumps(context) if context else None))
            
        except Exception as e:
            self.logger.error(f"Error recording performance metric: {e}")
            raise
    
    def get_blueprint_by_mission(self, mission_id: int) -> dict:
        """Get execution blueprint for a mission"""
        try:
            result = self.engine.execute(text("""
                SELECT id, blueprint_data, status, validation_score, complexity_level,
                       estimated_duration_minutes, created_at, updated_at
                FROM execution_blueprints
                WHERE mission_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """), (mission_id,))
            
            row = result.fetchone()
            if row:
                return {
                    'id': row[0],
                    'blueprint_data': json.loads(row[1]) if isinstance(row[1], str) else row[1],
                    'status': row[2],
                    'validation_score': row[3],
                    'complexity_level': row[4],
                    'estimated_duration_minutes': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'updated_at': row[7].isoformat() if row[7] else None
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting blueprint: {e}")
            raise
    
    def get_task_executions_by_blueprint(self, blueprint_id: int) -> list:
        """Get all task executions for a blueprint"""
        try:
            result = self.engine.execute(text("""
                SELECT id, task_id_in_blueprint, agent_used, status, start_time, end_time,
                       actual_duration_ms, estimated_duration_ms, memory_usage_mb,
                       cpu_usage_percent, log_summary, error_message
                FROM task_executions
                WHERE blueprint_id = %s
                ORDER BY created_at
            """), (blueprint_id,))
            
            executions = []
            for row in result.fetchall():
                executions.append({
                    'id': row[0],
                    'task_id_in_blueprint': row[1],
                    'agent_used': row[2],
                    'status': row[3],
                    'start_time': row[4].isoformat() if row[4] else None,
                    'end_time': row[5].isoformat() if row[5] else None,
                    'actual_duration_ms': row[6],
                    'estimated_duration_ms': row[7],
                    'memory_usage_mb': row[8],
                    'cpu_usage_percent': row[9],
                    'log_summary': row[10],
                    'error_message': row[11]
                })
            
            return executions
            
        except Exception as e:
            self.logger.error(f"Error getting task executions: {e}")
            raise
    
    def get_mission_performance_analytics(self, mission_id: int) -> dict:
        """Get comprehensive performance analytics for a mission"""
        try:
            # Get resource usage over time
            resource_result = self.engine.execute(text("""
                SELECT timestamp, memory_usage_mb, cpu_usage_percent, active_tasks_count,
                       completed_tasks_count, failed_tasks_count
                FROM resource_monitoring
                WHERE mission_id = %s
                ORDER BY timestamp
            """), (mission_id,))
            
            resource_data = []
            for row in resource_result.fetchall():
                resource_data.append({
                    'timestamp': row[0].isoformat() if row[0] else None,
                    'memory_usage_mb': row[1],
                    'cpu_usage_percent': row[2],
                    'active_tasks_count': row[3],
                    'completed_tasks_count': row[4],
                    'failed_tasks_count': row[5]
                })
            
            # Get performance metrics
            metrics_result = self.engine.execute(text("""
                SELECT metric_name, metric_value, metric_unit, timestamp
                FROM performance_analytics
                WHERE mission_id = %s
                ORDER BY timestamp
            """), (mission_id,))
            
            metrics_data = []
            for row in metrics_result.fetchall():
                metrics_data.append({
                    'metric_name': row[0],
                    'metric_value': row[1],
                    'metric_unit': row[2],
                    'timestamp': row[3].isoformat() if row[3] else None
                })
            
            return {
                'resource_usage': resource_data,
                'performance_metrics': metrics_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance analytics: {e}")
            raise
    
    def store_memory(self, mission_id: int, content: str, context: dict = None, importance_score: float = 0.5):
        """Store memory in both SQL and vector databases"""
        try:
            # Store in SQL database
            self.engine.execute(text("""
                INSERT INTO memory_entries (mission_id, content, context, importance_score)
                VALUES (%s, %s, %s, %s)
            """), (mission_id, content, json.dumps(context) if context else None, importance_score))
            
            # Store in ChromaDB for vector search
            if self.memory_collection:
                self.memory_collection.add(
                    documents=[content],
                    metadatas=[{
                        'mission_id': mission_id,
                        'importance_score': importance_score,
                        'context': json.dumps(context) if context else None
                    }],
                    ids=[f"memory_{mission_id}_{datetime.now().timestamp()}"]
                )
            
            self.logger.info(f"Stored memory for mission {mission_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            raise
    
    def search_memory(self, query: str, limit: int = 10) -> list:
        """Search memory using vector similarity"""
        try:
            if not self.memory_collection:
                return []
            
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            memories = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Error searching memory: {e}")
            return [] 