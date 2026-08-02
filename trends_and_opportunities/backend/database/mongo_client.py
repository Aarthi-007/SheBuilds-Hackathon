from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

_client = AsyncIOMotorClient(settings.MONGODB_URI)


def get_db():
    return _client[settings.MONGODB_DB_NAME]
