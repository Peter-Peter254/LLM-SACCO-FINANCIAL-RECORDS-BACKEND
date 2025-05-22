from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    username: str
    password: str
    userType: int

class UserResponse(BaseModel):
    id: UUID
    username: str
    userType:int
    created_at: datetime

    class Config:
        orm_mode = True


