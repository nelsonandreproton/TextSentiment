# Text Sentiment Extraction Web App

A web application that extracts text from images with specific formatting (red title, black content) and provides semantic search functionality using vector embeddings.

## Features

- **Image Text Extraction**: Upload images and extract text using OCR with color-based filtering
- **Semantic Search**: Search for similar texts using bible verses or any text query
- **Vector Storage**: Uses PostgreSQL with pgvector for efficient similarity search
- **Local AI**: Uses Ollama for generating embeddings (privacy-focused)
- **Image Processing**: Handles different background colors and filters out unwanted text

## Prerequisites

### Required Software
1. **Python 3.8+**
2. **PostgreSQL** with pgvector extension
3. **Tesseract OCR**
4. **Ollama** with `nomic-embed-text` model

### Installation Instructions

#### 1. Tesseract OCR
- **Windows**: Download from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
- **macOS**: `brew install tesseract`

#### 2. PostgreSQL
- **Windows**: Download from [PostgreSQL.org](https://www.postgresql.org/download/)
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`
- **macOS**: `brew install postgresql`

#### 3. Ollama
- Download from [Ollama.ai](https://ollama.ai/download)
- After installation: `ollama pull nomic-embed-text`

## Setup

1. **Clone/Download the project**
   ```bash
   cd TextSentiment
   ```

2. **Install dependencies (recommended first step)**
   ```bash
   python install_deps.py
   ```

3. **Run automated setup**
   ```bash
   python setup.py
   ```

4. **Manual setup (if needed)**
   ```bash
   # Install dependencies manually
   pip install -r config/requirements.txt

   # Set up environment variables
   cp config/.env.example .env
   # Edit .env with your database credentials

   # Create PostgreSQL database
   createdb textsentiment
   ```

4. **Start services**
   ```bash
   # Start PostgreSQL (if not running)
   # Start Ollama (if not running)
   ollama serve
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Image Upload
1. Navigate to `http://localhost:8000`
2. Upload an image with:
   - Red title text at the top
   - Black content text below
   - Various background colors (white, yellow, blue, green)
3. The system will:
   - Extract and separate red (title) and black (content) text
   - Filter out corner numbers and Portuguese musical notes (Re-, Sol-, Do, etc.)
   - Generate vector embeddings for semantic search

### Semantic Search
1. Enter a bible verse or any text in the search box
2. The system returns similar texts ranked by similarity score
3. Results show title, preview, and similarity percentage

### Managing Records
- View all uploaded records
- Delete unwanted records
- See creation timestamps

## Image Processing Details

The application is optimized for images with:
- **Title**: Red, bold text at the top
- **Content**: Black text (bold and regular)
- **Backgrounds**: White, yellow, blue, or green
- **Filtering**: Removes corner numbers and musical notes in Portuguese

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload and process image
- `POST /search` - Search for similar texts
- `GET /records` - Get all records
- `DELETE /records/{id}` - Delete a record
- `GET /health` - Health check

## Configuration

Edit `.env` file:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/textsentiment
OLLAMA_URL=http://localhost:11434
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Ensure Tesseract is in PATH
   - Windows: Add installation directory to system PATH

2. **Database connection failed**
   - Check if PostgreSQL is running
   - Verify database credentials in `.env`
   - Ensure database exists: `createdb textsentiment`

3. **Ollama model not available**
   - Run: `ollama pull nomic-embed-text`
   - Check Ollama service: `ollama serve`

4. **pgvector extension error**
   - Install pgvector: [Installation Guide](https://github.com/pgvector/pgvector#installation)
   - Or use Docker: `docker run --name postgres-vector -e POSTGRES_PASSWORD=password -p 5432:5432 -d pgvector/pgvector:pg15`

### Health Check
Visit `http://localhost:8000/health` to check system status.

## Project Structure

```
TextSentiment/
├── main.py                     # Application entry point
├── setup.py                    # Setup and installation script
├── pyproject.toml              # Modern Python project configuration
├── STRUCTURE.md                # Detailed structure documentation
│
├── app/                        # Main application package
│   ├── services/               # Business logic services
│   │   ├── database.py         # Database operations
│   │   ├── embedding_service.py # Ollama integration
│   │   └── image_processor.py  # Image processing and OCR
│   ├── api/                    # API routes (future expansion)
│   ├── core/                   # Core application logic
│   ├── models/                 # Data models and schemas
│   └── utils/                  # Utility functions
│
├── config/                     # Configuration files
│   ├── settings.py             # Application settings
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment template
│
├── templates/                  # HTML templates
│   ├── index.html             # Main page
│   ├── records.html           # Records list
│   └── record_detail.html     # Record details
│
├── tests/                      # Test modules
├── static/                     # Static web assets
├── uploads/                    # Uploaded images
└── logs/                      # Application logs
```

See [STRUCTURE.md](STRUCTURE.md) for detailed documentation.

## Security Features

- File type validation
- File size limits
- SQL injection prevention using parameterized queries
- Input sanitization
- No sensitive data logging
- Local processing (no data sent to external services)

## Performance Notes

- Vector similarity search is optimized with pgvector indices
- Images are processed locally for privacy
- Background processing for OCR operations
- Configurable similarity search limits

## License

This project uses open-source technologies and is free to use.