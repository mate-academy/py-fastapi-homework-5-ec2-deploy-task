from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBaseDTO(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UpdateUserActivitySchema(BaseModel):
    user_id: int
    status: str
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None


class UserActivitySchema(UpdateUserActivitySchema):
    email: EmailStr
