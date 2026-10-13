import httpx

from app.errors import BlopaError


class HomeAssistantError(BlopaError):
    pass


class HomeAssistantClient:
    def __init__(self, url, token, transport=None):
        self.http = httpx.Client(
            base_url=url.rstrip("/"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=httpx.Timeout(10.0, connect=3.0),
            transport=transport,
        )

    def status(self):
        try:
            reachable = self.http.get("/api/", timeout=2.0).is_success
        except httpx.HTTPError:
            reachable = False
        return {"configured": True, "reachable": reachable}

    def states(self):
        return self._request("GET", "/api/states")

    def call_service(self, domain, service, data):
        return self._request("POST", f"/api/services/{domain}/{service}", json=data)

    def config_entries(self, domain):
        return [entry for entry in self._request("GET", "/api/config/config_entries/entry") if entry["domain"] == domain]

    def reload_entry(self, entry_id):
        return self._request("POST", f"/api/config/config_entries/entry/{entry_id}/reload")

    def start_flow(self, handler):
        return self._request("POST", "/api/config/config_entries/flow", json={"handler": handler})

    def continue_flow(self, flow_id, data):
        return self._request("POST", f"/api/config/config_entries/flow/{flow_id}", json=data)

    def abort_flow(self, flow_id):
        return self._request("DELETE", f"/api/config/config_entries/flow/{flow_id}")

    def _request(self, method, path, **options):
        try:
            response = self.http.request(method, path, **options)
        except httpx.HTTPError as error:
            raise HomeAssistantError(f"No pude conectar con Home Assistant: {error}")
        if response.status_code == 401:
            raise HomeAssistantError("Home Assistant rechazó el token de acceso (HA_TOKEN).")
        if response.is_error:
            raise HomeAssistantError(f"Home Assistant respondió {response.status_code}: {response.text[:200]}")
        return response.json()
