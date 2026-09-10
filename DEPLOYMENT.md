# FloodFlow deployment

FloodFlow uses two services. Vercel hosts the React frontend; the FastAPI simulator and API must run as a persistent web service such as Render.

## Backend first

1. Push this repository to GitHub.
2. In Render, create a Blueprint from the repository. `render.yaml` configures the API service.
3. Add the existing Neon connection string as `DATABASE_URL`.
4. Set `CORS_ORIGINS` to the final Vercel URL, for example `https://floodflow.vercel.app`.
5. Deploy and verify `https://YOUR-API.onrender.com/health`.

The API start command keeps the simulator, authentication, reports, forecast endpoints, and routing service together in one process.

## Frontend

1. Create a Vercel project from the same repository.
2. Set the project root to `frontend`.
3. Set `VITE_API_BASE_URL` to `https://YOUR-API.onrender.com/api`.
4. Deploy. `frontend/vercel.json` keeps direct routes such as `/forecast`, `/routes`, and `/reports` working after refresh.

## Important

Do not set `VITE_API_BASE_URL` to localhost in Vercel. Do not put `DATABASE_URL` in Vercel; it belongs only in the backend service. After the Vercel domain is known, add that exact HTTPS origin to the backend `CORS_ORIGINS` value and redeploy the backend.
