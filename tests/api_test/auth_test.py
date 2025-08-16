from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

def test_user_signup_success(client: TestClient):
    """Test successful user signup"""
    response = client.post(
        "/api/v1/auth/signup", 
        json={"email": "new_user@example.com", "password": "strongpassword123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new_user@example.com"
    assert "id" in response.json()

def test_user_signup_duplicate_email(client: TestClient):
    """Test signup with duplicate email"""
    # Create first user
    client.post(
        "/api/v1/auth/signup", 
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    
    # Try to create another user with same email
    response = client.post(
        "/api/v1/auth/signup", 
        json={"email": "duplicate@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success(client: TestClient):
    """Test successful login"""
    # Create a user first
    client.post(
        "/api/v1/auth/signup", 
        json={"email": "login_test@example.com", "password": "password123"}
    )
    
    # Login with created user
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login_test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    # Create a user first
    client.post(
        "/api/v1/auth/signup", 
        json={"email": "invalid_login@example.com", "password": "correctpassword"}
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "invalid_login@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_me_authenticated(client: TestClient):
    """Test getting user profile when authenticated"""
    # Create a user
    client.post(
        "/api/v1/auth/signup", 
        json={"email": "me_test@example.com", "password": "password123"}
    )
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "me_test@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get user profile with token
    response = client.get(
        "/api/v1/auth/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me_test@example.com"

def test_get_me_unauthenticated(client: TestClient):
    """Test getting user profile without authentication"""
    response = client.get("/api/v1/auth/users/me")
    assert response.status_code == 401