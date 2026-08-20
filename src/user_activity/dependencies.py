from typing import Annotated

from fastapi import Depends, WebSocket, Request
from pymongo.asynchronous.database import AsyncDatabase

from config import get_settings, get_jwt_auth_manager
from security.interfaces import JWTAuthManagerInterface
from user_activity.activity_repo import UserActivityRepository
from user_activity.activity_service import UserActivityService
from user_activity.interfaces import UserActivityWebSocketManagerInterface, UserActivityRepoInterface
from user_activity.ws_activity_manager import UserActivityWebSocketManager


settings = get_settings()


def get_mongo_db(request: Request) -> AsyncDatabase:
    """
    Resolve the MongoDB database for HTTP request handlers.

    Reads the shared ``AsyncMongoClient`` from the application state, where it
    was placed during startup, so that every request reuses a single client and
    its connection pool instead of opening a new one.

    Args:
        request (Request): The incoming HTTP request, used to reach the
            application instance and its state.

    Returns:
        AsyncDatabase: The MongoDB database instance for activity storage.
    """
    return request.app.state.mongo_client[settings.MONGO_DB]


def get_mongo_db_ws(websocket: WebSocket) -> AsyncDatabase:
    """
    Resolve the MongoDB database for WebSocket handlers.

    Mirrors :func:`get_mongo_db`, but takes a ``WebSocket`` instead of a
    ``Request``: WebSocket routes never receive a ``Request`` object, so the
    application instance has to be reached through the socket itself. Both
    functions return a database backed by the same shared client.

    Args:
        websocket (WebSocket): The current WebSocket connection, used to reach
            the application instance and its state.

    Returns:
        AsyncDatabase: The MongoDB database instance for activity storage.
    """
    return websocket.app.state.mongo_client[settings.MONGO_DB]


def get_user_activity_repository(
    db: Annotated[AsyncDatabase, Depends(get_mongo_db)]
) -> UserActivityRepository:
    """
    Build a user activity repository for HTTP routes.

    Used by regular HTTP endpoints such as ``/accounts/login/``, where the
    database is resolved from the incoming request.

    Args:
        db (AsyncDatabase): The MongoDB database instance injected via
            :func:`get_mongo_db`.

    Returns:
        UserActivityRepository: A repository bound to the given database.
    """
    return UserActivityRepository(db)


def get_user_activity_repository_ws(
    db: Annotated[AsyncDatabase, Depends(get_mongo_db_ws)]
) -> UserActivityRepository:
    """
    Build a user activity repository for the WebSocket route.

    Consumed indirectly through :func:`get_user_activity_service`. It exists as
    a separate provider only because the database has to be resolved from a
    ``WebSocket`` rather than a ``Request``; the resulting repository is
    identical to the one returned by :func:`get_user_activity_repository`.

    Args:
        db (AsyncDatabase): The MongoDB database instance injected via
            :func:`get_mongo_db_ws`.

    Returns:
        UserActivityRepository: A repository bound to the given database.
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
            Depends(get_user_activity_repository_ws)
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
