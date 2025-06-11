from fastapi.testclient import TestClient
from main import app
import json
import tempfile
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Family Memory Vault API", "status": "running"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "family-memory-vault-api"}

def test_get_memories():
    response = client.get("/api/memories")
    assert response.status_code == 200
    data = response.json()
    assert "memories" in data
    assert isinstance(data["memories"], list)

def test_create_memory():
    memory_data = {
        "title": "Test Memory",
        "description": "This is a test memory",
        "date": "2024-01-01",
        "tags": ["test", "memory"],
        "location": "Test Location"
    }
    response = client.post("/api/memories", json=memory_data)
    assert response.status_code == 200
    created_memory = response.json()
    assert created_memory["title"] == memory_data["title"]
    assert created_memory["description"] == memory_data["description"]
    assert created_memory["date"] == memory_data["date"]
    assert created_memory["tags"] == memory_data["tags"]
    assert created_memory["location"] == memory_data["location"]
    assert "id" in created_memory

def test_get_single_memory():
    # First create a memory
    memory_data = {
        "title": "Single Test Memory",
        "description": "Testing single memory retrieval",
        "date": "2024-01-02",
        "tags": ["single", "test"],
        "location": "Single Test Location"
    }
    create_response = client.post("/api/memories", json=memory_data)
    created_memory = create_response.json()
    memory_id = created_memory["id"]
    
    # Then retrieve it
    response = client.get(f"/api/memories/{memory_id}")
    assert response.status_code == 200
    retrieved_memory = response.json()
    assert retrieved_memory["id"] == memory_id
    assert retrieved_memory["title"] == memory_data["title"]

def test_update_memory():
    # First create a memory
    memory_data = {
        "title": "Memory to Update",
        "description": "Original description",
        "date": "2024-01-03",
        "tags": ["update", "test"],
        "location": "Original Location"
    }
    create_response = client.post("/api/memories", json=memory_data)
    created_memory = create_response.json()
    memory_id = created_memory["id"]
    
    # Then update it
    update_data = {
        "title": "Updated Memory Title",
        "description": "Updated description"
    }
    update_response = client.put(f"/api/memories/{memory_id}", json=update_data)
    assert update_response.status_code == 200
    updated_memory = update_response.json()
    assert updated_memory["title"] == update_data["title"]
    assert updated_memory["description"] == update_data["description"]
    # Other fields should remain unchanged
    assert updated_memory["date"] == memory_data["date"]
    assert updated_memory["tags"] == memory_data["tags"]
    assert updated_memory["location"] == memory_data["location"]

def test_delete_memory():
    # First create a memory
    memory_data = {
        "title": "Memory to Delete",
        "description": "This memory will be deleted",
        "date": "2024-01-04",
        "tags": ["delete", "test"],
        "location": "Delete Location"
    }
    create_response = client.post("/api/memories", json=memory_data)
    created_memory = create_response.json()
    memory_id = created_memory["id"]
    
    # Then delete it
    delete_response = client.delete(f"/api/memories/{memory_id}")
    assert delete_response.status_code == 200
    delete_result = delete_response.json()
    assert "message" in delete_result
    assert "deleted_memory" in delete_result
    
    # Verify it's deleted
    get_response = client.get(f"/api/memories/{memory_id}")
    assert get_response.status_code == 404

def test_get_nonexistent_memory():
    response = client.get("/api/memories/99999")
    assert response.status_code == 404

def test_update_nonexistent_memory():
    update_data = {"title": "Updated Title"}
    response = client.put("/api/memories/99999", json=update_data)
    assert response.status_code == 404

def test_delete_nonexistent_memory():
    response = client.delete("/api/memories/99999")
    assert response.status_code == 404