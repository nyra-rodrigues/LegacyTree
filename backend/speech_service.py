import whisper
import tempfile
import os
from gtts import gTTS
import base64
import io
from typing import Optional, Tuple
import torch

class SpeechService:
    def __init__(self):
        self.whisper_model = None
        self.model_loaded = False
        
    def load_whisper_model(self):
        """Load the Whisper model for speech-to-text"""
        try:
            print("🔄 Loading Whisper model for speech recognition...")
            # Use a smaller model for faster processing
            self.whisper_model = whisper.load_model("base")
            self.model_loaded = True
            print("✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            self.model_loaded = False
    
    def speech_to_text(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """
        Convert speech audio to text using Whisper
        """
        if not self.model_loaded:
            print("⚠️ Whisper model not loaded, attempting to load now...")
            self.load_whisper_model()
            if not self.model_loaded:
                return None
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe audio
            result = self.whisper_model.transcribe(temp_file_path, language=language)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            transcribed_text = result["text"].strip()
            print(f"✅ Speech transcribed: {transcribed_text}")
            return transcribed_text
            
        except Exception as e:
            print(f"❌ Error in speech-to-text: {e}")
            return None
    
    def text_to_speech(self, text: str, language: str = "en", slow: bool = False) -> Optional[str]:
        """
        Convert text to speech using gTTS
        Returns base64 encoded audio data
        """
        try:
            print(f"🔊 Converting text to speech: {text[:50]}...")
            
            # Create TTS audio
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                tts.save(temp_file.name)
                temp_file_path = temp_file.name
            
            # Read the audio file and convert to base64
            with open(temp_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data).decode()
            audio_url = f"data:audio/mp3;base64,{audio_base64}"
            
            print("✅ Text-to-speech conversion completed!")
            return audio_url
            
        except Exception as e:
            print(f"❌ Error in text-to-speech: {e}")
            return None
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages for TTS"""
        return {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "hi": "Hindi",
            "ar": "Arabic"
        }
    
    def is_available(self) -> bool:
        """Check if speech services are available"""
        return self.model_loaded 