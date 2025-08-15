from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from ..repositories import regulation_repository as repo
from ..schemas.regulation import RegulationCreate, RegulationUpdate

def get_regulation(db: Session, regulation_id: UUID):
    db_regulation = repo.get(db, regulation_id=regulation_id)
    if not db_regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")
    return db_regulation

def get_all_regulations(db: Session, skip: int, limit: int):
    return repo.get_multi(db, skip=skip, limit=limit)

def create_regulation(db: Session, regulation: RegulationCreate):
    return repo.create(db, obj_in=regulation)

def update_regulation(db: Session, regulation_id: UUID, regulation_in: RegulationUpdate):
    db_regulation = get_regulation(db, regulation_id) # Reuse getter to check existence
    return repo.update(db, db_obj=db_regulation, obj_in=regulation_in)

def delete_regulation(db: Session, regulation_id: UUID):
    db_regulation = repo.remove(db, id=regulation_id)
    if not db_regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")
    return db_regulation