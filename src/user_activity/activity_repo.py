from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.user_activity import UserBaseDTO, UpdateUserActivitySchema, UserActivitySchema
from user_activity.interfaces import UserActivityRepoInterface


class UserActivityRepository(UserActivityRepoInterface):
    """MongoDB-backed implementation of the user activity repository."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        """
        Initialize the repository with a MongoDB database instance.

        Args:
            db (AsyncIOMotorDatabase): The Motor async MongoDB database instance.
        """
        self.db = db

    async def create_user_activity(self, user_data: UserBaseDTO) -> None:
        """
        Create or reset a user's activity record with an initial "offline" status.

        Args:
            user_data (UserBaseDTO): Basic user data (id and email) to seed the activity record.

        Returns:
            None
        """
        await self.db["user_activity"].update_one(
            {"user_id": user_data.id},
            {"$set": {"email": user_data.email, "status": "offline"}},
            upsert=True
        )

    async def update_user_activity(
            self,
            user_data: UpdateUserActivitySchema
    ) -> UserActivitySchema:
        """
        Update (or create) a user's activity record and return the resulting document.

        Args:
            user_data (UpdateUserActivitySchema): Fields to update on the user's activity record.

        Returns:
            UserActivitySchema: The updated activity record.
        """
        await self.db["user_activity"].update_one(
            {"user_id": user_data.user_id},
            {"$set": user_data.model_dump(exclude_none=True)},
            upsert=True
        )
        result = await self.db["user_activity"].find_one(
            {"user_id": user_data.user_id},
            {"_id": 0}
        )
        return UserActivitySchema.model_validate(result)

    async def get_all_active_users(self) -> List[UserActivitySchema]:
        """
        Retrieve all users that currently have an "online" status.

        Returns:
            List[UserActivitySchema]: A list of activity records for all online users.
        """
        users = await self.db["user_activity"].find(
            {"status": "online"},
            {"_id": 0}
        ).to_list()

        return [UserActivitySchema.model_validate(user) for user in users]
