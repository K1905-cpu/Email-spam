"""
Vercel Serverless Entrypoint for Email Spam Detection API
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Handler for Vercel
app_handler = app
