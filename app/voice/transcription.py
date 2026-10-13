import httpx

from app.errors import BlopaError


class TranscriptionError(BlopaError):
    pass


class TranscriptionClient:
    def __init__(self, url, transport=None):
        self.http = httpx.Client(base_url=url, timeout=httpx.Timeout(60.0, connect=3.0), transport=transport)

    def status(self):
        try:
            health = self.http.get("/health", timeout=2.0).json()
        except (httpx.HTTPError, ValueError):
            return {"configured": True, "reachable": False, "ready": False, "model": None}
        return {"configured": True, "reachable": True, "ready": bool(health.get("ready")), "model": health.get("model")}

    def transcribe(self, audio, filename, content_type, language="es"):
        try:
            response = self.http.post(
                "/transcriptions",
                files={"audio": (filename, audio, content_type)},
                data={"language": language},
            )
        except httpx.TimeoutException:
            raise TranscriptionError("La transcripción tardó demasiado.")
        except httpx.HTTPError:
            raise TranscriptionError("No pude conectar con el servicio de voz.")
        if response.is_error:
            raise TranscriptionError(response.json().get("detail", "No pude entender el audio."))
        return response.json()
