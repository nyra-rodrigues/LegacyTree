from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    theme = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    message_to_future = Column(Text, nullable=True)
    visibility = Column(String(50), default="Public")
    audio_path = Column(String(500), nullable=True)
    image_path = Column(String(500), nullable=True)
    illustration_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 