from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..services.auth_service import get_user_from_token


def current_user(
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias="floodflow_session"),
) -> User:
    user = get_user_from_token(db, session_token)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    if user.role in {"USER", "OPERATOR", "SUPER_ADMIN"}:
        user.role = "ADMIN" if user.role in {"OPERATOR", "SUPER_ADMIN"} else "PUBLIC"
        db.commit()
    return user


def require_operator(user: User = Depends(current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrative access required")
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
