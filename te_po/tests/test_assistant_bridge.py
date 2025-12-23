import os

os.environ["PIPELINE_TOKEN"] = "test-token"
os.environ["HUMAN_BEARER_KEY"] = "test-token"

from fastapi.testclient import TestClient
from te_po.core.main import app


client = TestClient(app)


def test_health():
    response = client.get("/assistant/health", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
