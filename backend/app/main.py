from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api import admin, auth, flood, reports, routes, simulator
from .config import get_settings
from .database import engine

app = FastAPI(title="FloodFlow API", version="0.1.0", description="Prototype urban flood nowcasting API")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(flood.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.on_event("startup")
def ensure_auth_schema() -> None:
    """Add the prototype profile field without requiring a destructive schema reset."""
    try:
        if engine.dialect.name == "postgresql":
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT"))
                connection.execute(text("ALTER TABLE flood_reports ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED'"))
                connection.execute(text("ALTER TABLE flood_reports ADD COLUMN IF NOT EXISTS admin_note TEXT"))
                connection.execute(text("ALTER TABLE flood_reports ALTER COLUMN photo_url TYPE TEXT"))
    except Exception:
        pass


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "floodflow-api", "data_mode": "synthetic"}


@app.get("/")
def root() -> dict:
    return {
        "service": "FloodFlow API",
        "status": "running",
        "data_mode": "synthetic",
        "docs": "/docs",
        "health": "/health",
    }
