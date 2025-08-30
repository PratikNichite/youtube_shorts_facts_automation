"""
Configuration module for YouTube Pipeline
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the pipeline"""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    # Script Configuration
    SIMILARITY_THRESHOLD = 0.7
    MAX_RETRIES = 3
    MAX_TOKENS = 1000
    TEMPERATURE = 0.8
    
    # Available topics for random selection
    AVAILABLE_TOPICS = [
        "Space and Astronomy",
        "Ocean and Marine Life", 
        "Human Body",
        "Ancient History",
        "Technology",
        "Animals",
        "Food and Nutrition",
        "Psychology",
        "Geography",
        "Science Discoveries",
        "Art and Culture",
        "Sports",
        "Music",
        "Weather and Climate",
        "Inventions",
        "Amazing Nature Facts",
        "Mind-Blowing Physics",
        "Historical Mysteries",
        "Future Technology",
        "Bizarre World Records"
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your .env file or environment variables."
            )
        return True