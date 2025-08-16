import pytest
from jose import jwt
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from app.core.config import SECRET_KEY, ALGORITHM

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hashed password should be different from original
    assert hashed != password
    
    # Verification should work
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail verification
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    """Test JWT token creation and validation"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    # Decode the token to verify it contains our data
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload  # Expiration time should be set