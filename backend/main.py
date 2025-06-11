from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
import re

app = FastAPI(
    title="Family Memory Vault API",
    description="API for managing family memories and photos",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        None, min_length=1, max_length=200, description="Memory title")
    description: Optional[str] = Field(
        None, min_length=1, max_length=2000, description="Memory description")
    date: Optional[str] = Field(
        None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date in YYYY-MM-DD format")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    location: Optional[str] = Field(
        None, max_length=200, description="Memory location")


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
    data_path = Path("../data/memories.json")
    if not data_path.exists():
        return {"memories": []}
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
            # Validate structure
            if not isinstance(data, dict) or "memories" not in data:
                return {"memories": []}
            if not isinstance(data["memories"], list):
                return {"memories": []}
            return data
    except (json.JSONDecodeError, IOError):
        # Handle malformed JSON or read errors by returning empty structure
        return {"memories": []}


def save_memories(data):
    """Save memories to JSON file with atomic write operation"""
    data_path = Path("../data/memories.json")
    data_path.parent.mkdir(exist_ok=True)
    
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


def get_next_id(memories):
    """Get next available ID"""
    if not memories:
        return 1
    return max(memory["id"] for memory in memories) + 1


@app.get("/")
async def root():
    return {"message": "Family Memory Vault API", "status": "running"}


@app.get("/health")
async def health_check():
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
    data = load_memories()
    memories = data["memories"]

    # Apply filters
    if tags:
        memories = [m for m in memories if any(
            tag in m.get("tags", []) for tag in tags)]

    if location:
        memories = [m for m in memories if location.lower()
                    in m.get("location", "").lower()]

    if date_from:
        try:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            memories = [m for m in memories if datetime.strptime(
                m["date"], "%Y-%m-%d").date() >= from_date]
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")

    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            memories = [m for m in memories if datetime.strptime(
                m["date"], "%Y-%m-%d").date() <= to_date]
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")

    return {"memories": memories}


@app.get("/api/memories/{memory_id}")
async def get_memory(memory_id: int):
    data = load_memories()
    memory = next((m for m in data["memories"] if m["id"] == memory_id), None)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@app.post("/api/memories")
async def create_memory(memory: MemoryCreate):
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
    return new_memory


@app.put("/api/memories/{memory_id}")
async def update_memory(memory_id: int, memory_update: MemoryUpdate):
    data = load_memories()
    memory_index = next((i for i, m in enumerate(
        data["memories"]) if m["id"] == memory_id), None)
    if memory_index is None:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Update only provided fields
    memory = data["memories"][memory_index]
    if memory_update.title is not None:
        memory["title"] = memory_update.title
    if memory_update.description is not None:
        memory["description"] = memory_update.description
    if memory_update.date is not None:
        memory["date"] = memory_update.date
    if memory_update.tags is not None:
        memory["tags"] = memory_update.tags
    if memory_update.location is not None:
        memory["location"] = memory_update.location

    save_memories(data)
    return memory


@app.delete("/api/memories/{memory_id}")
async def delete_memory(memory_id: int):
    data = load_memories()
    memory_index = next((i for i, m in enumerate(
        data["memories"]) if m["id"] == memory_id), None)
    if memory_index is None:
        raise HTTPException(status_code=404, detail="Memory not found")

    deleted_memory = data["memories"].pop(memory_index)
    save_memories(data)
    return {"message": "Memory deleted successfully", "deleted_memory": deleted_memory}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
