import asyncio
from typing import Annotated

from fastapi import Depends, WebSocket
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import get_settings, get_jwt_auth_manager
from security.interfaces import JWTAuthManagerInterface
from user_activity.activity_repo import UserActivityRepository
from user_activity.activity_service import UserActivityService
from user_activity.interfaces import UserActivityWebSocketManagerInterface, UserActivityRepoInterface
from user_activity.ws_activity_manager import UserActivityWebSocketManager


settings = get_settings()

client = AsyncIOMotorClient(settings.ME_CONFIG_MONGODB_URL)
client.get_io_loop = asyncio.get_running_loop


def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Provide the configured MongoDB database instance for dependency injection.

    Returns:
        AsyncIOMotorDatabase: The Motor database instance used for activity storage.
    """
    return client[settings.MONGO_DB]


def get_user_activity_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)]
) -> UserActivityRepository:
    """
    Build a UserActivityRepository bound to the injected MongoDB database.

    Args:
        db (AsyncIOMotorDatabase): The MongoDB database instance.

    Returns:
        UserActivityRepository: A repository instance for user activity persistence.
    """
    return UserActivityRepository(db)


def get_user_activity_ws_manager(websocket: WebSocket) -> UserActivityWebSocketManager:
    """
    Retrieve the shared WebSocket manager stored on the application state.

    Args:
        websocket (WebSocket): The current WebSocket connection, used to access the app instance.

    Returns:
        UserActivityWebSocketManager: The application-wide WebSocket connection manager.
    """
    return websocket.app.state.ws_manager


def get_user_activity_service(
        auth_manager: Annotated[
            JWTAuthManagerInterface,
            Depends(get_jwt_auth_manager)
        ],
        activity_ws_manager: Annotated[
            UserActivityWebSocketManagerInterface,
            Depends(get_user_activity_ws_manager)
        ],
        activity_repo: Annotated[
            UserActivityRepoInterface,
            Depends(get_user_activity_repository)
        ]
) -> UserActivityService:
    """
    Assemble a UserActivityService with all of its required dependencies.

    Args:
        auth_manager (JWTAuthManagerInterface): Manager used to decode access tokens.
        activity_ws_manager (UserActivityWebSocketManagerInterface): Manager for active WebSocket connections.
        activity_repo (UserActivityRepoInterface): Repository for persisting user activity state.

    Returns:
        UserActivityService: A fully configured user activity service instance.
    """
    return UserActivityService(
        manager=activity_ws_manager,
        activity_repo=activity_repo,
        jwt_auth_manager=auth_manager
    )
