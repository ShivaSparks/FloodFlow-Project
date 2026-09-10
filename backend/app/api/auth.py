from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, ProfileUpdate, UserCreate, UserPublic
from ..services.auth_service import (
    SESSION_COOKIE,
    create_session,
    delete_session,
    hash_password,
    set_session_cookie,
    verify_password,
)
from .dependencies import current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)) -> User:
    email = str(payload.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(name=payload.name, email=email, password_hash=hash_password(payload.password), role="PUBLIC")
    db.add(user)
    db.commit()
    db.refresh(user)
    set_session_cookie(response, create_session(db, user))
    return user


@router.post("/login", response_model=UserPublic)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Keep older prototype rows usable while exposing only the two current roles.
    if user.role in {"USER", "OPERATOR", "SUPER_ADMIN"}:
        user.role = "ADMIN" if user.role in {"OPERATOR", "SUPER_ADMIN"} else "PUBLIC"
        db.commit()
    set_session_cookie(response, create_session(db, user))
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> None:
    delete_session(db, request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE)


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(current_user)) -> User:
    return user


@router.patch("/me", response_model=UserPublic)
def update_me(payload: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
    user.name = payload.name.strip()
    user.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(user)
    return user
