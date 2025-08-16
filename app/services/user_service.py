from ..core.security import verify_password
from ..repositories import user_repository as repo
from ..schemas.user import UserCreate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def authenticate_user(db: Session, email: str, password: str):
    user = repo.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_user(db: Session, user_in: UserCreate):
    user = repo.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )
    return repo.create(db, obj_in=user_in)
