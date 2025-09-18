#!/usr/bin/env python3
"""
MongoDB setup script for Text Sentiment Extraction application.
This script helps set up the database and check dependencies.
"""

import sys
import subprocess
from pathlib import Path
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required")
        return False
    print(f"[OK] Python version: {sys.version}")
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Tesseract OCR is installed")
            return True
    except FileNotFoundError:
        pass

    print("[ERROR] Tesseract OCR not found")
    print("Please install Tesseract OCR:")
    print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("  Linux: sudo apt-get install tesseract-ocr")
    print("  macOS: brew install tesseract")
    return False

def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'config/requirements.txt'])
        print("[OK] Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install dependencies")
        return False

def check_mongodb():
    """Check if MongoDB is running."""
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv

        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        client.close()
        print("[OK] MongoDB connection successful")
        return True

    except ImportError:
        print("[ERROR] Dependencies not installed. Please run 'pip install -r config/requirements.txt' first")
        return False
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        print("Please ensure MongoDB is installed and running")
        print("Download from: https://www.mongodb.com/try/download/community")
        return False

def setup_mongodb():
    """Set up MongoDB database and collections."""
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv

        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_database = os.getenv("MONGODB_DATABASE", "textsentiment")

        client = MongoClient(mongodb_url)
        db = client[mongodb_database]
        collection = db.text_records

        # Create indexes
        from pymongo import IndexModel, TEXT

        # Text index for title search
        title_index = IndexModel([("title", TEXT)], name="title_text_index")

        # Index for created_at
        date_index = IndexModel([("created_at", -1)], name="created_at_index")

        # Compound index for title uniqueness (case-insensitive)
        title_unique_index = IndexModel([("title_lower", 1)], unique=True, name="title_unique_index")

        # Create indexes (will skip if they already exist)
        collection.create_indexes([title_index, date_index, title_unique_index])

        client.close()
        print("[OK] MongoDB database and indexes created successfully")
        return True

    except ImportError:
        print("[ERROR] Dependencies not installed. Please run 'pip install -r config/requirements.txt' first")
        return False
    except Exception as e:
        print(f"[ERROR] MongoDB setup failed: {e}")
        return False

def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        from dotenv import load_dotenv

        load_dotenv()
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("[OK] Ollama is running")

            # Check if nomic-embed-text model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]

            if any('nomic-embed-text' in name for name in model_names):
                print("[OK] nomic-embed-text model is available")
                return True
            else:
                print("[ERROR] nomic-embed-text model not found")
                print("Please run: ollama pull nomic-embed-text")
                return False
        else:
            print("[ERROR] Ollama is not responding")
            return False
    except ImportError:
        print("[ERROR] Dependencies not installed. Please run 'pip install -r config/requirements.txt' first")
        return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to Ollama: {e}")
        print("Please ensure Ollama is installed and running")
        print("Install from: https://ollama.ai/download")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['uploads', 'logs', 'static/css', 'static/js', 'static/img']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("[OK] Directories created")

def main():
    """Main setup function."""
    print("Setting up Text Sentiment Extraction Application (MongoDB Version)")
    print("=" * 60)

    # Check environment file
    if not Path('.env').exists():
        print("Creating .env file from template...")
        if Path('config/.env.example').exists():
            Path('.env').write_text(Path('config/.env.example').read_text())
            print("[OK] .env file created. Please update MongoDB credentials if needed.")
        else:
            print("[ERROR] config/.env.example not found")
            return False

    success = True

    # Run all checks in order
    success &= check_python_version()
    success &= check_tesseract()

    # Install dependencies first
    deps_installed = install_dependencies()
    success &= deps_installed

    # Only proceed with database/ollama checks if dependencies are installed
    if deps_installed:
        success &= check_mongodb()
        success &= setup_mongodb()
        success &= check_ollama()
    else:
        print("[WARNING] Skipping MongoDB and Ollama checks due to missing dependencies")

    create_directories()

    print("\n" + "=" * 60)
    if success:
        print("Setup completed successfully!")
        print("\nTo start the application:")
        print("  python main.py")
        print("\nOr with uvicorn:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\nAccess the application at: http://localhost:8000")
    else:
        print("Setup completed with errors. Please fix the issues above.")
        return False

    return True

if __name__ == "__main__":
    main()