from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
import tempfile
import logging
import sys
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/familiy-mem-vault/backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("family-memory-vault")

app = FastAPI(
    title="Family Memory Vault API",
    description="API for managing family memories and photos",
    version="1.0.0"
)

# Configure CORS
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5175",
    "https://solid-robot-5pgrgw5jv7c4wwr-8000.app.github.dev",
    "https://solid-robot-5pgrgw5jv7c4wwr-5173.app.github.dev",
    "https://solid-robot-5pgrgw5jv7c4wwr-5175.app.github.dev"
]

logger.info(f"Configuring CORS with allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "no-origin")

    logger.info(
        f"REQUEST: {request.method} {request.url} from {client_host} (Origin: {origin})")

    response = await call_next(request)

    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"RESPONSE: {request.method} {request.url} -> {response.status_code} ({process_time:.3f}s)")

    return response

# Pydantic models


class MemoryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200,
                       description="Memory title")
    description: str = Field(..., min_length=1,
                             max_length=2000, description="Memory description")
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$',
                      description="Date in YYYY-MM-DD format")
    tags: List[str] = Field(default=[], description="List of tags")
    location: str = Field(default="", max_length=200,
                          description="Memory location")


class MemoryUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Memory title"
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=2000, description="Memory description"
    )
    date: Optional[str] = Field(
        None, pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="Date in YYYY-MM-DD format"
    )
    tags: Optional[List[str]] = Field(
        None, description="List of tags"
    )
    location: Optional[str] = Field(
        None, max_length=200, description="Memory location"
    )


class Memory(BaseModel):
    id: int
    title: str
    description: str
    date: str
    photos: List[str] = []
    tags: List[str] = []
    location: str = ""


def load_memories():
    """Load memories from JSON file"""
    data_path = Path(__file__).parent.parent / "data" / "memories.json"
    logger.info(f"Loading memories from: {data_path}")

    if not data_path.exists():
        logger.warning(f"Memories file does not exist at {data_path}")
        return {"memories": []}

    try:
        with open(data_path, "r") as f:
            data = json.load(f)
            # Validate structure
            if not isinstance(data, dict) or "memories" not in data:
                logger.error(
                    "Invalid JSON structure: missing 'memories' key or not a dict")
                return {"memories": []}
            if not isinstance(data["memories"], list):
                logger.error(
                    "Invalid JSON structure: 'memories' is not a list")
                return {"memories": []}

            memory_count = len(data["memories"])
            logger.info(f"Successfully loaded {memory_count} memories")
            return data
    except (json.JSONDecodeError, IOError) as e:
        # Handle malformed JSON or read errors by returning empty structure
        logger.error(f"Error loading memories: {e}")
        return {"memories": []}


def save_memories(data):
    """Save memories to JSON file with atomic write operation"""
    data_path = Path(__file__).parent.parent / "data" / "memories.json"
    data_path.parent.mkdir(exist_ok=True)

    logger.info(f"Saving {len(data['memories'])} memories to {data_path}")

    # Write to temporary file first, then atomically move to target
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=data_path.parent,
        delete=False,
        suffix='.tmp'
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2)
        tmp_file.flush()
        os.fsync(tmp_file.fileno())  # Ensure data is written to disk
        temp_path = tmp_file.name

    # Atomically move temp file to target location
    os.replace(temp_path, data_path)
    logger.info(f"Successfully saved memories to {data_path}")


def get_next_id(memories):
    """Get next available ID"""
    if not memories:
        return 1
    return max(memory["id"] for memory in memories) + 1


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Family Memory Vault API", "status": "running"}


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "family-memory-vault-api"}


