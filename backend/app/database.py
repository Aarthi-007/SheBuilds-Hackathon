import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import mongomock
import mongomock_motor
from beanie import init_beanie
from app.config import settings
from app.models import all_models

logger = logging.getLogger("uvicorn")

# Patch Motor append_metadata compatibility with Beanie 2.x
setattr(AsyncIOMotorClient, "append_metadata", lambda self, *args, **kwargs: None)
setattr(AsyncIOMotorDatabase, "append_metadata", lambda self, *args, **kwargs: None)

# Patch mongomock Beanie 2.x parameter compatibility
orig_list_col_names = mongomock.database.Database.list_collection_names
def patched_list_col_names(self, session=None, filter=None, **kwargs):
    kwargs.pop("authorizedCollections", None)
    kwargs.pop("nameOnly", None)
    return orig_list_col_names(self, session=session, filter=filter, **kwargs)
mongomock.database.Database.list_collection_names = patched_list_col_names

_client: AsyncIOMotorClient | None = None
_mock_client: mongomock_motor.AsyncMongoMockClient | None = None
_database: AsyncIOMotorDatabase | None = None
_use_mock: bool = False

MAX_DB_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def get_client() -> AsyncIOMotorClient:
    global _client, _mock_client, _use_mock
    if _use_mock:
        if _mock_client is None:
            _mock_client = mongomock_motor.AsyncMongoMockClient()
        return _mock_client

    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    global _database
    if _database is None:
        client = get_client()
        _database = client[settings.DATABASE_NAME]
    return _database


async def init_db():
    global _client, _mock_client, _database, _use_mock
    if _database is not None:
        return

    for attempt in range(1, MAX_DB_RETRIES + 1):
        try:
            _client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
            await _client.admin.command("ping")
            database = _client[settings.DATABASE_NAME]
            await init_beanie(database=database, document_models=all_models)
            _database = database
            _use_mock = False
            logger.info("Successfully connected to MongoDB database '%s'", settings.DATABASE_NAME)
            return
        except Exception as e:
            logger.warning("MongoDB connection attempt %d/%d failed: %s", attempt, MAX_DB_RETRIES, e)
            if attempt < MAX_DB_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)

    logger.warning("Real MongoDB connection unavailable after %d attempts. Falling back to in-memory AsyncMongoMockClient database.", MAX_DB_RETRIES)
    _use_mock = True
    _mock_client = mongomock_motor.AsyncMongoMockClient()
    mock_db = _mock_client[settings.DATABASE_NAME]
    await init_beanie(database=mock_db, document_models=all_models)
    _database = mock_db
    logger.info("Successfully initialized in-memory MongoDB database '%s' with Beanie.", settings.DATABASE_NAME)


async def close_db():
    global _client, _mock_client, _database, _use_mock
    if _client is not None:
        _client.close()
        _client = None
    if _mock_client is not None and hasattr(_mock_client, "close"):
        try:
            _mock_client.close()
        except Exception:
            pass
        _mock_client = None
    _database = None
    _use_mock = False
