from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from ..repositories import regulation_repository as repo
from ..core.redis_client import get_cache, set_cache, delete_cache
from ..schemas.regulation import Regulation, RegulationCreate, RegulationUpdate

def get_regulation(db: Session, regulation_id: UUID):
    cache_key = f"regulation:{regulation_id}"

    # Try to get from cache
    cached_regulation = get_cache(cache_key)
    if cached_regulation:
        return cached_regulation

    # If miss, get from DB
    db_regulation = repo.get(db, regulation_id=regulation_id)
    if not db_regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")

    # Set cache for next time
    # Use the Pydantic model to serialize the SQLAlchemy object properly
    regulation_data = Regulation.model_validate(db_regulation, from_attributes=True).model_dump()
    set_cache(cache_key, regulation_data)

    return regulation_data

def get_all_regulations(db: Session, skip: int, limit: int):
    return repo.get_multi(db, skip=skip, limit=limit)

def create_regulation(db: Session, regulation: RegulationCreate):
    return repo.create(db, obj_in=regulation)

def update_regulation(db: Session, regulation_id: UUID, regulation_in: RegulationUpdate):
    db_regulation = repo.get(db, regulation_id=regulation_id)
    if not db_regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")

    updated_regulation = repo.update(db, db_obj=db_regulation, obj_in=regulation_in)

    # Invalidate cache
    cache_key = f"regulation:{regulation_id}"
    delete_cache(cache_key)

    return updated_regulation

def delete_regulation(db: Session, regulation_id: UUID):
    db_regulation = repo.remove(db, id=regulation_id)
    if not db_regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")

    # Invalidate cache
    cache_key = f"regulation:{regulation_id}"
    delete_cache(cache_key)

    return db_regulation