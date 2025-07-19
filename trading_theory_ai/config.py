import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for AI Trading Theory Development"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model Configuration
    GEMINI_MODEL_1 = "gemini-1.5-flash"  # First debater
    GEMINI_MODEL_2 = "gemini-1.5-pro"    # Second debater
    
    # System Configuration
    MAX_DEBATE_ROUNDS = 5
    DEBATE_TIMEOUT = 300  # seconds
    
    # Output Configuration
    OUTPUT_DIR = Path("output")
    RULES_BOOK_FILE = "Algorithm_and_Rules_Book.md"
    DEBATE_LOGS_DIR = Path("debate_logs")
    
    # Prompt Configuration
    SYSTEM_PROMPT_TEMPLATE = """
    You are an expert AI trading strategist participating in a collaborative debate to develop sophisticated trading theories and frameworks.
    
    Your role: {role}
    Topic: {topic}
    
    Guidelines:
    1. Focus purely on theoretical frameworks - no implementation or live trading
    2. Challenge assumptions and propose innovative approaches
    3. Build upon previous arguments while introducing new perspectives
    4. Maintain academic rigor and cite theoretical foundations
    5. Document all insights for the Algorithm & Rules Book
    
    Previous discussion context: {context}
    """
    
    def __init__(self):
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Create output directories
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.DEBATE_LOGS_DIR.mkdir(exist_ok=True)