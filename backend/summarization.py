from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class SummarizationService:
    def __init__(self, use_ai_model=True):
        # Use a much smaller, faster model for summarization
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        self.use_ai_model = use_ai_model
        
        if use_ai_model:
            try:
                self.summarizer = pipeline(
                    "summarization", 
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
                print(f"✅ Summarization model loaded: {self.model_name}")
            except Exception as e:
                print(f"❌ Error loading summarization model: {e}")
                print("🔄 Falling back to lightweight mode")
                self.summarizer = None
                self.use_ai_model = False
        else:
            self.summarizer = None
            print("🔄 Running in lightweight mode (no AI model)")
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Summarize text using AI
        """
        if not self.summarizer:
            return self._fallback_summarize(text)
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # If text is too short, return as is
            if len(cleaned_text.split()) < 20:
                return cleaned_text
            
            # Generate summary
            summary = self.summarizer(
                cleaned_text, 
                max_length=max_length, 
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            print(f"Summarization error: {e}")
            return self._fallback_summarize(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for summarization"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit text length (models have input limits)
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text
    
    def _fallback_summarize(self, text: str) -> str:
        """Fallback summarization when AI model fails"""
        words = text.split()
        if len(words) > 50:
            return ' '.join(words[:50]) + "..."
        return text
    
    def generate_title(self, text: str) -> str:
        """Generate a title based on the story content"""
        # Simple keyword-based title generation
        text_lower = text.lower()
        
        # Check for family members
        if any(word in text_lower for word in ["grandfather", "grandpa", "grandad"]):
            return "Memories of Grandfather"
        elif any(word in text_lower for word in ["grandmother", "grandma", "nana"]):
            return "Memories of Grandmother"
        elif any(word in text_lower for word in ["father", "dad", "papa"]):
            return "Memories of Father"
        elif any(word in text_lower for word in ["mother", "mom", "mama"]):
            return "Memories of Mother"
        
        # Check for themes
        elif "war" in text_lower:
            return "War Time Memories"
        elif any(word in text_lower for word in ["migration", "immigration", "journey"]):
            return "The Great Journey"
        elif "love" in text_lower:
            return "A Love Story"
        elif "wedding" in text_lower:
            return "Wedding Day Memories"
        elif "birth" in text_lower or "born" in text_lower:
            return "Birth Story"
        elif "school" in text_lower or "education" in text_lower:
            return "School Days"
        elif "work" in text_lower or "job" in text_lower:
            return "Working Life"
        
        return "A Special Memory"
    
    def classify_theme(self, text: str) -> str:
        """Classify the theme of the story"""
        text_lower = text.lower()
        
        # Define theme keywords
        themes = {
            "love": ["love", "romance", "marriage", "wedding", "kiss", "heart"],
            "war": ["war", "battle", "soldier", "military", "army", "conflict"],
            "migration": ["migration", "immigration", "journey", "travel", "move", "country"],
            "family": ["family", "children", "parents", "grandparents", "home"],
            "tradition": ["tradition", "culture", "custom", "ceremony", "ritual"],
            "adventure": ["adventure", "explore", "discover", "travel", "journey"],
            "struggle": ["struggle", "difficult", "hard", "challenge", "overcome"],
            "success": ["success", "achieve", "accomplish", "win", "victory"]
        }
        
        # Count theme matches
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            theme_scores[theme] = score
        
        # Return the theme with highest score, default to family
        if theme_scores:
            best_theme = max(theme_scores, key=theme_scores.get)
            if theme_scores[best_theme] > 0:
                return best_theme
        
        return "family" 