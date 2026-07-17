from database import UserModel


class FakeUserActivityRepo:
    """
    Fake UserActivityRepository class for unit testing.
    """

    async def create_user_activity(self, user: UserModel) -> None:
        """
        Fake creation or reset a user's activity record
        """
