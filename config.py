"""
Configuration settings for Ezrex.AI
"""

import os
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models" / "trained_models"
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = PROJECT_ROOT / "database"

# Create directories if they don't exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASE_CONFIG = {
    "path": str(DATABASE_DIR / "ezrex_ai.db"),
    "timeout": 10,
    "check_same_thread": False,
}

# Machine Learning configuration
ML_CONFIG = {
    "device": "cpu",  # Use "cpu" for Termux/mobile, "cuda" if GPU available
    "learning_rate": 0.001,
    "hidden_size": 128,
    "num_layers": 2,
    "dropout": 0.2,
    "batch_size": 16,
    "epochs": 10,
    "vocab_size": 5000,
}

# User preferences configuration
USER_PREFS_CONFIG = {
    "learning_enabled": True,
    "feedback_weight": 0.8,
    "max_history": 1000,
    "auto_save_interval": 50,  # Save every 50 interactions
}

# Model paths
MODELS = {
    "intent_classifier": str(MODELS_DIR / "intent_classifier.pt"),
    "response_generator": str(MODELS_DIR / "response_generator.pt"),
    "code_analyzer": str(MODELS_DIR / "code_analyzer.pt"),
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(PROJECT_ROOT / "logs" / "ezrex_ai.log"),
}

# Create logs directory
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# UI Configuration (Kivy)
UI_CONFIG = {
    "window_width": 400,
    "window_height": 800,
    "theme_color": "#2196F3",
    "font_size": 14,
}

# Data Analysis configuration
DATA_ANALYSIS_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": ["csv", "json", "txt"],
    "chart_types": ["bar", "line", "pie", "scatter"],
}

# Coding Assistant configuration
CODE_HELPER_CONFIG = {
    "supported_languages": ["python", "javascript", "java", "cpp", "c", "sql"],
    "max_code_length": 5000,
    "enable_syntax_check": True,
}
