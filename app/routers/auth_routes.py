from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user_schemas import Token, UserCreate, UserResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def registeruser(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return register_user(db, user)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def loginuser(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return login_user(db, user)
