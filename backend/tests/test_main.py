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

def test_filter_memories_by_tags():
    # Create test memories with different tags
    memories = [
        {
            "title": "Family Vacation",
            "description": "Trip to the beach",
            "date": "2024-06-15",
            "tags": ["family", "vacation", "beach"],
            "location": "Beach Resort"
        },
        {
            "title": "Birthday Party",
            "description": "John's birthday",
            "date": "2024-07-20",
            "tags": ["birthday", "celebration"],
            "location": "Home"
        },
        {
            "title": "Work Conference",
            "description": "Annual work meeting",
            "date": "2024-08-10",
            "tags": ["work", "conference"],
            "location": "Office"
        }
    ]
    
    # Create the memories
    for memory in memories:
        client.post("/api/memories", json=memory)
    
    # Test filtering by single tag
    response = client.get("/api/memories?tags=family")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    assert len([m for m in filtered_memories if "family" in m.get("tags", [])]) > 0
    
    # Test filtering by multiple tags (OR logic)
    response = client.get("/api/memories?tags=birthday&tags=vacation")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    assert len([m for m in filtered_memories if any(tag in m.get("tags", []) for tag in ["birthday", "vacation"])]) > 0

def test_filter_memories_by_location():
    # Test location filtering (case-insensitive substring search)
    response = client.get("/api/memories?location=home")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    for memory in filtered_memories:
        assert "home" in memory.get("location", "").lower()
    
    # Test location filtering with partial match
    response = client.get("/api/memories?location=Beach")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    for memory in filtered_memories:
        assert "beach" in memory.get("location", "").lower()

def test_filter_memories_by_date_range():
    # Test date filtering
    response = client.get("/api/memories?date_from=2024-07-01")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    for memory in filtered_memories:
        assert memory["date"] >= "2024-07-01"
    
    # Test date range filtering
    response = client.get("/api/memories?date_from=2024-06-01&date_to=2024-07-31")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    for memory in filtered_memories:
        assert "2024-06-01" <= memory["date"] <= "2024-07-31"

def test_filter_memories_invalid_date():
    # Test invalid date format
    response = client.get("/api/memories?date_from=invalid-date")
    assert response.status_code == 400
    
    response = client.get("/api/memories?date_to=invalid-date")
    assert response.status_code == 400

def test_filter_memories_combined():
    # Test combining multiple filters
    response = client.get("/api/memories?tags=family&location=beach&date_from=2024-06-01")
    assert response.status_code == 200
    data = response.json()
    filtered_memories = data["memories"]
    for memory in filtered_memories:
        # Should match all criteria
        assert "family" in memory.get("tags", [])
        assert "beach" in memory.get("location", "").lower()
        assert memory["date"] >= "2024-06-01"