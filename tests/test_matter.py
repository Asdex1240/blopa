import json

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.home.client import HomeAssistantError
from app.home.matter import MatterError, MatterPairing, clean_code
from app.home.socket import HomeAssistantSocket
from app.server import create_app


class FakeSocket:
    def __init__(self, replies):
        self.replies = list(replies)
        self.sent = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def send(self, data):
        self.sent.append(json.loads(data))

    def recv(self, timeout=None):
        return json.dumps(self.replies.pop(0))


def connector_for(*sockets):
    queue = list(sockets)
    return lambda url, **options: queue.pop(0)


def ha_socket(*results):
    sockets = [
        FakeSocket([{"type": "auth_required"}, {"type": "auth_ok"}, {"id": 1, **result}])
        for result in results
    ]
    return HomeAssistantSocket("http://homeassistant:8123", "token", connector=connector_for(*sockets)), sockets


@pytest.mark.parametrize("code, expected", [
    ("3497-011-2332", "34970112332"),
    (" 3497 011 2332 ", "34970112332"),
    ("mt:y.k9042c00kj0j1000", "MT:Y.K9042C00KJ0J1000"),
])
def test_clean_code(code, expected):
    assert clean_code(code) == expected


@pytest.mark.parametrize("code", ["1234", "abcdefghijk", "1234-567-890-12"])
def test_rejects_bad_codes(code):
    with pytest.raises(MatterError):
        clean_code(code)


def test_socket_uses_websocket_url_and_token():
    socket, sockets = ha_socket({"success": True, "result": {"ok": 1}})
    assert socket.url == "ws://homeassistant:8123/api/websocket"
    assert socket.call("ping/test", value=3) == {"ok": 1}
    assert sockets[0].sent == [{"type": "auth", "access_token": "token"}, {"id": 1, "type": "ping/test", "value": 3}]


def test_socket_raises_on_errors():
    socket, _ = ha_socket({"success": False, "error": {"message": "Commission failed"}})
    with pytest.raises(HomeAssistantError, match="Commission failed"):
        socket.call("matter/commission")


def test_pair_existing_device_on_network():
    socket, sockets = ha_socket({"success": True, "result": None})
    MatterPairing(socket, "ws://matter/ws").pair("3497-011-2332")
    assert sockets[0].sent[1] == {"id": 1, "type": "matter/commission", "code": "34970112332", "network_only": True}


def test_pair_new_device_sets_wifi_first():
    socket, sockets = ha_socket({"success": True, "result": None}, {"success": True, "result": None})
    MatterPairing(socket, "ws://matter/ws").pair("34970112332", wifi_ssid="Casa", wifi_password="secreta")
    assert sockets[0].sent[1] == {"id": 1, "type": "matter/set_wifi_credentials", "network_name": "Casa", "password": "secreta"}
    assert sockets[1].sent[1]["network_only"] is False


def test_discover_lists_commissionable_nodes():
    matter_socket = FakeSocket([
        {"server_version": "1.4.0"},
        {"message_id": "discover", "result": [
            {"instance_name": "ABC", "device_name": "Foco Steren", "vendor_id": 4417, "product_id": 1, "host_name": "E03ECB.local", "commissioning_mode": 2},
            {"instance_name": "DEF", "vendor_id": 1, "product_id": 2},
        ]},
    ])
    found = MatterPairing(None, "ws://matter/ws", connector=connector_for(matter_socket)).discover()
    assert matter_socket.sent == [{"message_id": "discover", "command": "discover", "args": {}}]
    assert [item["name"] for item in found] == ["Foco Steren", "Dispositivo Matter 1:2"]


class FakeMatter:
    def __init__(self, error=None):
        self.error = error
        self.paired = []

    def status(self):
        return {"configured": True, "reachable": True}

    def discover(self):
        return [{"id": "ABC", "name": "Foco Steren"}]

    def pair(self, code, wifi_ssid=None, wifi_password=None):
        if self.error:
            raise self.error
        self.paired.append((code, wifi_ssid, wifi_password))


class FakeLlm:
    def status(self):
        return {"reachable": True, "model_available": True, "model_loaded": True}


def api_with(tmp_path, matter):
    settings = Settings(ha_url="http://homeassistant:8123", ha_token="token", data_dir=str(tmp_path))
    return TestClient(create_app(settings, llm=FakeLlm(), web_dir=tmp_path / "none", matter=matter))


def test_pairing_routes(tmp_path):
    matter = FakeMatter()
    client = api_with(tmp_path, matter)
    assert client.get("/devices/discovered").json() == {"devices": [{"id": "ABC", "name": "Foco Steren"}]}
    response = client.post("/devices/pairings", json={"code": "3497-011-2332", "wifi_ssid": "Casa", "wifi_password": "x"})
    assert response.status_code == 201
    assert matter.paired == [("3497-011-2332", "Casa", "x")]


@pytest.mark.parametrize("error, status", [
    (MatterError("El código debe tener 11 dígitos"), 422),
    (HomeAssistantError("Commission failed"), 502),
])
def test_pairing_errors(tmp_path, error, status):
    response = api_with(tmp_path, FakeMatter(error)).post("/devices/pairings", json={"code": "34970112332"})
    assert response.status_code == status


@pytest.mark.parametrize("message", ["No pude hablar con Home Assistant: timed out in 180.0s", "Commission failed: No commissionable device was discovered"])
def test_pair_explains_device_not_found(message):
    socket, _ = ha_socket({"success": False, "error": {"message": message}})
    with pytest.raises(MatterError, match="No encontré ningún dispositivo esperando con ese código"):
        MatterPairing(socket, "ws://matter/ws").pair("34970112332")
