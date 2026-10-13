import json
import re

from websockets.exceptions import WebSocketException
from websockets.sync.client import connect

from app.errors import BlopaError
from app.home.client import HomeAssistantError

PAIRING_TIMEOUT_SECONDS = 180
NOT_FOUND_HINTS = ("timed out", "no commissionable device", "discovery")
NOT_FOUND = (
    "No encontré ningún dispositivo esperando con ese código. Revisa que el código siga vigente "
    "(dura pocos minutos), que el dispositivo esté encendido y conectado a tu Wi-Fi, y genera uno nuevo si hace falta."
)


class MatterError(BlopaError):
    pass


def clean_code(code):
    code = code.strip()
    if code.upper().startswith("MT:"):
        return code.upper()
    digits = re.sub(r"[\s-]", "", code)
    if not digits.isdigit() or len(digits) not in (11, 21):
        raise MatterError("El código debe tener 11 o 21 dígitos, o empezar con MT: si viene de un QR.")
    return digits


def describe(node):
    name = node.get("device_name") or f"Dispositivo Matter {node.get('vendor_id', '?')}:{node.get('product_id', '?')}"
    return {
        "id": node.get("instance_name") or node.get("host_name") or name,
        "name": name,
        "vendor_id": node.get("vendor_id"),
        "product_id": node.get("product_id"),
        "host": node.get("host_name"),
        "addresses": node.get("addresses") or [],
        "commissioning_mode": node.get("commissioning_mode"),
    }


class MatterPairing:
    def __init__(self, ha_socket, matter_url, connector=connect):
        self.ha_socket = ha_socket
        self.matter_url = matter_url
        self.connector = connector

    def status(self):
        try:
            with self.connector(self.matter_url, open_timeout=2, close_timeout=1) as socket:
                json.loads(socket.recv(timeout=2))
            return {"configured": True, "reachable": True}
        except (OSError, TimeoutError, WebSocketException):
            return {"configured": True, "reachable": False}

    def discover(self):
        try:
            with self.connector(self.matter_url, open_timeout=5, close_timeout=2) as socket:
                json.loads(socket.recv(timeout=5))
                socket.send(json.dumps({"message_id": "discover", "command": "discover", "args": {}}))
                while True:
                    message = json.loads(socket.recv(timeout=20))
                    if message.get("message_id") == "discover":
                        break
        except (OSError, TimeoutError, WebSocketException) as error:
            raise MatterError(f"No pude hablar con el servidor Matter: {error}")
        if "error_code" in message:
            raise MatterError(message.get("details") or "El servidor Matter no pudo buscar dispositivos.")
        return [describe(node) for node in message.get("result") or []]

    def pair(self, code, wifi_ssid=None, wifi_password=None):
        code = clean_code(code)
        if wifi_ssid:
            self.ha_socket.call("matter/set_wifi_credentials", network_name=wifi_ssid, password=wifi_password or "")
        try:
            self.ha_socket.call("matter/commission", timeout=PAIRING_TIMEOUT_SECONDS, code=code, network_only=not wifi_ssid)
        except HomeAssistantError as error:
            if any(hint in str(error).lower() for hint in NOT_FOUND_HINTS):
                raise MatterError(NOT_FOUND)
            raise
