from app.schemas.regulation import RegulationCreate, RegulationUpdate
from app.schemas.user import UserCreate
from app.services import regulation_service, user_service
from fastapi import HTTPException
from sqlalchemy.orm import Session
import pytest
import uuid


def test_user_create_success(db_session: Session):
    """Test creating a user successfully"""
    user_in = UserCreate(email="service_test@example.com", password="testpassword")
    user = user_service.create_user(db_session, user_in)
    assert user.email == "service_test@example.com"
    assert hasattr(user, "hashed_password")
    assert user.hashed_password != "testpassword"  # Password should be hashed


def test_user_create_duplicate(db_session: Session):
    """Test creating a user with duplicate email"""
    user_in = UserCreate(email="duplicate_service@example.com", password="testpassword")
    user_service.create_user(db_session, user_in)

    # Try to create the same user again
    with pytest.raises(HTTPException) as excinfo:
        user_service.create_user(db_session, user_in)
    assert excinfo.value.status_code == 400
    assert "already exists" in excinfo.value.detail


def test_authenticate_user_success(db_session: Session):
    """Test successful user authentication"""
    # Create a user
    user_in = UserCreate(email="auth_service@example.com", password="correctpassword")
    user_service.create_user(db_session, user_in)

    # Authenticate with correct credentials
    authenticated_user = user_service.authenticate_user(
        db_session, email="auth_service@example.com", password="correctpassword"
    )
    assert authenticated_user is not False
    assert authenticated_user.email == "auth_service@example.com"


def test_authenticate_user_wrong_password(db_session: Session):
    """Test failed authentication with wrong password"""
    # Create a user
    user_in = UserCreate(email="wrong_pass@example.com", password="correctpassword")
    user_service.create_user(db_session, user_in)

    # Try to authenticate with wrong password
    result = user_service.authenticate_user(
        db_session, email="wrong_pass@example.com", password="wrongpassword"
    )
    assert result is False


def test_authenticate_user_nonexistent(db_session: Session):
    """Test authentication with nonexistent user"""
    result = user_service.authenticate_user(
        db_session, email="nonexistent@example.com", password="anypassword"
    )
    assert result is False
