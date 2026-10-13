import json

from websockets.exceptions import WebSocketException
from websockets.sync.client import connect

from app.home.client import HomeAssistantError


class HomeAssistantSocket:
    def __init__(self, url, token, connector=connect):
        self.url = f"{url.replace('http', 'ws', 1).rstrip('/')}/api/websocket"
        self.token = token
        self.connector = connector

    def call(self, command, timeout=30, **payload):
        try:
            with self.connector(self.url, open_timeout=5, close_timeout=2) as socket:
                self._authenticate(socket)
                socket.send(json.dumps({"id": 1, "type": command, **payload}))
                return self._result(socket, timeout)
        except (OSError, TimeoutError, WebSocketException) as error:
            raise HomeAssistantError(f"No pude hablar con Home Assistant: {error}")

    def _authenticate(self, socket):
        json.loads(socket.recv(timeout=5))
        socket.send(json.dumps({"type": "auth", "access_token": self.token}))
        if json.loads(socket.recv(timeout=5)).get("type") != "auth_ok":
            raise HomeAssistantError("Home Assistant rechazó el token de acceso (HA_TOKEN).")

    def _result(self, socket, timeout):
        while True:
            message = json.loads(socket.recv(timeout=timeout))
            if message.get("id") != 1:
                continue
            if not message.get("success"):
                raise HomeAssistantError(message.get("error", {}).get("message", "Home Assistant devolvió un error."))
            return message.get("result")
