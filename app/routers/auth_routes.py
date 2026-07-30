from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user_schemas import UserCreate, UserResponse
from app.services.auth_service import register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def registeruser(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return register_user(db, user)


@router.post("/login")
def loginuser():
    return status.HTTP_200_OK
