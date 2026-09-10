"""Create the Stage 2 schema on the configured database.

This command is intentionally separate from data seeding. It can use the local
SQLite fallback for a smoke test, but spatial queries require Neon/PostGIS.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.database import Base, engine
from backend.app.models import *  # noqa: F401,F403


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop", action="store_true", help="drop all tables first; use only for local development")
    args = parser.parse_args()
    if args.drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(f"Created {len(Base.metadata.tables)} tables using configured database.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
