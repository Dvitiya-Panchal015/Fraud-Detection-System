from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_and_swagger_are_available() -> None:
    with TestClient(app) as client:
        health = client.get("/health")

        assert health.status_code == 200
        assert health.json()["model_ready"] is True
        assert client.get("/docs").status_code == 200