"""
Configuration management for the receipt automation application.
"""
import os
import streamlit as st
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"
RNC_CSV_PATH = DATA_DIR / "RNC_Contribuyentes_Actualizado_30_Ago_2025.csv"

# API Configuration
def get_gemini_api_key():
    """
    Get Gemini API key from Streamlit secrets or environment variable.
    Priority: Streamlit secrets > Environment variable
    """
    try:
        # Try Streamlit secrets first (for deployment)
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variable (for local development)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in .streamlit/secrets.toml "
                "or as an environment variable."
            )
        return api_key

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODEL_LITE = "gemini-2.5-flash-lite"

# Image Processing Configuration
CONTRAST_ENHANCEMENT_FACTOR = 2
BBOX_EXPANSION_FACTOR = 0.05  # 5% expansion for bounding boxes

# Supported file types
SUPPORTED_FILE_TYPES = ["jpg", "jpeg", "pdf"]
