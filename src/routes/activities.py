from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket

from user_activity.dependencies import get_user_activity_service
from user_activity.interfaces import UserActivityServiceInterface


users_activity_router = APIRouter()


@users_activity_router.websocket("/users/")
async def users_activity(
    websocket: WebSocket,
    activity_service: Annotated[UserActivityServiceInterface, Depends(get_user_activity_service)],
) -> None:
    """
    WebSocket endpoint for tracking user online/offline activity.

    Accepts a WebSocket connection and delegates the whole connection
    lifecycle (authentication, broadcasting connect/disconnect events,
    and cleanup on disconnect) to the activity service.

    Args:
        websocket (WebSocket): The incoming WebSocket connection.
        activity_service (UserActivityServiceInterface): Service responsible
            for handling the WebSocket connection lifecycle.

    Returns:
        None
    """
    await activity_service.process(websocket)