@app.get("/api/memories")
async def get_memories(
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    location: Optional[str] = Query(
        None, description="Filter by location keyword"),
    date_from: Optional[str] = Query(
        None, description="Filter by start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(
        None, description="Filter by end date (YYYY-MM-DD)")
):
    logger.info(
        f"GET /api/memories called with filters - tags: {tags}, location: {location}, date_from: {date_from}, date_to: {date_to}")

    data = load_memories()
    memories = data["memories"]
    original_count = len(memories)

    # Apply filters
    if tags:
        memories = [m for m in memories if any(
            tag in m.get("tags", []) for tag in tags)]
        logger.info(f"Applied tags filter, {len(memories)} memories remain")

    if location:
        memories = [m for m in memories if location.lower()
                    in m.get("location", "").lower()]
        logger.info(
            f"Applied location filter, {len(memories)} memories remain")

    if date_from:
        try:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            memories = [m for m in memories if datetime.strptime(
                m["date"], "%Y-%m-%d").date() >= from_date]
            logger.info(
                f"Applied date_from filter, {len(memories)} memories remain")
        except ValueError:
            logger.error(f"Invalid date_from format: {date_from}")
            raise HTTPException(
                status_code=400,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )

    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            memories = [m for m in memories if datetime.strptime(
                m["date"], "%Y-%m-%d").date() <= to_date]
            logger.info(
                f"Applied date_to filter, {len(memories)} memories remain")
        except ValueError:
            logger.error(f"Invalid date_to format: {date_to}")
            raise HTTPException(
                status_code=400,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )

    logger.info(
        f"Returning {len(memories)} memories (original: {original_count})")
    return {"memories": memories}


@app.get("/api/memories/{memory_id}")
async def get_memory(memory_id: int):
    logger.info(f"GET /api/memories/{memory_id} called")
    data = load_memories()
    memory = next((m for m in data["memories"] if m["id"] == memory_id), None)
    if not memory:
        logger.warning(f"Memory with id {memory_id} not found")
        raise HTTPException(status_code=404, detail="Memory not found")
    logger.info(f"Successfully retrieved memory with id {memory_id}")
    return memory


@app.post("/api/memories")
async def create_memory(memory: MemoryCreate):
    logger.info(f"POST /api/memories called with title: {memory.title}")
    data = load_memories()
    new_memory = {
        "id": get_next_id(data["memories"]),
        "title": memory.title,
        "description": memory.description,
        "date": memory.date,
        "photos": [],
        "tags": memory.tags,
        "location": memory.location
    }
    data["memories"].append(new_memory)
    save_memories(data)
    logger.info(
        f"Successfully created memory with id {new_memory['id']}: {memory.title}")
    return new_memory


@app.put("/api/memories/{memory_id}")
async def update_memory(memory_id: int, memory_update: MemoryUpdate):
    logger.info(f"PUT /api/memories/{memory_id} called")
    data = load_memories()
    memory_index = next((i for i, m in enumerate(
        data["memories"]) if m["id"] == memory_id), None)
    if memory_index is None:
        logger.warning(f"Memory with id {memory_id} not found for update")
        raise HTTPException(status_code=404, detail="Memory not found")

    # Update only provided fields
    memory = data["memories"][memory_index]
    updated_fields = []
    if memory_update.title is not None:
        memory["title"] = memory_update.title
        updated_fields.append("title")
    if memory_update.description is not None:
        memory["description"] = memory_update.description
        updated_fields.append("description")
    if memory_update.date is not None:
        memory["date"] = memory_update.date
        updated_fields.append("date")
    if memory_update.tags is not None:
        memory["tags"] = memory_update.tags
        updated_fields.append("tags")
    if memory_update.location is not None:
        memory["location"] = memory_update.location
        updated_fields.append("location")

    save_memories(data)
    logger.info(
        f"Successfully updated memory {memory_id}, fields: {updated_fields}")
    return memory


@app.delete("/api/memories/{memory_id}")
async def delete_memory(memory_id: int):
    logger.info(f"DELETE /api/memories/{memory_id} called")
    data = load_memories()
    memory_index = next((i for i, m in enumerate(
        data["memories"]) if m["id"] == memory_id), None)
    if memory_index is None:
        logger.warning(f"Memory with id {memory_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Memory not found")

    deleted_memory = data["memories"].pop(memory_index)
    save_memories(data)
    logger.info(
        f"Successfully deleted memory {memory_id}: {deleted_memory['title']}")
    return {
        "message": "Memory deleted successfully",
        "deleted_memory": deleted_memory
    }


@app.on_event("startup")
async def startup_event():
    logger.info("=== Family Memory Vault API Starting ===")
    logger.info(f"Application version: 1.0.0")
    logger.info(f"CORS origins configured: {cors_origins}")

    # Test loading memories on startup
    data = load_memories()
    logger.info(f"Startup check: {len(data['memories'])} memories available")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== Family Memory Vault API Shutting Down ===")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on host=0.0.0.0, port={port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
