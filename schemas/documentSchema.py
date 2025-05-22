from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    name: str
    year: int
    description: Optional[str] = None
    file_url: str

class DocumentResponse(BaseModel):
    id: str
    name: str
    year: int
    description: Optional[str]
    file_url: str
    status: int
    created_at: datetime

    class Config:
        orm_mode = True
