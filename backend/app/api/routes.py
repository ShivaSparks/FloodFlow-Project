from fastapi import APIRouter, HTTPException, Query
import httpx

from ..schemas import RouteRequest
from ..services.routing_service import get_safe_route

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/geocode")
async def geocode(q: str = Query(min_length=3, max_length=200)) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "FloodFlowPrototype/0.1"}) as client:
            response = await client.get("https://nominatim.openstreetmap.org/search", params={"q": q, "format": "jsonv2", "addressdetails": 1, "limit": 8, "countrycodes": "in"})
            response.raise_for_status()
            results = response.json()
            seen: set[tuple[str, str]] = set()
            cleaned = []
            for item in results:
                key = (str(item.get("lat", "")), str(item.get("lon", "")))
                if key in seen:
                    continue
                seen.add(key)
                item["result_type"] = item.get("type", "place").replace("_", " ").title()
                cleaned.append(item)
            return cleaned[:5]
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Address search unavailable: {exc}") from exc


@router.post("/safe")
async def safe_route(payload: RouteRequest) -> dict:
    try:
        return await get_safe_route(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Routing provider unavailable: {exc}") from exc
