# FloodFlow

FloodFlow is an urban flood forecasting, live simulation, and flood-aware emergency route planning platform. It integrates geospatial datasets, digital elevation models (DEM), runoff hydrology models, drainage network graphs, and machine learning corrections to deliver real-time flood depth predictions, road inundation risk assessments, and safe routing for citizens and municipal emergency operators.

---

## Architecture Overview

```
FloodFlow/
├── backend/                  # FastAPI application, database models, ML models, and API routers
│   ├── app/
│   │   ├── api/              # Endpoints (auth, flood, reports, routes, simulator, admin)
│   │   ├── model/            # Hydrology, surface flow, drainage graph & ML correction models
│   │   ├── models/           # SQLAlchemy ORM database models
│   │   ├── services/         # Authentication and OSRM routing services
│   │   ├── config.py         # Pydantic settings and environment management
│   │   ├── database.py       # Engine and session creation (SQLite fallback or PostgreSQL/PostGIS)
│   │   └── main.py           # FastAPI application entry point and middleware
│   └── requirements.txt      # Backend runtime dependencies
├── data/
│   └── flood_project_data/   # Seed/pilot GIS layers, DEM, rainfall scenarios, and OSM roads
├── docs/                     # Data dictionary, architecture, and source documentation
├── frontend/                 # React + TypeScript + Vite dashboard & map interface
│   ├── src/                  # Pages (LiveMap, Forecast, SafeRoutes, Reports, Admin, Operations)
│   ├── public/               # Static map assets and road geometry
│   ├── package.json          # Frontend dependencies
│   └── vercel.json           # SPA rewrite configuration
├── scripts/                  # Data prep, validation, ML training, and schema utilities
├── tests/                    # Unit and integration test suites
├── DEPLOYMENT.md             # Render (backend) and Vercel (frontend) deployment guide
├── render.yaml               # Render blueprint configuration
└── .env.example              # Environment variables template
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- **Python**: 3.11 or 3.12 recommended
- **Node.js**: 18+ or 20+
- **pnpm**: `npm install -g pnpm` (recommended for frontend)

---

### 2. Backend Setup

1. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to configure your database connection string and credentials. By default, it falls back to a local SQLite database for development.*

4. **Prepare and validate data**:
   ```bash
   python scripts/validate_data.py
   python scripts/prepare_data.py
   ```

5. **Initialize database schema and seed demo administrator**:
   ```bash
   python scripts/create_schema.py
   python scripts/create_demo_operator.py
   ```

6. **Start the FastAPI backend server**:
   ```bash
   python scripts/run_api.py
   # Or using uvicorn directly:
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   API docs will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
   Health check endpoint: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 3. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend packages**:
   ```bash
   pnpm install
   ```

3. **Configure frontend environment**:
   ```bash
   cp .env.example .env
   ```
   *Ensure `VITE_API_BASE_URL` points to `http://127.0.0.1:8000/api`.*

4. **Start the Vite development server**:
   ```bash
   pnpm dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running Tests

Run the backend test suite with `pytest`:
```bash
pytest
```

---

## Machine Learning & Demos

FloodFlow includes offline scripts for model training, synthetic simulations, and OSRM network alignment:
```bash
# Train or test the XGBoost risk correction model:
python scripts/train_stage3b_demo.py

# Run standalone hybrid forecast simulation demo:
python scripts/run_hybrid_demo.py

# Align local road layers to OpenStreetMap:
python scripts/align_roads_to_osm.py
```

---

## Deployment

FloodFlow is architected to deploy across two cloud services:
- **Backend API & Simulator**: Render web service using [render.yaml](render.yaml) or a standard container runtime.
- **Frontend SPA**: Vercel using [frontend/vercel.json](frontend/vercel.json).
- **Database**: Neon Serverless PostgreSQL with PostGIS extension enabled.

For detailed, step-by-step production deployment instructions, refer to [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Security Notes

- **Never commit `.env` or any file containing real API keys, passwords, or connection strings.**
- Ensure `.gitignore` is preserved before running `git add .`.
- For production deployments, manage secrets strictly inside the hosting provider's dashboard (e.g., Render Environment Variables / Vercel Project Settings).
