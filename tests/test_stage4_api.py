from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stage4_routes_are_registered():
    paths = set(app.openapi()["paths"])
    assert "/api/auth/register" in paths
    assert "/api/flood/prediction" in paths
    assert "/api/reports/flood" in paths
    assert "/api/routes/safe" in paths
    assert "/api/simulator/advance" in paths
    assert "/api/admin/status" in paths
