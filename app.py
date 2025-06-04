#!/usr/bin/env python3
"""
Main entry point for GitHub deployments
Import path fix for streamlit_twitter_bot.py
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main streamlit app
from streamlit_twitter_bot import main

if __name__ == "__main__":
    main()
