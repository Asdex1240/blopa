import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.server import create_app


class FakeLlm:
    def status(self):
        return {"reachable": True, "model_available": True, "model_loaded": True}


def n8n(request):
    if request.url.path == "/healthz":
        return httpx.Response(200, json={"status": "ok"})
    if request.url.path == "/webhook/blopa-ping":
        return httpx.Response(200, json={"message": "pong"})
    return httpx.Response(404, json={"message": "not registered"})


@pytest.fixture
def client(tmp_path):
    settings = Settings(n8n_url="http://n8n:5678", data_dir=str(tmp_path))
    return TestClient(create_app(settings, llm=FakeLlm(), web_dir=tmp_path / "none", n8n_transport=httpx.MockTransport(n8n)))


PING = {"name": "Ping de prueba", "description": "Prueba la conexión", "webhook_path": "blopa-ping"}


def test_health_reports_n8n(client):
    assert client.get("/health").json()["services"]["n8n"] == {"configured": True, "reachable": True}


def test_create_and_list(client):
    created = client.post("/automations", json=PING)
    assert created.status_code == 201
    assert created.json()["webhook_url"] == "http://n8n:5678/webhook/blopa-ping"
    assert created.json()["requires_confirmation"] is True
    assert [item["name"] for item in client.get("/automations").json()["automations"]] == ["Ping de prueba"]


def test_duplicate_name_is_conflict(client):
    client.post("/automations", json=PING)
    assert client.post("/automations", json=PING).status_code == 409


@pytest.mark.parametrize("path", ["http://evil.com/x", "../admin", "/blopa", "a b", ""])
def test_rejects_invalid_webhook_paths(client, path):
    assert client.post("/automations", json={**PING, "webhook_path": path}).status_code == 422


def test_patch_updates_fields(client):
    automation_id = client.post("/automations", json=PING).json()["id"]
    response = client.patch(f"/automations/{automation_id}", json={"requires_confirmation": False})
    assert response.json()["requires_confirmation"] is False


def test_run_from_panel_records_history(client):
    automation_id = client.post("/automations", json=PING).json()["id"]
    run = client.post(f"/automations/{automation_id}/runs", json={"text": "hola"}).json()
    assert run["ok"] is True
    assert run["source"] == "panel"
    assert client.get("/automation-runs").json()["runs"][0]["automation_name"] == "Ping de prueba"
    assert client.get("/automations").json()["automations"][0]["last_run"]["ok"] is True


def test_failed_run_is_recorded(client):
    automation_id = client.post("/automations", json={**PING, "webhook_path": "missing"}).json()["id"]
    run = client.post(f"/automations/{automation_id}/runs", json={}).json()
    assert run["ok"] is False
    assert run["status_code"] == 404


def test_delete_and_missing(client):
    automation_id = client.post("/automations", json=PING).json()["id"]
    assert client.delete(f"/automations/{automation_id}").status_code == 204
    assert client.delete(f"/automations/{automation_id}").status_code == 404


def test_routes_absent_without_n8n(tmp_path):
    app = create_app(Settings(data_dir=str(tmp_path)), llm=FakeLlm(), web_dir=tmp_path / "none")
    assert TestClient(app).get("/automations").status_code == 404
