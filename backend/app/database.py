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

# Patch mongomock authorizedCollections parameter compatibility
orig_list_col_names = mongomock.database.Database.list_collection_names
def patched_list_col_names(self, session=None, filter=None, **kwargs):
    kwargs.pop("authorizedCollections", None)
    return orig_list_col_names(self, session=session, filter=filter, **kwargs)
mongomock.database.Database.list_collection_names = patched_list_col_names


async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1000)
        await client.admin.command('ping')
        database = client[settings.DATABASE_NAME]
        await init_beanie(database=database, document_models=all_models)
        logger.info(f"Successfully connected to MongoDB database '{settings.DATABASE_NAME}'")
    except Exception as e:
        logger.info(f"Real MongoDB connection unavailable ({e}). Fallback to in-memory AsyncMongoMockClient database.")
        mock_client = mongomock_motor.AsyncMongoMockClient()
        mock_db = mock_client[settings.DATABASE_NAME]
        await init_beanie(database=mock_db, document_models=all_models)
        logger.info(f"Successfully initialized in-memory MongoDB database '{settings.DATABASE_NAME}' with Beanie.")
