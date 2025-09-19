import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "textsentiment")

# Ollama Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"

# Upload Directory (legacy - still used by main.py)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)