# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()