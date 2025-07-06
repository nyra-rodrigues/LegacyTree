from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch
from typing import List
import os
import base64

# Import our modules
from database import get_db, engine
from models import Base, Story
from schemas import StoryCreate, StoryUpdate, Story as StorySchema, ConversationRequest
from geocoding import GeocodingService
from summarization import SummarizationService

# Optional import for image generation
try:
    from image_generation import ImageGenerationService
    IMAGE_GENERATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Image generation not available: {e}")
    IMAGE_GENERATION_AVAILABLE = False

# Optional import for speech services


try:
    from speech_service import SpeechService
    SPEECH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Speech services not available: {e}")
    SPEECH_AVAILABLE = False

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

# Initialize image generation service (lazy loading)
if IMAGE_GENERATION_AVAILABLE:
    image_generation_service = ImageGenerationService(use_gpu=False)  # Start with CPU for compatibility
else:
    image_generation_service = None

# Initialize speech service (lazy loading)
if SPEECH_AVAILABLE:
    speech_service = SpeechService()
    # Pre-load the Whisper model to avoid delays
    speech_service.load_whisper_model()
else:
    speech_service = None

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

# AI Illustration Generation endpoint
@app.post("/api/generate-illustration")
def generate_illustration(request: dict):
    """Generate an AI illustration based on story content"""
    if not IMAGE_GENERATION_AVAILABLE or image_generation_service is None:
        raise HTTPException(status_code=503, detail="Image generation service not available")
    
    story_text = request.get("text", "")
    style = request.get("style", "realistic")
    
    if not story_text:
        raise HTTPException(status_code=400, detail="Story text is required")
    
    try:
        # Generate the illustration
        illustration_data = image_generation_service.generate_story_illustration(story_text, style)
        
        if illustration_data:
            return {
                "success": True,
                "illustration_url": illustration_data,
                "style": style
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate illustration")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Illustration generation error: {str(e)}")

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

@app.get("/api/health")
def health_check():
    """Check the health and availability of all services"""
    return {
        "status": "healthy",
        "services": {
            "speech": {
                "available": SPEECH_AVAILABLE,
                "initialized": speech_service is not None,
                "model_loaded": speech_service.is_available() if speech_service else False
            },
            "image_generation": {
                "available": IMAGE_GENERATION_AVAILABLE,
                "initialized": image_generation_service is not None
            },
            "summarization": {
                "available": True,
                "model_loaded": summarization_service.summarizer is not None
            },
            "geocoding": {
                "available": True
            }
        }
    }

# Speech-to-Text endpoint
@app.post("/api/speech-to-text")
def convert_speech_to_text(request: dict):
    """Convert speech audio to text"""
    if not SPEECH_AVAILABLE or speech_service is None:
        raise HTTPException(status_code=503, detail="Speech service not available")
    
    audio_data = request.get("audio_data")
    language = request.get("language", "en")
    
    if not audio_data:
        raise HTTPException(status_code=400, detail="Audio data is required")
    
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)
        
        # Convert speech to text
        text = speech_service.speech_to_text(audio_bytes, language)
        
        if text:
            return {"success": True, "text": text}
        else:
            raise HTTPException(status_code=500, detail="Failed to transcribe speech")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-text error: {str(e)}")

# Text-to-Speech endpoint
@app.post("/api/text-to-speech")
def convert_text_to_speech(request: dict):
    """Convert text to speech"""
    if not SPEECH_AVAILABLE or speech_service is None:
        raise HTTPException(status_code=503, detail="Speech service not available")
    
    text = request.get("text", "")
    language = request.get("language", "en")
    slow = request.get("slow", False)
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        # Convert text to speech
        audio_url = speech_service.text_to_speech(text, language, slow)
        
        if audio_url:
            return {"success": True, "audio_url": audio_url}
        else:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-speech error: {str(e)}")

# Get supported languages endpoint
@app.get("/api/speech/languages")
def get_supported_languages():
    """Get list of supported languages for speech services"""
    if not SPEECH_AVAILABLE:
        raise HTTPException(status_code=503, detail="Speech service not available - module not imported")
    
    if speech_service is None:
        raise HTTPException(status_code=503, detail="Speech service not available - service not initialized")
    
    try:
        languages = speech_service.get_supported_languages()
        return languages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting languages: {str(e)}") 