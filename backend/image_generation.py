from diffusers import DiffusionPipeline
import torch
from PIL import Image
import io
import base64
import os
from typing import Optional

class ImageGenerationService:
    def __init__(self, use_gpu=True):
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.pipeline = None
        self.model_loaded = False
        
    def load_model(self):
        """Load the Stable Diffusion XL model"""
        try:
            print("🔄 Loading Stable Diffusion XL model...")
            
            if self.use_gpu:
                
                self.pipeline = DiffusionPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16"
                )
                self.pipeline.to("cuda")

                if torch.__version__ < "2.0":
                    self.pipeline.enable_xformers_memory_efficient_attention()
            else:
                # CPU version
                self.pipeline = DiffusionPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=torch.float32,
                    use_safetensors=True
                )
                self.pipeline.enable_model_cpu_offload()
            
            self.model_loaded = True
            print("✅ Stable Diffusion XL model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading Stable Diffusion XL model: {e}")
            self.model_loaded = False
    
    def generate_story_illustration(self, story_text: str, style: str = "realistic") -> Optional[str]:
        """
        Generate an illustration based on story content
        Returns base64 encoded image or None if failed
        """
        if not self.model_loaded:
            print("⚠️ Model not loaded, attempting to load now...")
            self.load_model()
            if not self.model_loaded:
                return None
        
        try:
            # Create a prompt based on the story content
            prompt = self._create_prompt_from_story(story_text, style)
            
            print(f"🎨 Generating illustration with prompt: {prompt}")
            
            # Generate the image
            image = self.pipeline(
                prompt=prompt,
                num_inference_steps=20,  # Reduced for faster generation
                guidance_scale=7.5,
                width=512,
                height=512
            ).images[0]
            
            # Convert to base64 for storage/transmission
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            print("✅ Illustration generated successfully!")
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"❌ Error generating illustration: {e}")
            return None
    
    def _create_prompt_from_story(self, story_text: str, style: str = "realistic") -> str:
        """
        Create an effective prompt from story content
        """
        # Extract key elements from the story
        story_lower = story_text.lower()
        
        # Define style modifiers
        style_modifiers = {
            "realistic": "photorealistic, detailed, high quality",
            "artistic": "artistic, painterly, beautiful composition",
            "vintage": "vintage, nostalgic, sepia tones",
            "modern": "modern, clean, minimalist",
            "fantasy": "fantastical, magical, dreamlike"
        }
        
        style_desc = style_modifiers.get(style, "realistic, detailed")
        
        # Extract themes and subjects
        themes = []
        if any(word in story_lower for word in ["war", "soldier", "military"]):
            themes.append("historical, wartime scene")
        if any(word in story_lower for word in ["love", "romance", "marriage"]):
            themes.append("romantic, emotional scene")
        if any(word in story_lower for word in ["family", "grandfather", "grandmother"]):
            themes.append("family, generational scene")
        if any(word in story_lower for word in ["migration", "journey", "travel"]):
            themes.append("journey, travel scene")
        if any(word in story_lower for word in ["school", "education"]):
            themes.append("educational, learning scene")
        if any(word in story_lower for word in ["work", "job", "career"]):
            themes.append("professional, working scene")
        
        # Create the prompt
        if themes:
            theme_desc = ", ".join(themes)
            prompt = f"A {style_desc} illustration depicting {theme_desc}. {story_text[:100]}..."
        else:
            prompt = f"A {style_desc} illustration depicting a meaningful life moment. {story_text[:100]}..."
        
        # Add quality modifiers
        prompt += ", high quality, detailed, emotional, meaningful"
        
        return prompt
    
    def is_available(self) -> bool:
        """Check if image generation is available"""
        return self.model_loaded 