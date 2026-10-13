import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.home.client import HomeAssistantError
from app.home.devices import DeviceDirectory, InvalidAction
from app.server import create_app


def qr_step(token):
    return {
        "type": "form",
        "flow_id": "flow-1",
        "step_id": "scan",
        "data_schema": [{"name": "QR", "selector": {"qr_code": {"data": f"tuyaSmart--qrLogin?token={token}"}}}],
    }


class FakeHomeAssistant:
    def __init__(self, scans_needed=1, valid_code="BaJ0orh"):
        self.scans_needed = scans_needed
        self.valid_code = valid_code
        self.confirmations = 0
        self.aborted = []
        self.reloaded = []

    def __call__(self, request):
        path, method = request.url.path, request.method
        body = json.loads(request.content) if request.content else {}
        if path == "/api/":
            return httpx.Response(200, json={"message": "API running."})
        if path == "/api/states":
            return httpx.Response(200, json=[{"entity_id": "light.shome_120", "state": "on", "attributes": {"friendly_name": "SHOME-120"}}])
        if path == "/api/config/config_entries/entry":
            return httpx.Response(200, json=[
                {"entry_id": "e1", "domain": "tuya", "title": "ap-0007", "state": "loaded"},
                {"entry_id": "e2", "domain": "matter", "title": "Matter", "state": "loaded"},
            ])
        if path.endswith("/reload"):
            self.reloaded.append(path.split("/")[-2])
            return httpx.Response(200, json={"require_restart": False})
        if path == "/api/config/config_entries/flow" and method == "POST":
            assert body == {"handler": "tuya"}
            return httpx.Response(200, json={"type": "form", "flow_id": "flow-1", "step_id": "user"})
        if path == "/api/config/config_entries/flow/flow-1" and method == "DELETE":
            self.aborted.append("flow-1")
            return httpx.Response(200, json={"message": "Flow aborted"})
        if path == "/api/config/config_entries/flow/flow-1":
            if "user_code" in body:
                if body["user_code"] != self.valid_code:
                    return httpx.Response(200, json={
                        "type": "form", "step_id": "user", "errors": {"base": "login_error"},
                        "description_placeholders": {"msg": "user code invalid", "code": "1106"},
                    })
                return httpx.Response(200, json=qr_step("first"))
            self.confirmations += 1
            if self.confirmations < self.scans_needed:
                return httpx.Response(200, json={**qr_step(f"retry{self.confirmations}"), "errors": {"base": "login_error"}})
            return httpx.Response(200, json={"type": "create_entry", "title": "juan@correo.com"})
        return httpx.Response(404)


class FakeLlm:
    def status(self):
        return {"reachable": True, "model_available": True, "model_loaded": True}


def api_with(tmp_path, fake):
    settings = Settings(ha_url="http://homeassistant:8123", ha_token="token", data_dir=str(tmp_path))
    app = create_app(settings, llm=FakeLlm(), web_dir=tmp_path / "none", ha_transport=httpx.MockTransport(fake))
    return TestClient(app)


def test_lists_connected_tuya_accounts(tmp_path):
    client = api_with(tmp_path, FakeHomeAssistant())
    assert client.get("/accounts").json() == {"accounts": [{"id": "e1", "provider": "tuya", "title": "ap-0007", "state": "loaded"}]}


def test_link_returns_qr_then_connects(tmp_path):
    client = api_with(tmp_path, FakeHomeAssistant())
    link = client.post("/accounts/tuya/links", json={"user_code": "BaJ0orh"})
    assert link.status_code == 201
    assert link.json() == {"id": "flow-1", "qr": "tuyaSmart--qrLogin?token=first"}
    confirmed = client.post("/accounts/tuya/links/flow-1/confirmations").json()
    assert confirmed == {"connected": True, "title": "juan@correo.com", "qr": None}


def test_confirming_before_scanning_returns_a_new_qr(tmp_path):
    client = api_with(tmp_path, FakeHomeAssistant(scans_needed=2))
    client.post("/accounts/tuya/links", json={"user_code": "BaJ0orh"})
    first = client.post("/accounts/tuya/links/flow-1/confirmations").json()
    assert first == {"connected": False, "title": None, "qr": "tuyaSmart--qrLogin?token=retry1"}
    assert client.post("/accounts/tuya/links/flow-1/confirmations").json()["connected"] is True


def test_invalid_user_code_is_explained_and_flow_aborted(tmp_path):
    fake = FakeHomeAssistant()
    response = api_with(tmp_path, fake).post("/accounts/tuya/links", json={"user_code": "malo123"})
    assert response.status_code == 422
    assert "Smart Life no reconoció ese código" in response.json()["detail"]
    assert fake.aborted == ["flow-1"]


def test_cancel_and_refresh(tmp_path):
    fake = FakeHomeAssistant()
    client = api_with(tmp_path, fake)
    assert client.delete("/accounts/tuya/links/flow-1").status_code == 204
    assert client.post("/accounts/tuya/refreshes").status_code == 202
    assert fake.reloaded == ["e1"]


def test_accounts_absent_without_home_assistant(tmp_path):
    app = create_app(Settings(data_dir=str(tmp_path)), llm=FakeLlm(), web_dir=tmp_path / "none")
    assert TestClient(app).get("/accounts").status_code == 404


class FakeSocket:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def call(self, command, **payload):
        if self.error:
            raise self.error
        self.calls.append((command, payload))


class RenamingClient:
    def __init__(self):
        self.name = "SHOME-120"

    def states(self):
        return [{"entity_id": "light.shome_120", "state": "on", "attributes": {"friendly_name": self.name}}]


def test_rename_updates_entity_registry():
    socket = FakeSocket()
    directory = DeviceDirectory(RenamingClient(), socket)
    directory.rename("light.shome_120", "  Luz del cuarto ")
    assert socket.calls == [("config/entity_registry/update", {"entity_id": "light.shome_120", "name": "Luz del cuarto"})]


def test_rename_explains_entities_without_registry():
    directory = DeviceDirectory(RenamingClient(), FakeSocket(HomeAssistantError("Entity not found")))
    with pytest.raises(InvalidAction, match="no permite cambiarle el nombre"):
        directory.rename("light.shome_120", "Luz")
