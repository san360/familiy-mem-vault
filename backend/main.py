from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from pathlib import Path

app = FastAPI(
    title="Family Memory Vault API",
    description="API for managing family memories and photos",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MemoryCreate(BaseModel):
    title: str
    description: str
    date: str
    tags: List[str] = []
    location: str = ""

class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None

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
    if data_path.exists():
        with open(data_path, "r") as f:
            return json.load(f)
    return {"memories": []}

def save_memories(data):
    """Save memories to JSON file"""
    data_path = Path("../data/memories.json")
    data_path.parent.mkdir(exist_ok=True)
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)

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
async def get_memories():
    data = load_memories()
    return data

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
    memory_index = next((i for i, m in enumerate(data["memories"]) if m["id"] == memory_id), None)
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
    memory_index = next((i for i, m in enumerate(data["memories"]) if m["id"] == memory_id), None)
    if memory_index is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    deleted_memory = data["memories"].pop(memory_index)
    save_memories(data)
    return {"message": "Memory deleted successfully", "deleted_memory": deleted_memory}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)