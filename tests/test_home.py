import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.home.client import HomeAssistantClient
from app.home.devices import DeviceDirectory, DeviceNotFound, InvalidAction
from app.server import create_app
from app.tools.home import HomeControlDeviceTool, HomeDeviceStatusTool, HomeListDevicesTool

STATES = [
    {"entity_id": "light.sala", "state": "on", "attributes": {"friendly_name": "Luz de la sala", "brightness": 128}},
    {"entity_id": "light.cocina", "state": "off", "attributes": {"friendly_name": "Luz de la cocina"}},
    {"entity_id": "switch.cafetera", "state": "off", "attributes": {"friendly_name": "Cafetera"}},
    {"entity_id": "lock.puerta", "state": "locked", "attributes": {"friendly_name": "Puerta principal"}},
    {"entity_id": "climate.recamara", "state": "cool", "attributes": {"friendly_name": "Clima recámara", "current_temperature": 26, "temperature": 23}},
    {"entity_id": "sensor.humedad", "state": "40", "attributes": {"friendly_name": "Humedad"}},
]


class FakeHomeAssistant:
    def __init__(self):
        self.calls = []

    def __call__(self, request):
        if request.url.path == "/api/":
            return httpx.Response(200, json={"message": "API running."})
        if request.url.path == "/api/states":
            assert request.headers["authorization"] == "Bearer token"
            return httpx.Response(200, json=STATES)
        if request.url.path.startswith("/api/services/"):
            _, _, _, domain, service = request.url.path.split("/")
            self.calls.append((domain, service, json.loads(request.content)))
            return httpx.Response(200, json=[])
        return httpx.Response(404)


@pytest.fixture
def home():
    fake = FakeHomeAssistant()
    client = HomeAssistantClient("http://homeassistant:8123", "token", transport=httpx.MockTransport(fake))
    return DeviceDirectory(client), fake


def test_lists_only_controllable_domains(home):
    directory, _ = home
    assert [device.entity_id for device in directory.list()] == [
        "climate.recamara", "light.cocina", "light.sala", "lock.puerta", "switch.cafetera",
    ]


@pytest.mark.parametrize("query, expected", [
    ("Luz de la sala", "light.sala"),
    ("la luz de la sala", "light.sala"),
    ("luz sala", "light.sala"),
    ("cafetera", "switch.cafetera"),
    ("puerta", "lock.puerta"),
    ("clima de la recamara", "climate.recamara"),
    ("light.cocina", "light.cocina"),
])
def test_finds_devices_by_spoken_name(home, query, expected):
    directory, _ = home
    assert directory.find(query).entity_id == expected


def test_ambiguous_or_unknown_names_list_options(home):
    directory, _ = home
    with pytest.raises(DeviceNotFound, match="Opciones"):
        directory.find("garage")


def test_controls_with_mapped_service(home):
    directory, fake = home
    directory.control(directory.find("luz de la cocina"), "encender")
    directory.control(directory.find("sala"), "ajustar_brillo", 30)
    assert fake.calls == [
        ("light", "turn_on", {"entity_id": "light.cocina"}),
        ("light", "turn_on", {"entity_id": "light.sala", "brightness_pct": 30}),
    ]


def test_rejects_actions_outside_the_closed_list(home):
    directory, fake = home
    with pytest.raises(InvalidAction, match="Acciones permitidas: encender, apagar"):
        directory.control(directory.find("cafetera"), "desbloquear")
    assert fake.calls == []


@pytest.mark.parametrize("value", [None, "mucho", 0, 150])
def test_validates_values(home, value):
    directory, _ = home
    with pytest.raises(InvalidAction):
        directory.control(directory.find("sala"), "ajustar_brillo", value)


def test_state_labels_in_spanish(home):
    directory, _ = home
    assert directory.find("sala").state_label == "encendido al 50%"
    assert directory.find("puerta").state_label == "cerrada con llave"
    assert directory.find("clima").state_label == "enfriando, 26 °C (objetivo 23 °C)"


def test_control_tool_confirms_only_sensitive_devices(home):
    directory, _ = home
    tool = HomeControlDeviceTool(directory)
    assert tool.confirmation_for(device="luz de la sala", action="apagar") is None
    assert tool.confirmation_for(device="puerta principal", action="desbloquear") == (
        "Voy a quitar la llave de «Puerta principal» (cerradura)."
    )
    assert "poner a 21 °C" in tool.confirmation_for(device="clima", action="ajustar_temperatura", value=21)


def test_control_tool_reports_errors_as_text(home):
    directory, _ = home
    tool = HomeControlDeviceTool(directory)
    assert "no acepta" in tool.call(device="cafetera", action="abrir")
    assert "No encontré" in tool.call(device="garage", action="abrir")
    assert "Mandé la orden, pero «Cafetera» sigue apagado" in tool.call(device="cafetera", action="encender")


