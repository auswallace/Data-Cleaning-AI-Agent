"""
Configuration management for the AI Data Cleaning Agent
Uses environment variables with sensible defaults
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CLEANED_DIR = DATA_DIR / "cleaned"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOAD_DIR, CLEANED_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys (optional - only needed for AI-enhanced features)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# File Upload Limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".parquet"}

# Data Cleaning Configuration
MISSING_VALUE_THRESHOLD = float(os.getenv("MISSING_VALUE_THRESHOLD", "0.5"))  # Drop columns with >50% missing
OUTLIER_CONTAMINATION = float(os.getenv("OUTLIER_CONTAMINATION", "0.05"))  # Expected outlier percentage
KNN_NEIGHBORS = int(os.getenv("KNN_NEIGHBORS", "5"))

# LLM Configuration
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")  # Cheaper, faster model
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))  # Low temp for consistent results
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

# Agent Configuration
MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "5"))
AGENT_MEMORY_SIZE = int(os.getenv("AGENT_MEMORY_SIZE", "10"))

# Validation
def validate_config():
    """Validate that required configuration is present"""
    issues = []

    if MAX_FILE_SIZE_MB < 1:
        issues.append("MAX_FILE_SIZE_MB must be at least 1")

    if not 0 < MISSING_VALUE_THRESHOLD < 1:
        issues.append("MISSING_VALUE_THRESHOLD must be between 0 and 1")

    if not 0 < OUTLIER_CONTAMINATION < 0.5:
        issues.append("OUTLIER_CONTAMINATION must be between 0 and 0.5")

    return issues

# Run validation on import
config_issues = validate_config()
if config_issues and not DEBUG_MODE:
    raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {issue}" for issue in config_issues))
