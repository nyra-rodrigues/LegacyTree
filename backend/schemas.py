from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StoryBase(BaseModel):
    title: str
    summary: str
    theme: str
    location: str
    lat: float
    lon: float
    date: datetime
    message_to_future: Optional[str] = None
    visibility: str = "Public"
    illustration_url: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    theme: Optional[str] = None
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    date: Optional[datetime] = None
    message_to_future: Optional[str] = None
    visibility: Optional[str] = None
    illustration_url: Optional[str] = None

class Story(StoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationRequest(BaseModel):
    history: list[str] 