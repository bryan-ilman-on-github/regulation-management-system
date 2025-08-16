import pytest
import uuid
from sqlalchemy.orm import Session
from app.repositories import regulation_repository, user_repository
from app.schemas.regulation import RegulationCreate, RegulationUpdate
from app.schemas.user import UserCreate

def test_user_repository_create(db_session: Session):
    """Test creating a user via repository"""
    user_in = UserCreate(email="repo_test@example.com", password="repopassword")
    user = user_repository.create(db_session, obj_in=user_in)
    assert user.email == "repo_test@example.com"
    assert hasattr(user, "hashed_password")
    
    # Verify it's in the database
    saved_user = user_repository.get_by_email(db_session, email="repo_test@example.com")
    assert saved_user is not None
    assert saved_user.email == "repo_test@example.com"

def test_user_repository_get_by_email(db_session: Session):
    """Test getting a user by email"""
    # Create a user first
    user_in = UserCreate(email="get_email@example.com", password="testpassword")
    user_repository.create(db_session, obj_in=user_in)
    
    # Get the user
    user = user_repository.get_by_email(db_session, email="get_email@example.com")
    assert user is not None
    assert user.email == "get_email@example.com"
    
    # Test nonexistent user
    nonexistent = user_repository.get_by_email(db_session, email="nonexistent@example.com")
    assert nonexistent is None

def test_regulation_repository_create(db_session: Session):
    """Test creating a regulation via repository"""
    regulation_in = RegulationCreate(
        nama_peraturan="Repo Regulation",
        judul="Repo Test Judul",
        tahun="2020"
    )
    regulation = regulation_repository.create(db_session, obj_in=regulation_in)
    assert regulation.nama_peraturan == "Repo Regulation"
    assert regulation.judul == "Repo Test Judul"
    assert regulation.tahun == "2020"
    assert hasattr(regulation, "regulation_id")

def test_regulation_repository_get(db_session: Session):
    """Test getting a regulation by ID"""
    # Create a regulation first
    regulation_in = RegulationCreate(
        nama_peraturan="Get Repo Regulation",
        judul="Get Repo Test Judul",
        tahun="2019"
    )
    created = regulation_repository.create(db_session, obj_in=regulation_in)
    
    # Get the regulation
    regulation = regulation_repository.get(db_session, regulation_id=created.regulation_id)
    assert regulation is not None
    assert regulation.nama_peraturan == "Get Repo Regulation"
    
    # Test nonexistent regulation
    nonexistent = regulation_repository.get(db_session, regulation_id=uuid.uuid4())
    assert nonexistent is None