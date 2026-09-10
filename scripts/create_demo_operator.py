"""Create or promote the prototype operator account in the configured database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from backend.app.config import get_settings
from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.services.auth_service import hash_password

settings = get_settings()
EMAIL = settings.demo_operator_email
PASSWORD = settings.demo_operator_password

with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == EMAIL))
    if user is None:
        user = User(name="FloodFlow Administrator", email=EMAIL, password_hash=hash_password(PASSWORD), role="ADMIN")
        db.add(user)
    else:
        user.password_hash = hash_password(PASSWORD)
        user.role = "ADMIN"
        user.is_active = True
    db.commit()
    print(f"Demo operator ready: {EMAIL} ({user.role})")
