# FloodFlow database migrations

Stage 2 uses Alembic for schema versioning.

Before applying migrations to Neon:

1. Copy the Neon connection string into .env as DATABASE_URL.
2. Enable PostGIS with CREATE EXTENSION IF NOT EXISTS postgis;.
3. Run the migration command documented in the backend setup guide.

The source data is seeded separately and is never used to generate migrations.
