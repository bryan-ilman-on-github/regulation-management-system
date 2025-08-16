from ...core.database import get_db
from ...models.user import User
from ...schemas.regulation import Regulation, RegulationCreate, RegulationUpdate
from ...services import regulation_service as service
from ..dependencies import get_current_user
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=Regulation, status_code=201)
def create_regulation(
    regulation_in: RegulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # PROTECTED
):
    return service.create_regulation(db=db, regulation=regulation_in)


@router.get("/", response_model=List[Regulation])
def read_regulations(
    skip: int = 0,
    limit: int = Query(default=100, lte=200),
    db: Session = Depends(get_db),
):
    return service.get_all_regulations(db, skip=skip, limit=limit)


@router.get("/{regulation_id}", response_model=Regulation)
def read_regulation(regulation_id: UUID, db: Session = Depends(get_db)):
    return service.get_regulation(db=db, regulation_id=regulation_id)


@router.put("/{regulation_id}", response_model=Regulation)
def update_regulation(
    regulation_id: UUID,
    regulation_in: RegulationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # PROTECTED
):
    return service.update_regulation(
        db=db, regulation_id=regulation_id, regulation_in=regulation_in
    )


@router.delete("/{regulation_id}", response_model=Regulation)
def delete_regulation(
    regulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # PROTECTED
):
    return service.delete_regulation(db=db, regulation_id=regulation_id)
