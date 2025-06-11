from fastapi.testclient import TestClient
from main import app

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