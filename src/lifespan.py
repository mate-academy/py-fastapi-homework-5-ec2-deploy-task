from contextlib import asynccontextmanager

from fastapi import FastAPI

from user_activity.ws_activity_manager import UserActivityWebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ws_manager = UserActivityWebSocketManager()
    yield
