import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

def test_create_user(client: TestClient):
    response = client.post("/api/v1/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

# Convert this to a fixture instead of a regular function
@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    # Create a user directly instead of calling test_create_user
    response = client.post("/api/v1/auth/signup", json={"email": "test@example.com", "password": "password123"})
    # If user already exists, this will fail but we'll still try to log in
    
    # Get the auth token
    response = client.post("/api/v1/auth/login", data={"username": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Now use the fixture instead of calling get_auth_token
def test_create_regulation(client: TestClient, db_session: Session, auth_headers: dict):
    regulation_data = {"nama_peraturan": "Test Peraturan", "judul": "Judul Test", "tahun": "2025"}
    response = client.post("/api/v1/regulations/", json=regulation_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nama_peraturan"] == "Test Peraturan"
    assert "regulation_id" in data

def test_read_regulations_unauthenticated(client: TestClient):
    response = client.get("/api/v1/regulations/")
    assert response.status_code == 200

def test_read_single_regulation(client: TestClient, auth_headers: dict):
    """Test reading a single regulation"""
    # First create a regulation
    regulation_data = {"nama_peraturan": "Peraturan Test", "judul": "Judul Test Read Single", "tahun": "2023"}
    create_response = client.post("/api/v1/regulations/", json=regulation_data, headers=auth_headers)
    regulation_id = create_response.json()["regulation_id"]
    
    # Now read it
    response = client.get(f"/api/v1/regulations/{regulation_id}")
    assert response.status_code == 200
    assert response.json()["nama_peraturan"] == "Peraturan Test"
    assert response.json()["regulation_id"] == regulation_id

def test_read_nonexistent_regulation(client: TestClient):
    """Test reading a regulation that doesn't exist"""
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/regulations/{random_id}")
    assert response.status_code == 404

def test_update_regulation(client: TestClient, auth_headers: dict):
    """Test updating a regulation"""
    # First create a regulation
    regulation_data = {"nama_peraturan": "Peraturan Update", "judul": "Judul Before Update", "tahun": "2022"}
    create_response = client.post("/api/v1/regulations/", json=regulation_data, headers=auth_headers)
    regulation_id = create_response.json()["regulation_id"]
    
    # Now update it
    update_data = {"judul": "Judul After Update", "status": "Updated"}
    response = client.put(
        f"/api/v1/regulations/{regulation_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["judul"] == "Judul After Update"
    assert response.json()["status"] == "Updated"
    # Original data should be preserved
    assert response.json()["nama_peraturan"] == "Peraturan Update"

def test_update_regulation_unauthenticated(client: TestClient):
    """Test updating a regulation without authentication"""
    random_id = str(uuid.uuid4())
    response = client.put(
        f"/api/v1/regulations/{random_id}",
        json={"judul": "Unauthorized Update"}
    )
    assert response.status_code == 401

def test_delete_regulation(client: TestClient, auth_headers: dict):
    """Test deleting a regulation"""
    # First create a regulation
    regulation_data = {"nama_peraturan": "Peraturan Delete", "judul": "Judul For Delete", "tahun": "2021"}
    create_response = client.post("/api/v1/regulations/", json=regulation_data, headers=auth_headers)
    regulation_id = create_response.json()["regulation_id"]
    
    # Now delete it
    response = client.delete(
        f"/api/v1/regulations/{regulation_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/regulations/{regulation_id}")
    assert get_response.status_code == 404

def test_delete_regulation_unauthenticated(client: TestClient):
    """Test deleting a regulation without authentication"""
    random_id = str(uuid.uuid4())
    response = client.delete(f"/api/v1/regulations/{random_id}")
    assert response.status_code == 401

def test_pagination(client: TestClient, auth_headers: dict):
    """Test pagination of regulations"""
    # Create multiple regulations
    for i in range(5):
        regulation_data = {
            "nama_peraturan": f"Peraturan {i}", 
            "judul": f"Judul {i}", 
            "tahun": "2020"
        }
        client.post("/api/v1/regulations/", json=regulation_data, headers=auth_headers)
    
    # Test first page (skip=0, limit=2)
    response = client.get("/api/v1/regulations/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test second page (skip=2, limit=2)
    response = client.get("/api/v1/regulations/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2