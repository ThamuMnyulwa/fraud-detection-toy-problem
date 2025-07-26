"""
Configuration settings for the Agentic Coupon Abuse Detection System.
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Google ADK Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GENAI_USE_VERTEXAI = (
    os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE"
)

# Model Configuration
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash")

# Application Settings
DEBUG = os.getenv("DEBUG", "FALSE").upper() == "TRUE"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Performance Settings
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 8192))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))
TOP_P = float(os.getenv("TOP_P", 0.95))
TOP_K = int(os.getenv("TOP_K", 40))

# Security Settings
SAFETY_SETTINGS = os.getenv("SAFETY_SETTINGS", "HIGH")

# Fraud Detection Rules
FRAUD_RULES = {
    "identity_reuse": {
        "patterns": [
            "same_phone_multiple_accounts",
            "same_user_name_multiple_accounts",
        ],
        "weight": 0.85,
        "threshold": 2,
    },
    "vendor_check": {
        "patterns": [
            "fraudulent_vendor_name",
        ],
        "weight": 0.90,
        "threshold": 1,
    },
    "base_abuse": {
        "patterns": [
            "high_discount_ratio",
        ],
        "weight": 0.75,
        "threshold": 1,
    },
}

# Fraudulent vendor names
FRAUDULENT_VENDORS = ["FakeShop", "ScamStore", "FraudMart"]

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("fraud_detection")
