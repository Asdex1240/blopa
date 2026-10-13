import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.server import create_app


class FakeLlm:
    def status(self):
        return {"reachable": True, "model_available": True, "model_loaded": True}


def whisper(text="Prende la luz de la sala.", status=200):
    received = {}

    def handler(request):
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "model": "small", "ready": True})
        received["body"] = request.content
        if status != 200:
            return httpx.Response(status, json={"detail": "No pude leer el audio: formato desconocido"})
        return httpx.Response(200, json={"text": text, "language": "es", "duration": 1.2, "elapsed": 0.9, "model": "small"})

    return handler, received


def client_for(tmp_path, handler):
    settings = Settings(whisper_url="http://whisper:9000", data_dir=str(tmp_path))
    app = create_app(settings, llm=FakeLlm(), web_dir=tmp_path / "none", voice_transport=httpx.MockTransport(handler))
    return TestClient(app)


def upload(client, data=b"fake-webm-audio"):
    return client.post("/voice/transcriptions", files={"audio": ("voz.webm", data, "audio/webm")})


def test_health_reports_voice(tmp_path):
    handler, _ = whisper()
    voice = client_for(tmp_path, handler).get("/health").json()["services"]["voice"]
    assert voice == {"configured": True, "reachable": True, "ready": True, "model": "small"}


def test_forwards_audio_and_returns_text(tmp_path):
    handler, received = whisper()
    response = upload(client_for(tmp_path, handler))
    assert response.status_code == 200
    assert response.json()["text"] == "Prende la luz de la sala."
    assert b"fake-webm-audio" in received["body"]
    assert b'name="language"' in received["body"]


def test_empty_recording_is_rejected(tmp_path):
    handler, _ = whisper()
    assert upload(client_for(tmp_path, handler), b"").status_code == 422


def test_silence_is_explained(tmp_path):
    handler, _ = whisper(text="")
    response = upload(client_for(tmp_path, handler))
    assert response.status_code == 422
    assert "No escuché nada" in response.json()["detail"]


def test_whisper_errors_are_reported(tmp_path):
    handler, _ = whisper(status=422)
    response = upload(client_for(tmp_path, handler))
    assert response.status_code == 502
    assert "formato desconocido" in response.json()["detail"]


def test_absent_without_whisper(tmp_path):
    app = create_app(Settings(data_dir=str(tmp_path)), llm=FakeLlm(), web_dir=tmp_path / "none")
    assert upload(TestClient(app)).status_code == 404
