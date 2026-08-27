from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from user_activity.ws_activity_manager import UserActivityWebSocketManager
from config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.mongo_client = AsyncMongoClient(settings.ME_CONFIG_MONGODB_URL)
    app.state.ws_manager = UserActivityWebSocketManager()

    yield

    await app.state.mongo_client.close()
