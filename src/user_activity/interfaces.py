from abc import ABC, abstractmethod
from typing import List

from fastapi import WebSocket

from schemas.user_activity import (
    UserBaseDTO,
    UpdateUserActivitySchema,
    UserActivitySchema
)


class UserActivityRepoInterface(ABC):
    """Abstract interface for persisting and querying user online activity."""

    @abstractmethod
    async def create_user_activity(self, user_data: UserBaseDTO) -> None:
        """
        Create the initial activity record for a user.

        Args:
            user_data (UserBaseDTO): Basic user data used to seed the record.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def update_user_activity(self, user_data: UpdateUserActivitySchema) -> UpdateUserActivitySchema:
        """
        Update a user's activity status.

        Args:
            user_data (UpdateUserActivitySchema): Fields to update on the activity record.

        Returns:
            UserActivitySchema: The updated activity record.
        """
        pass

    @abstractmethod
    async def get_all_active_users(self) -> List[UserActivitySchema]:
        """
        Retrieve all currently online users.

        Returns:
            List[UserActivitySchema]: Activity records for all online users.
        """
        pass


class UserActivityWebSocketManagerInterface(ABC):
    """Abstract interface for managing active WebSocket connections and broadcasting activity events."""

    @abstractmethod
    async def connect(self, websocket: WebSocket, user_data: UserActivitySchema) -> None:
        """
        Register a new WebSocket connection for a user.

        Args:
            websocket (WebSocket): The WebSocket connection to register.
            user_data (UserActivitySchema): The connecting user's activity data.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection for a user.

        Args:
            user_id (int): The ID of the disconnecting user.
            websocket (WebSocket): The WebSocket connection to remove.

        Returns:
             None
        """
        pass

    @abstractmethod
    async def _broadcast(self, message: dict, exclude: int = None) -> None:
        """
        Broadcast a message to all connected users, optionally excluding one user.

        Args:
            message (dict): The message payload to broadcast.
            exclude (Optional[int]): User ID to exclude from the broadcast, if any.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def send_personal_message(self, message: dict, user_id: int) -> None:
        """
        Send a message to all active connections of a single user.

        Args:
            message (dict): The message payload to send.
            user_id (int): The ID of the user to send the message to.

        Returns:
            None
        """
        pass


class UserActivityServiceInterface(ABC):

    @abstractmethod
    async def process(self, websocket: WebSocket) -> None:
        """
        Handle a single WebSocket connection end-to-end (auth, tracking, cleanup).

        Args:
            websocket (WebSocket): The incoming WebSocket connection.

        Returns:
            None
        """
        pass
