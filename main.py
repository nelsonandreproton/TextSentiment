from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import aiofiles
import uuid
from pathlib import Path
import logging
from typing import Optional, List
import shutil

from config.settings import MAX_FILE_SIZE_MB, UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.services.image_processor import ImageProcessor
from app.services.mongodb_database import MongoDatabase
from app.services.embedding_service import EmbeddingService
from app.services.bible_service import BibleService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
image_processor = ImageProcessor()
database = MongoDatabase()
embedding_service = EmbeddingService()
bible_service = BibleService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    try:
        await database.connect()
        model_available = await embedding_service.check_model_availability()
        if not model_available:
            logger.error("Embedding model not available. Please run: ollama pull nomic-embed-text")
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

    yield

    # Shutdown
    database.close()
    logger.info("Application shutdown completed")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Busca Bíblica Semântica",
    description="Sistema de busca semântica para textos bíblicos com citações automáticas",
    lifespan=lifespan
)

# Create necessary directories
UPLOAD_DIR.mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="templates")

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Sanitize filename to prevent path traversal
    filename = Path(file.filename).name
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    if file.size and file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )

    # Additional content type validation
    if file.content_type and not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file content type")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with upload form and search."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/records", response_class=HTMLResponse)
async def records_page(request: Request):
    """Records list page."""
    return templates.TemplateResponse("records.html", {"request": request})

@app.get("/records/{record_id}", response_class=HTMLResponse)
async def record_detail_page(request: Request, record_id: int):
    """Individual record detail page."""
    return templates.TemplateResponse("record_detail.html", {"request": request, "record_id": record_id})

