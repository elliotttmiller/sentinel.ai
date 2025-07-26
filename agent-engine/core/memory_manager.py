"""
Memory Manager for Project Sentinel.

Handles long-term memory and learning using vector databases.
Stores mission outcomes and retrieves relevant past experiences.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict

from pydantic import BaseModel, Field
from loguru import logger

# TODO: Import actual vector database client
# from chromadb import Client as ChromaClient
# from chromadb.config import Settings


@dataclass
class MissionMemory:
    """Memory entry for a completed mission."""
    mission_id: str
    user_prompt: str
    optimized_prompt: str
    execution_plan: Dict[str, Any]
    success: bool
    completed_steps: List[str]
    failed_steps: List[str]
    outputs: Dict[str, str]
    errors: Dict[str, str]
    duration: float
    timestamp: datetime
    metadata: Dict[str, Any]


class MemoryQuery(BaseModel):
    """Query for retrieving relevant memories."""
    query_text: str = Field(description="Text to search for in memories")
    max_results: int = Field(default=5, description="Maximum number of results to return")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity score")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")


class MemoryResult(BaseModel):
    """Result of a memory query."""
    memories: List[MissionMemory] = Field(description="Relevant memories found")
    similarity_scores: List[float] = Field(description="Similarity scores for each memory")
    total_found: int = Field(description="Total number of memories found")


class MemoryManager:
    """
    Manages long-term memory and learning for Project Sentinel.
    
    Responsibilities:
    - Store mission outcomes and experiences
    - Retrieve relevant past experiences
    - Enable continuous learning and improvement
    - Provide context for future missions
    """
    
    def __init__(self, vector_db_url: Optional[str] = None):
        self.vector_db_url = vector_db_url
        self.logger = logger.bind(component="memory_manager")
        
        # TODO: Initialize actual vector database client
        # self.client = ChromaClient(Settings(
        #     chroma_api_impl="rest",
        #     chroma_server_host=vector_db_url or "localhost",
        #     chroma_server_http_port=8000
        # ))
        # self.collection = self.client.get_or_create_collection("sentinel_memories")
        
        # For now, use in-memory storage
        self.memories: Dict[str, MissionMemory] = {}
        self.logger.info("Memory manager initialized with in-memory storage")
    
    async def store_mission_memory(self, memory: MissionMemory) -> str:
        """
        Store a mission memory in the vector database.
        
        Args:
            memory: The mission memory to store
            
        Returns:
            str: ID of the stored memory
        """
        memory_id = self._generate_memory_id(memory)
        self.logger.info(f"Storing mission memory: {memory_id}")
        
        # Create document for vector storage
        document = {
            "mission_id": memory.mission_id,
            "user_prompt": memory.user_prompt,
            "optimized_prompt": memory.optimized_prompt,
            "success": memory.success,
            "completed_steps": json.dumps(memory.completed_steps),
            "failed_steps": json.dumps(memory.failed_steps),
            "duration": memory.duration,
            "timestamp": memory.timestamp.isoformat(),
            "metadata": json.dumps(memory.metadata)
        }
        
        # Create embedding text for similarity search
        embedding_text = self._create_embedding_text(memory)
        
        # TODO: Store in actual vector database
        # self.collection.add(
        #     documents=[embedding_text],
        #     metadatas=[document],
        #     ids=[memory_id]
        # )
        
        # Store in memory for now
        self.memories[memory_id] = memory
        
        self.logger.info(f"Memory stored successfully: {memory_id}")
        return memory_id
    
    async def query_memories(self, query: MemoryQuery) -> MemoryResult:
        """
        Query memories for relevant past experiences.
        
        Args:
            query: The memory query to execute
            
        Returns:
            MemoryResult: Relevant memories and similarity scores
        """
        self.logger.info(f"Querying memories: {query.query_text}")
        
        # TODO: Use actual vector database query
        # results = self.collection.query(
        #     query_texts=[query.query_text],
        #     n_results=query.max_results,
        #     where=query.filters
        # )
        
        # For now, perform simple text matching
        relevant_memories = []
        similarity_scores = []
        
        for memory in self.memories.values():
            # Simple similarity calculation (replace with actual embedding similarity)
            similarity = self._calculate_similarity(query.query_text, memory)
            
            if similarity >= query.similarity_threshold:
                relevant_memories.append(memory)
                similarity_scores.append(similarity)
        
        # Sort by similarity score
        sorted_results = sorted(
            zip(relevant_memories, similarity_scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Limit results
        limited_results = sorted_results[:query.max_results]
        
        if limited_results:
            memories, scores = zip(*limited_results)
        else:
            memories, scores = [], []
        
        return MemoryResult(
            memories=list(memories),
            similarity_scores=list(scores),
            total_found=len(relevant_memories)
        )
    
    async def get_memory_by_id(self, memory_id: str) -> Optional[MissionMemory]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[MissionMemory]: The memory if found
        """
        return self.memories.get(memory_id)
    
    async def get_successful_memories(self, limit: int = 10) -> List[MissionMemory]:
        """
        Get recent successful mission memories.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List[MissionMemory]: Successful mission memories
        """
        successful_memories = [
            memory for memory in self.memories.values()
            if memory.success
        ]
        
        # Sort by timestamp (most recent first)
        sorted_memories = sorted(
            successful_memories,
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        return sorted_memories[:limit]
    
    async def get_failed_memories(self, limit: int = 10) -> List[MissionMemory]:
        """
        Get recent failed mission memories for learning.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List[MissionMemory]: Failed mission memories
        """
        failed_memories = [
            memory for memory in self.memories.values()
            if not memory.success
        ]
        
        # Sort by timestamp (most recent first)
        sorted_memories = sorted(
            failed_memories,
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        return sorted_memories[:limit]
    
    async def get_memories_by_agent_role(self, agent_role: str, limit: int = 10) -> List[MissionMemory]:
        """
        Get memories involving a specific agent role.
        
        Args:
            agent_role: The agent role to filter by
            limit: Maximum number of memories to return
            
        Returns:
            List[MissionMemory]: Memories involving the specified agent role
        """
        relevant_memories = []
        
        for memory in self.memories.values():
            # Check if the agent role was involved in this mission
            if self._agent_role_in_memory(memory, agent_role):
                relevant_memories.append(memory)
        
        # Sort by timestamp (most recent first)
        sorted_memories = sorted(
            relevant_memories,
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        return sorted_memories[:limit]
    
    def _generate_memory_id(self, memory: MissionMemory) -> str:
        """Generate a unique ID for a memory."""
        content = f"{memory.mission_id}{memory.timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _create_embedding_text(self, memory: MissionMemory) -> str:
        """Create text for embedding generation."""
        return f"""
        Mission: {memory.mission_id}
        User Prompt: {memory.user_prompt}
        Optimized Prompt: {memory.optimized_prompt}
        Success: {memory.success}
        Completed Steps: {', '.join(memory.completed_steps)}
        Failed Steps: {', '.join(memory.failed_steps)}
        Duration: {memory.duration}
        Metadata: {json.dumps(memory.metadata)}
        """
    
    def _calculate_similarity(self, query: str, memory: MissionMemory) -> float:
        """
        Calculate similarity between query and memory.
        
        This is a simple implementation. In production, use actual embeddings.
        """
        query_lower = query.lower()
        memory_text = self._create_embedding_text(memory).lower()
        
        # Simple word overlap similarity
        query_words = set(query_lower.split())
        memory_words = set(memory_text.split())
        
        if not query_words or not memory_words:
            return 0.0
        
        intersection = query_words.intersection(memory_words)
        union = query_words.union(memory_words)
        
        return len(intersection) / len(union)
    
    def _agent_role_in_memory(self, memory: MissionMemory, agent_role: str) -> bool:
        """Check if an agent role was involved in a memory."""
        # Check execution plan for agent role
        if "steps" in memory.execution_plan:
            for step in memory.execution_plan["steps"]:
                if step.get("agent_role") == agent_role:
                    return True
        
        # Check completed and failed steps
        all_steps = memory.completed_steps + memory.failed_steps
        for step_id in all_steps:
            if agent_role in step_id.lower():
                return True
        
        return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        total_memories = len(self.memories)
        successful_memories = sum(1 for m in self.memories.values() if m.success)
        failed_memories = total_memories - successful_memories
        
        if total_memories > 0:
            success_rate = successful_memories / total_memories
        else:
            success_rate = 0.0
        
        return {
            "total_memories": total_memories,
            "successful_memories": successful_memories,
            "failed_memories": failed_memories,
            "success_rate": success_rate,
            "oldest_memory": min((m.timestamp for m in self.memories.values()), default=None),
            "newest_memory": max((m.timestamp for m in self.memories.values()), default=None)
        } 