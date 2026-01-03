import os

from fastapi.testclient import TestClient

from te_po.core.main import app


def test_app_imports():
    assert app is not None


def test_root_and_heartbeat_routes_exist():
    client = TestClient(app)
    resp_root = client.get("/")
    assert resp_root.status_code == 200
    resp_hb = client.get("/heartbeat")
    assert resp_hb.status_code == 200
