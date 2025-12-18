"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Council members - list of OpenRouter model identifiers
# Can be overridden via COUNCIL_MODELS env var (comma-separated)
_env_council = os.getenv("COUNCIL_MODELS")
if _env_council:
    COUNCIL_MODELS = [m.strip() for m in _env_council.split(",") if m.strip()]
else:
    COUNCIL_MODELS = [
        "openai/gpt-5.1",
        "google/gemini-3-pro-preview",
        "anthropic/claude-sonnet-4.5",
        "x-ai/grok-4.1-fast",
    ]

# Chairman model - synthesizes final response
# Can be overridden via CHAIRMAN_MODEL env var
CHAIRMAN_MODEL = os.getenv("CHAIRMAN_MODEL", "openai/gpt-5.1")

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# File upload configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp", "image/gif"]
SUPPORTED_FILE_TYPES = ["application/pdf", "text/plain"]