@app.post("/add-record")
async def add_record(
    title: str = Form(..., description="Record title", max_length=500),
    content: str = Form(..., description="Record content", max_length=10000)
):
    """Add a new record manually."""
    try:
        # Validate inputs
        title = title.strip()
        content = content.strip()

        if not title:
            raise HTTPException(status_code=400, detail="Título não pode estar vazio")
        if not content:
            raise HTTPException(status_code=400, detail="Conteúdo não pode estar vazio")

        # Check if title already exists
        existing_record = await database.check_title_exists(title)
        if existing_record:
            return JSONResponse({
                "success": False,
                "message": "Título duplicado detectado",
                "duplicate_detected": True,
                "existing_record": {
                    "id": existing_record["id"],
                    "title": existing_record["title"],
                    "created_at": existing_record["created_at"].isoformat() if existing_record["created_at"] else None
                },
                "title": title,
                "content": content[:200] + "..." if len(content) > 200 else content
            })

        # Generate embedding for the content
        embedding = await embedding_service.generate_embedding(content)
        if embedding is None:
            raise HTTPException(status_code=500, detail="Failed to generate embedding")

        # Save to database (no filename since it's manual input)
        record_id = await database.insert_record(
            title=title,
            text=content,
            embedding=embedding,
            filename=None
        )

        return JSONResponse({
            "success": True,
            "message": "Registro adicionado com sucesso",
            "record_id": record_id,
            "title": title,
            "content": content
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add record failed: {e}")
        raise HTTPException(status_code=500, detail="Falha ao adicionar registro")

@app.post("/search")
async def search_similar_texts(
    query: str = Form(..., description="Citação bíblica (ex: 'Lucas 2,15') ou texto para buscar", max_length=5000)
):
    """Buscar textos similares à citação bíblica ou texto fornecido."""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Consulta de busca não pode estar vazia")

        query = query.strip()
        search_text = query
        citation_info = None

        # Check if the query is a Bible citation
        if bible_service.is_bible_citation(query):
            logger.info(f"Detected Bible citation: {query}")

            # Get the actual Bible verse text
            bible_verse = await bible_service.get_verse_by_citation(query)
            if bible_verse:
                search_text = bible_verse.text
                citation_info = {
                    "citation": bible_verse.citation,
                    "text": bible_verse.text,
                    "detected": True
                }
                logger.info(f"Bible verse found: {bible_verse.citation} - {bible_verse.text[:100]}...")
            else:
                logger.warning(f"Bible citation not found: {query}")
                return JSONResponse({
                    "success": False,
                    "error": f"Citação bíblica '{query}' não encontrada. Verifique o formato (ex: 'Lucas 2,15')",
                    "query": query
                })

        # Generate embedding for the search text (either original query or Bible verse text)
        query_embedding = await embedding_service.generate_embedding(search_text)
        if query_embedding is None:
            raise HTTPException(status_code=500, detail="Falha ao gerar embedding para consulta de busca")

        # Search for similar texts
        results = await database.search_similar(query_embedding, limit=10)

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result["id"],
                "title": result["title"],
                "similarity_score": round(result["similarity_score"], 4),
                "preview": result["extracted_text"][:150] + "..." if len(result["extracted_text"]) > 150 else result["extracted_text"],
                "image_filename": result["image_filename"],
                "created_at": result["created_at"].isoformat() if result["created_at"] else None
            })

        return JSONResponse({
            "success": True,
            "query": query,
            "search_text": search_text,
            "bible_citation": citation_info,
            "results": formatted_results,
            "count": len(formatted_results)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Busca falhou")

@app.get("/api/records")
async def get_all_records():
    """Obter todos os registros de texto armazenados."""
    try:
        records = await database.get_all_records()

        formatted_records = []
        for record in records:
            formatted_records.append({
                "id": record["id"],
                "title": record["title"],
                "preview": record["extracted_text"][:100] + "..." if len(record["extracted_text"]) > 100 else record["extracted_text"],
                "image_filename": record["image_filename"],
                "created_at": record["created_at"].isoformat() if record["created_at"] else None
            })

        return JSONResponse({
            "success": True,
            "records": formatted_records,
            "count": len(formatted_records)
        })

    except Exception as e:
        logger.error(f"Failed to get records: {e}")
        raise HTTPException(status_code=500, detail="Falha ao recuperar registros")

@app.get("/api/records/{record_id}")
async def get_record_detail(record_id: str):
    """Obter informações detalhadas de um registro específico."""
    try:
        # Get the specific record from database using MongoDB ObjectId
        record = await database.get_record_by_id(record_id)

        if not record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

        return JSONResponse({
            "success": True,
            "record": {
                "id": record["id"],
                "title": record["title"],
                "extracted_text": record["extracted_text"],
                "image_filename": record["image_filename"],
                "created_at": record["created_at"].isoformat() if record["created_at"] else None,
                "word_count": record["word_count"],
                "character_count": record["character_count"]
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Falha ao recuperar registro")

@app.put("/records/{record_id}")
async def update_record(record_id: str, request: Request):
    """Atualizar um registro de texto."""
    try:
        # Get JSON data from request
        data = await request.json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title:
            raise HTTPException(status_code=400, detail="Título não pode estar vazio")
        if not content:
            raise HTTPException(status_code=400, detail="Conteúdo não pode estar vazio")

        # Check if the record exists
        existing_record = await database.get_record_by_id(record_id)
        if not existing_record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

        # Check if title already exists (but allow same record to keep same title)
        title_exists = await database.check_title_exists(title)
        if title_exists and title_exists["id"] != record_id:
            return JSONResponse({
                "success": False,
                "message": "Título duplicado detectado",
                "duplicate_detected": True,
                "existing_record": {
                    "id": title_exists["id"],
                    "title": title_exists["title"],
                    "created_at": title_exists["created_at"].isoformat() if title_exists["created_at"] else None
                }
            })

        # Generate new embedding for updated content
        embedding = await embedding_service.generate_embedding(content)
        if embedding is None:
            raise HTTPException(status_code=500, detail="Falha ao gerar embedding")

        # Update the record
        success = await database.update_record(record_id, title, content, embedding)
        if success:
            return JSONResponse({"success": True, "message": "Registro atualizado com sucesso"})
        else:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Falha ao atualizar registro")

@app.delete("/records/{record_id}")
async def delete_record(record_id: str):
    """Excluir um registro de texto."""
    try:
        success = await database.delete_record(record_id)
        if success:
            return JSONResponse({"success": True, "message": "Registro excluído com sucesso"})
        else:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Falha ao excluir registro")

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    try:
        model_available = await embedding_service.check_model_availability()
        return {
            "status": "healthy",
            "embedding_model_available": model_available,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)