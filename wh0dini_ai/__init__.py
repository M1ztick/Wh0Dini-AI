"""
Wh0Dini-AI: A GPT-powered FastAPI chatbot with a privacy-first, white-box architecture.

This package provides a complete FastAPI-based chatbot solution using OpenAI's GPT models
with focus on privacy, transparency, and user data protection.
"""

__version__ = "1.0.0"
__author__ = "M1ztick"
__email__ = ""
__license__ = "MIT"
__description__ = "A GPT-powered FastAPI chatbot with a privacy-first, white-box architecture"

# Import main components for easier access
from .app import app
from .main import main

__all__ = ["app", "main", "__version__"]