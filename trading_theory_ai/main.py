#!/usr/bin/env python3
"""
AI Trading Theory Development Framework

A collaborative system where AI models debate and develop sophisticated trading theories,
creating a growing Algorithm & Rules Book for future implementation.

Usage:
    python -m trading_theory_ai.main [command] [options]
    
Commands:
    start-debate    Start a new AI debate session
    demo           Run a demonstration debate
    list-frameworks List all theory frameworks
    show-book      Show Algorithm & Rules Book statistics
    
Environment Variables:
    GEMINI_API_KEY  Required - Your Google Gemini API key
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_theory_ai.cli import app

def main():
    """Main entry point for the application"""
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable is required")
        print("\nTo get started:")
        print("1. Get a Gemini API key from: https://ai.google.dev/")
        print("2. Set it as an environment variable:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        print("3. Run the application again")
        sys.exit(1)
    
    # Run the CLI application
    app()

if __name__ == "__main__":
    main()