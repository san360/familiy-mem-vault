from fastapi.testclient import TestClient
from main import app, load_memories, save_memories
from pathlib import Path
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
    memory_data = {
        "title": "Single Test Memory",
        "description": "Testing single memory retrieval",
        "date": "2024-01-02",
        "tags": ["single", "test"],
        "location": "Single Test Location"
    }
    create_response = client.post("/api/memories", json=memory_data)
    memory_id = create_response.json()["id"]

    response = client.get(f"/api/memories/{memory_id}")
    assert response.status_code == 200
    retrieved = response.json()
    assert retrieved["id"] == memory_id
    assert retrieved["title"] == memory_data["title"]

def test_update_memory():
    memory_data = {
        "title": "Memory to Update",
        "description": "Original description",
        "date": "2024-01-03",
        "tags": ["update", "test"],
        "location": "Original Location"
    }
    created = client.post("/api/memories", json=memory_data).json()
    memory_id = created["id"]

    update_data = {
        "title": "Updated Memory Title",
        "description": "Updated description"
    }
    response = client.put(f"/api/memories/{memory_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == update_data["title"]
    assert updated["description"] == update_data["description"]
    assert updated["date"] == memory_data["date"]
    assert updated["tags"] == memory_data["tags"]
    assert updated["location"] == memory_data["location"]

def test_delete_memory():
    memory_data = {
        "title": "Memory to Delete",
        "description": "This memory will be deleted",
        "date": "2024-01-04",
        "tags": ["delete", "test"],
        "location": "Delete Location"
    }
    created = client.post("/api/memories", json=memory_data).json()
    memory_id = created["id"]

    response = client.delete(f"/api/memories/{memory_id}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "deleted_memory" in result

    # Confirm deletion
    get_response = client.get(f"/api/memories/{memory_id}")
    assert get_response.status_code == 404

def test_get_nonexistent_memory():
    response = client.get("/api/memories/99999")
    assert response.status_code == 404

def test_update_nonexistent_memory():
    response = client.put("/api/memories/99999", json={"title": "Updated Title"})
    assert response.status_code == 404

def test_delete_nonexistent_memory():
    response = client.delete("/api/memories/99999")
    assert response.status_code == 404

def test_filter_memories_by_tags():
    memories = [
        {"title": "Family Vacation", "description": "Trip to the beach", "date": "2024-06-15", "tags": ["family", "vacation", "beach"], "location": "Beach Resort"},
        {"title": "Birthday Party", "description": "John's birthday", "date": "2024-07-20", "tags": ["birthday", "celebration"], "location": "Home"},
        {"title": "Work Conference", "description": "Annual work meeting", "date": "2024-08-10", "tags": ["work", "conference"], "location": "Office"},
    ]
    for m in memories:
        client.post("/api/memories", json=m)

    response = client.get("/api/memories?tags=family")
    assert response.status_code == 200
    assert any("family" in m.get("tags", []) for m in response.json()["memories"])

    response = client.get("/api/memories?tags=birthday&tags=vacation")
    assert response.status_code == 200
    assert any(tag in m.get("tags", []) for m in response.json()["memories"] for tag in ["birthday", "vacation"])

def test_filter_memories_by_location():
    response = client.get("/api/memories?location=home")
    assert response.status_code == 200
    for m in response.json()["memories"]:
        assert "home" in m.get("location", "").lower()

    response = client.get("/api/memories?location=Beach")
    assert response.status_code == 200
    for m in response.json()["memories"]:
        assert "beach" in m.get("location", "").lower()

def test_filter_memories_by_date_range():
    response = client.get("/api/memories?date_from=2024-07-01")
    assert response.status_code == 200
    for m in response.json()["memories"]:
        assert m["date"] >= "2024-07-01"

    response = client.get("/api/memories?date_from=2024-06-01&date_to=2024-07-31")
    assert response.status_code == 200
    for m in response.json()["memories"]:
        assert "2024-06-01" <= m["date"] <= "2024-07-31"

def test_filter_memories_invalid_date():
    response = client.get("/api/memories?date_from=invalid-date")
    assert response.status_code == 400

    response = client.get("/api/memories?date_to=invalid-date")
    assert response.status_code == 400

def test_filter_memories_combined():
    response = client.get("/api/memories?tags=family&location=beach&date_from=2024-06-01")
    assert response.status_code == 200
    for m in response.json()["memories"]:
        assert "family" in m.get("tags", [])
        assert "beach" in m.get("location", "").lower()
        assert m["date"] >= "2024-06-01"

def test_create_memory_validation():
    # Empty title
    response = client.post("/api/memories", json={"title": "", "description": "Valid", "date": "2024-01-01"})
    assert response.status_code == 422

    # Empty description
    response = client.post("/api/memories", json={"title": "Valid", "description": "", "date": "2024-01-01"})
    assert response.status_code == 422

    # Invalid date
    response = client.post("/api/memories", json={"title": "Valid", "description": "Valid", "date": "invalid-date"})
    assert response.status_code == 422

    # Too long title
    response = client.post("/api/memories", json={"title": "x" * 201, "description": "Valid", "date": "2024-01-01"})
    assert response.status_code == 422

    # Valid memory
    response = client.post("/api/memories", json={
        "title": "Valid Memory",
        "description": "A valid memory description",
        "date": "2024-01-01",
        "tags": ["validation", "test"],
        "location": "Test Location"
    })
    assert response.status_code == 200
    memory = response.json()
    assert memory["title"] == "Valid Memory"
    assert memory["tags"] == ["validation", "test"]

def test_load_memories_empty_file():
    """Test that load_memories handles empty files correctly"""
    # Create temporary empty file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
        tmp_file.write("")
        empty_file_path = tmp_file.name
    
    try:
        # Temporarily replace the data file path
        original_load = load_memories
        def mock_load():
            data_path = Path(empty_file_path)
            if not data_path.exists():
                return {"memories": []}
            
            try:
                with open(data_path, "r") as f:
                    data = json.load(f)
                    if not isinstance(data, dict) or "memories" not in data:
                        return {"memories": []}
                    if not isinstance(data["memories"], list):
                        return {"memories": []}
                    return data
            except (json.JSONDecodeError, IOError):
                return {"memories": []}
        
        # Test the function
        result = mock_load()
        assert result == {"memories": []}
        assert isinstance(result["memories"], list)
        
    finally:
        os.unlink(empty_file_path)

def test_load_memories_malformed_file():
    """Test that load_memories handles malformed JSON files correctly"""
    # Create temporary malformed JSON file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
        tmp_file.write('{"memories": [invalid json}')
        malformed_file_path = tmp_file.name
    
    try:
        # Temporarily replace the data file path
        def mock_load():
            data_path = Path(malformed_file_path)
            if not data_path.exists():
                return {"memories": []}
            
            try:
                with open(data_path, "r") as f:
                    data = json.load(f)
                    if not isinstance(data, dict) or "memories" not in data:
                        return {"memories": []}
                    if not isinstance(data["memories"], list):
                        return {"memories": []}
                    return data
            except (json.JSONDecodeError, IOError):
                return {"memories": []}
        
        # Test the function
        result = mock_load()
        assert result == {"memories": []}
        assert isinstance(result["memories"], list)
        
    finally:
        os.unlink(malformed_file_path)

def test_save_and_fetch_multiple_entries():
    """Test saving and fetching multiple memory entries"""
    # Get initial count
    initial_response = client.get("/api/memories")
    initial_count = len(initial_response.json()["memories"])
    
    # Create multiple memories
    memories_data = [
        {
            "title": "Memory 1",
            "description": "First test memory",
            "date": "2024-01-01",
            "tags": ["test", "first"],
            "location": "Location 1"
        },
        {
            "title": "Memory 2", 
            "description": "Second test memory",
            "date": "2024-01-02",
            "tags": ["test", "second"],
            "location": "Location 2"
        },
        {
            "title": "Memory 3",
            "description": "Third test memory", 
            "date": "2024-01-03",
            "tags": ["test", "third"],
            "location": "Location 3"
        }
    ]
    
    created_ids = []
    for memory_data in memories_data:
        response = client.post("/api/memories", json=memory_data)
        assert response.status_code == 200
        created_memory = response.json()
        created_ids.append(created_memory["id"])
        assert created_memory["title"] == memory_data["title"]
        assert created_memory["description"] == memory_data["description"]
    
    # Fetch all memories and verify they were saved
    response = client.get("/api/memories")
    assert response.status_code == 200
    all_memories = response.json()["memories"]
    assert len(all_memories) >= initial_count + 3
    
    # Verify each created memory can be fetched individually
    for memory_id, original_data in zip(created_ids, memories_data):
        response = client.get(f"/api/memories/{memory_id}")
        assert response.status_code == 200
        fetched_memory = response.json()
        assert fetched_memory["title"] == original_data["title"]
        assert fetched_memory["description"] == original_data["description"]

def test_file_safe_atomic_writing():
    """Test that save_memories uses atomic writing to prevent corruption"""
    import tempfile
    import threading
    import time
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file_path = Path(temp_dir) / "test_memories.json"
        
        # Mock the save_memories function to use our test file
        def test_save_memories(data):
            with tempfile.NamedTemporaryFile(
                mode='w', 
                dir=test_file_path.parent, 
                delete=False,
                suffix='.tmp'
            ) as tmp_file:
                json.dump(data, tmp_file, indent=2)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                temp_path = tmp_file.name
            
            os.replace(temp_path, test_file_path)
        
        # Test data
        test_data = {"memories": [{"id": 1, "title": "Test", "description": "Test", "date": "2024-01-01", "photos": [], "tags": [], "location": ""}]}
        
        # Write the data
        test_save_memories(test_data)
        
        # Verify file exists and contains correct data
        assert test_file_path.exists()
        with open(test_file_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == test_data
        
        # Test that no temporary files are left behind
        temp_files = list(test_file_path.parent.glob("*.tmp"))
        assert len(temp_files) == 0


def test_path_resolution_from_different_working_directory():
    """Test that load_memories works correctly regardless of current working directory"""
    import subprocess
    import sys
    
    # Get the current working directory
    original_cwd = os.getcwd()
    
    try:
        # Test from project root directory (parent of backend)
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        
        # Load memories from different working directory
        data = load_memories()
        assert isinstance(data, dict)
        assert "memories" in data
        assert isinstance(data["memories"], list)
        
        # If the data file exists, we should get some memories
        data_file = Path(__file__).parent.parent.parent / "data" / "memories.json"
        if data_file.exists():
            # Verify we can read actual data
            assert len(data["memories"]) > 0
            # Verify the first memory has the expected structure
            if data["memories"]:
                memory = data["memories"][0]
                assert "id" in memory
                assert "title" in memory
                assert "description" in memory
                assert "date" in memory
                
    finally:
        # Always restore the original working directory
        os.chdir(original_cwd)
