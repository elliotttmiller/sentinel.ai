"""
GraphQL endpoint for SentinelAI dashboard data (agents, analytics, etc.)
"""
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List
from dataclasses import dataclass

@dataclass
class AgentType:
    id: str
    name: str
    description: str

@strawberry.type
class Agent:
    id: strawberry.ID
    name: str
    description: str

@strawberry.type
class Query:
    @strawberry.field
    def available_agents(self) -> List[Agent]:
        # Example static data; replace with DB/service call
        agent1 = Agent(id=strawberry.ID("1"), name="Gemini Pro", description="Google Gemini 1.5 Pro agent")
        agent2 = Agent(id=strawberry.ID("2"), name="Sentinel", description="SentinelAI system agent")
        return [agent1, agent2]
# To enable this endpoint, add the following to your FastAPI app initialization (e.g., in main.py):
# from src.api.graphql import graphql_app
# app.include_router(graphql_app, prefix="/api/graphql")

schema = strawberry.Schema(Query)
graphql_app = GraphQLRouter(schema)
