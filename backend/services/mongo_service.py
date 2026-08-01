"""
Thin wrapper around the Motor async client.
Repositories import this; agents and services do NOT touch mongo_client directly.
"""
from motor.motor_asyncio import AsyncIOMotorCollection
from database.mongo_client import get_db


class MongoService:
    def collection(self, name: str) -> AsyncIOMotorCollection:
        return get_db()[name]