def test_list_and_status_tools(home):
    directory, _ = home
    assert "- Luz de la sala (luz): encendido al 50%" in HomeListDevicesTool(directory).call()
    assert HomeDeviceStatusTool(directory).call(device="puerta") == "Puerta principal (cerradura) está cerrada con llave."


class FakeLlm:
    def status(self):
        return {"reachable": True, "model_available": True, "model_loaded": True}


@pytest.fixture
def api(tmp_path):
    fake = FakeHomeAssistant()
    settings = Settings(ha_url="http://homeassistant:8123", ha_token="token", data_dir=str(tmp_path))
    app = create_app(settings, llm=FakeLlm(), web_dir=tmp_path / "none", ha_transport=httpx.MockTransport(fake))
    return TestClient(app), fake


def test_health_and_tools_include_home(api):
    client, _ = api
    health = client.get("/health").json()
    assert health["services"]["home_assistant"] == {"configured": True, "reachable": True}
    assert {"home_list_devices", "home_device_status", "home_control_device"} <= set(health["tools"])


def test_device_routes(api):
    client, fake = api
    devices = client.get("/devices").json()["devices"]
    lock = next(device for device in devices if device["entity_id"] == "lock.puerta")
    assert lock["sensitive"] is True
    assert lock["actions"] == ["bloquear", "desbloquear"]
    assert client.post("/devices/light.cocina/actions", json={"action": "encender"}).status_code == 202
    assert client.post("/devices/light.cocina/actions", json={"action": "abrir"}).status_code == 422
    assert client.get("/devices/light.nada").status_code == 404
    assert fake.calls == [("light", "turn_on", {"entity_id": "light.cocina"})]


def test_routes_absent_without_home_assistant(tmp_path):
    app = create_app(Settings(data_dir=str(tmp_path)), llm=FakeLlm(), web_dir=tmp_path / "none")
    assert TestClient(app).get("/devices").status_code == 404


@pytest.mark.parametrize("text, command, question", [
    ("¿Qué luces están prendidas?", False, True),
    ("¿Está prendido?", False, True),
    ("Abre la persiana de la cocina", True, False),
    ("Pon el clima recámara a 22", True, False),
    ("Pon el foco al 30 por ciento", True, False),
    ("Préndelo al 60", True, False),
    ("Ponlo al máximo", True, False),
    ("Bájale un poco", True, False),
    ("Apágalo", True, False),
    ("¿Cómo está el clima en Saltillo?", False, False),
    ("¿Qué temperatura hace en Guadalajara?", False, False),
    ("Pon música", False, False),
    ("¿Qué hay de nuevo?", False, False),
    ("Cuéntame un chiste", False, False),
])
def test_classifies_house_requests(home, text, command, question):
    directory, _ = home
    assert HomeControlDeviceTool(directory).required_for(text) is command
    assert HomeDeviceStatusTool(directory).required_for(text) is question
    assert HomeListDevicesTool(directory).required_for(text) is question


def test_waits_for_transitional_states_to_settle():
    states = iter(["locking", "locking", "jammed"])

    class Client:
        def states(self):
            return [{"entity_id": "lock.patio", "state": next(states), "attributes": {"friendly_name": "Patio"}}]

    naps = []
    directory = DeviceDirectory(Client(), sleep=naps.append)
    assert directory.settled("lock.patio").state == "jammed"
    assert naps == [0.5, 0.5]


def test_waits_for_slow_cloud_devices_to_report_the_change():
    states = iter(["on", "on", "off"])

    class Client:
        def states(self):
            return [{"entity_id": "light.foco", "state": next(states), "attributes": {"friendly_name": "Foco"}}]

    naps = []
    directory = DeviceDirectory(Client(), sleep=naps.append)
    before = directory.get("light.foco")
    assert directory.settled("light.foco", before=before).state == "off"
    assert naps == [0.5]


def test_spoken_kind_picks_the_only_device_of_that_kind():
    class Client:
        def states(self):
            return [
                {"entity_id": "light.shome_120", "state": "on", "attributes": {"friendly_name": "Luces"}},
                {"entity_id": "switch.cafetera", "state": "off", "attributes": {"friendly_name": "Cafetera"}},
            ]

    directory = DeviceDirectory(Client())
    assert directory.find("el foco Steren").entity_id == "light.shome_120"
    assert directory.find("Focos Teren").entity_id == "light.shome_120"
    assert directory.find("el contacto").entity_id == "switch.cafetera"


def test_spoken_kind_is_ambiguous_with_several_devices(home):
    directory, _ = home
    with pytest.raises(DeviceNotFound):
        directory.find("el foco")
