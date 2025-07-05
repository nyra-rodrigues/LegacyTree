from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch
from typing import List
import os

# Import our modules
from database import get_db, engine
from models import Base, Story
from schemas import StoryCreate, StoryUpdate, Story as StorySchema, ConversationRequest
from geocoding import GeocodingService
from summarization import SummarizationService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LegacyTree API", description="API for family story preservation")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load BlenderBot model and tokenizer at startup
MODEL_NAME = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(MODEL_NAME)
model = BlenderbotForConditionalGeneration.from_pretrained(MODEL_NAME)

# Initialize geocoding service
geocoding_service = GeocodingService()

# Initialize summarization service
summarization_service = SummarizationService(use_ai_model=True)  # Enable AI model

def build_conversation_input(history: List[str]):
    # BlenderBot expects the conversation as a single string, with each turn separated by </s>
    return " </s> ".join(history)

# Story Management Endpoints
@app.post("/api/stories", response_model=StorySchema)
def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    """Create a new story"""
    # Get coordinates for the location
    lat, lon = geocoding_service.get_coordinates(story.location)
    
    db_story = Story(
        title=story.title,
        summary=story.summary,
        theme=story.theme,
        location=story.location,
        lat=lat,
        lon=lon,
        date=story.date,
        message_to_future=story.message_to_future,
        visibility=story.visibility,
        illustration_url=story.illustration_url
    )
    
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@app.get("/api/stories", response_model=List[StorySchema])
def get_stories(db: Session = Depends(get_db), visibility: str = None):
    """Get all stories, optionally filtered by visibility"""
    query = db.query(Story)
    if visibility:
        query = query.filter(Story.visibility == visibility)
    return query.all()

@app.get("/api/stories/{story_id}", response_model=StorySchema)
def get_story(story_id: int, db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@app.put("/api/stories/{story_id}", response_model=StorySchema)
def update_story(story_id: int, story_update: StoryUpdate, db: Session = Depends(get_db)):
    """Update a story"""
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Update fields that are provided
    update_data = story_update.dict(exclude_unset=True)
    
    # If location is being updated, get new coordinates
    if "location" in update_data:
        lat, lon = geocoding_service.get_coordinates(update_data["location"])
        update_data["lat"] = lat
        update_data["lon"] = lon
    
    for field, value in update_data.items():
        setattr(db_story, field, value)
    
    db.commit()
    db.refresh(db_story)
    return db_story

@app.delete("/api/stories/{story_id}")
def delete_story(story_id: int, db: Session = Depends(get_db)):
    """Delete a story"""
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(db_story)
    db.commit()
    return {"message": "Story deleted successfully"}

# Geocoding endpoint
@app.get("/api/geocode/{location}")
def geocode_location(location: str):
    """Get coordinates for a location"""
    location_info = geocoding_service.get_location_info(location)
    return location_info

# AI Story Processing endpoint
@app.post("/api/process-story")
def process_story(request: dict):
    """Process story text with AI to generate summary, title, and theme"""
    text = request.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        # Generate AI summary
        summary = summarization_service.summarize_text(text)
        
        # Generate title
        title = summarization_service.generate_title(text)
        
        # Classify theme
        theme = summarization_service.classify_theme(text)
        
        return {
            "summary": summary,
            "title": title,
            "theme": theme,
            "original_length": len(text),
            "summary_length": len(summary)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

# Existing conversation endpoint
@app.post("/api/conversation")
def converse(req: ConversationRequest):
    """Chat with AI using BlenderBot"""
    # Build input from history
    input_text = build_conversation_input(req.history)
    inputs = tokenizer([input_text], return_tensors="pt")
    reply_ids = model.generate(**inputs, max_length=128)
    output = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return {"response": output} 

@app.get("/")
def read_root():
    return {"message": "Welcome to LegacyTree API", "version": "1.0.0"} 