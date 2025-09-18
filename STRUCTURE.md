# Project Structure

This document outlines the organization of the Text Sentiment Extraction project following Python best practices.

## Directory Structure

```
TextSentiment/
├── main.py                     # Application entry point (FastAPI app)
├── setup.py                    # Setup and installation script
├── pyproject.toml              # Modern Python project configuration
├── README.md                   # Project documentation
├── STRUCTURE.md                # This file
├── .env                        # Environment variables (created from template)
├── .gitignore                  # Git ignore rules
│
├── app/                        # Main application package
│   ├── __init__.py
│   ├── api/                    # API routes and endpoints
│   │   └── __init__.py
│   ├── core/                   # Core application logic
│   │   └── __init__.py
│   ├── models/                 # Data models and schemas
│   │   └── __init__.py
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── database.py         # Database operations
│   │   ├── embedding_service.py # Ollama integration
│   │   └── image_processor.py  # Image processing and OCR
│   └── utils/                  # Utility functions
│       └── __init__.py
│
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── settings.py             # Application settings
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment template
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html             # Main upload/search page
│   ├── records.html           # Records list page
│   └── record_detail.html     # Individual record view
│
├── static/                     # Static web assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── img/                   # Images
│
├── tests/                      # Test modules
│   ├── __init__.py
│   ├── test_basic.py          # Basic functionality tests
│   ├── test_integration.py    # Integration tests
│   ├── test_duplicate_detection.py # Duplicate detection tests
│   └── test_api.py            # API endpoint tests
│
├── uploads/                    # Uploaded image files
├── logs/                      # Application logs
└── docs/                      # Additional documentation
```

## Package Organization

### `app/` - Main Application Package
Contains all application code organized by responsibility:

- **`services/`** - Business logic and external service integrations
  - `database.py` - PostgreSQL database operations with pgvector
  - `embedding_service.py` - Ollama API integration for embeddings
  - `image_processor.py` - OCR and image processing logic

- **`api/`** - API routes and endpoint definitions (future expansion)
- **`core/`** - Core application logic and utilities
- **`models/`** - Data models, schemas, and validation
- **`utils/`** - Shared utility functions

### `config/` - Configuration Management
- **`settings.py`** - Application configuration and environment variables
- **`requirements.txt`** - Python package dependencies
- **`.env.example`** - Template for environment variables

### `templates/` - Web Interface
HTML templates using Jinja2 templating engine

### `static/` - Static Assets
Web assets organized by type (CSS, JavaScript, images)

### `tests/` - Test Suite
Comprehensive test coverage including unit, integration, and API tests

## Key Benefits of This Structure

1. **Separation of Concerns** - Each module has a clear responsibility
2. **Scalability** - Easy to add new features and services
3. **Testability** - Clear separation makes testing easier
4. **Maintainability** - Logical organization simplifies maintenance
5. **Python Standards** - Follows PEP 8 and modern Python practices

## Import Conventions

```python
# Standard library imports
import os
import sys

# Third-party imports
from fastapi import FastAPI
import numpy as np

# Local application imports
from config.settings import DATABASE_URL
from app.services.database import Database
from app.services.embedding_service import EmbeddingService
```

## Running the Application

1. **Setup**: `python setup.py`
2. **Development**: `python main.py`
3. **Production**: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Development Tools

The project includes configuration for:
- **Black** - Code formatting
- **isort** - Import sorting
- **MyPy** - Type checking
- **pytest** - Testing framework

Run development tools:
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Run tests
pytest
```