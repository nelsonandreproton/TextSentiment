import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "textsentiment")

# Other Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
EMBEDDING_MODEL = "nomic-embed-text"

UPLOAD_DIR.mkdir(exist_ok=True)