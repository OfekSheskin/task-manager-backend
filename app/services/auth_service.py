
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.core.security import hash_password, create_access_token, verify_password
from app.schemas.user_schemas import Token, UserCreate


def register_user(db: Session, user: UserCreate) -> models.User:#function takes user schema and input checks if its in the database if not it hashes the password and adds the user to the database
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    new_user = models.User(
        username=user.username,
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, user: UserCreate) -> Token: #function takes user schema and input checks if its in the database if not it raises an exception if it is it checks the password creates jwt token and returns it
        result = db.execute(select(models.User).where(models.User.username == user.username))
        existing_user = result.scalars().first()   
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        if not verify_password(user.password, existing_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        token = create_access_token(existing_user.user_id)
        return Token(access_token=token, token_type="bearer")