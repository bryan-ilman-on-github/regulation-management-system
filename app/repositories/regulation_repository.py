from sqlalchemy.orm import Session
from uuid import UUID
from ..models.regulation import Regulation
from ..schemas.regulation import RegulationCreate, RegulationUpdate

def get(db: Session, regulation_id: UUID) -> Regulation | None:
    return db.query(Regulation).filter(Regulation.regulation_id == regulation_id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[Regulation]:
    return db.query(Regulation).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: RegulationCreate) -> Regulation:
    db_obj = Regulation(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, *, db_obj: Regulation, obj_in: RegulationUpdate) -> Regulation:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, id: UUID) -> Regulation | None:
    obj = db.get(Regulation, id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj