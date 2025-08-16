from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# This import needs to happen before the app is imported
# to ensure mocks are in place.
from app.core.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def mock_redis(monkeypatch):
    """
    Mocks all Redis cache functions to prevent actual Redis connections during tests.
    This fixture runs automatically for every test.
    """

    # This fake function will be used to replace set_cache, delete_cache, etc.
    def no_op(*args, **kwargs):
        pass

    # This fake function simulates a cache miss every time.
    def mock_get_cache(*args, **kwargs):
        return None

    # We patch the functions where they are IMPORTED and USED, not where they are defined.
    monkeypatch.setattr("app.services.regulation_service.get_cache", mock_get_cache)
    monkeypatch.setattr("app.services.regulation_service.set_cache", no_op)
    monkeypatch.setattr("app.services.regulation_service.delete_cache", no_op)
    # If you added mget/mset, mock them as well
    # monkeypatch.setattr("app.services.regulation_service.mget_cache", lambda keys: [None] * len(keys))
    # monkeypatch.setattr("app.services.regulation_service.mset_cache", no_op)


# Now it's safe to import the app because the dependencies are mocked
from app.main import app


@pytest.fixture(scope="function")
def db_session():
    """
    Creates a new database session for a test and cleans up after.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session, mock_redis):  # ADDED db_session as a dependency
    """
    Provides a TestClient for making API requests in tests.
    """

    # Dependency override to use the test database
    def override_get_db():
        # The db_session fixture has already created a session,
        # so we can yield it directly here for the API to use.
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
