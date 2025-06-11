from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

def load_memories():
    """Load memories from JSON file"""
    data_path = Path("../data/memories.json")
    if data_path.exists():
        with open(data_path, "r") as f:
            return json.load(f)
    return {"memories": []}

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)