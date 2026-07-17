from contextlib import asynccontextmanager

from fastapi import FastAPI

from user_activity.ws_activity_manager import UserActivityWebSocketManager
from config import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ws_manager = UserActivityWebSocketManager()
    yield
