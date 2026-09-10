from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import SessionRecord, User
from ..config import get_settings

password_hash = PasswordHash.recommended()
SESSION_COOKIE = "floodflow_session"


def set_session_cookie(response, token: str) -> None:
    secure = get_settings().secure_cookies
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="none" if secure else "lax",
        secure=secure,
        max_age=604800,
    )


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: Session, user: User) -> str:
    raw_token = secrets.token_urlsafe(48)
    db.add(
        SessionRecord(
            user_id=user.id,
            token_hash=_token_hash(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
    )
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return raw_token


def get_user_from_token(db: Session, raw_token: str | None) -> User | None:
    if not raw_token:
        return None
    record = db.scalar(
        select(SessionRecord).where(
            SessionRecord.token_hash == _token_hash(raw_token),
            SessionRecord.expires_at > datetime.now(timezone.utc),
        )
    )
    if record is None:
        return None
    return db.get(User, record.user_id)


def delete_session(db: Session, raw_token: str | None) -> None:
    if not raw_token:
        return
    record = db.scalar(select(SessionRecord).where(SessionRecord.token_hash == _token_hash(raw_token)))
    if record:
        db.delete(record)
        db.commit()
