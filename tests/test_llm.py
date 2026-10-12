import json

import httpx
import pytest

from app.config import Settings
from app.errors import LlmFailed, LlmUnavailable, ModelMissing
from app.llm import OllamaClient

SETTINGS = Settings(ollama_url="http://ollama:11434", model="qwen3:4b-instruct", num_ctx=2048, max_tokens=300)


def client_returning(handler):
    return OllamaClient(SETTINGS, transport=httpx.MockTransport(handler))


def test_chat_sends_model_options_and_returns_message():
    sent = {}

    def handler(request):
        sent.update(json.loads(request.content))
        return httpx.Response(200, json={"message": {"role": "assistant", "content": "Hola"}})

    message = client_returning(handler).chat([{"role": "user", "content": "hola"}])
    assert message["content"] == "Hola"
    assert sent["model"] == "qwen3:4b-instruct"
    assert sent["stream"] is False
    assert sent["think"] is False
    assert sent["options"] == {"num_ctx": 2048, "num_predict": 300}
    assert "tools" not in sent


def test_connection_error_raises_unavailable():
    def handler(request):
        raise httpx.ConnectError("refused")

    with pytest.raises(LlmUnavailable, match="No puedo conectar"):
        client_returning(handler).chat([])


def test_missing_model_raises_model_missing():
    def handler(request):
        return httpx.Response(404, json={"error": "model 'qwen3:4b-instruct' not found"})

    with pytest.raises(ModelMissing, match="ollama pull qwen3:4b-instruct"):
        client_returning(handler).chat([])


def test_server_error_raises_failed():
    def handler(request):
        return httpx.Response(500, json={"error": "out of memory"})

    with pytest.raises(LlmFailed, match="out of memory"):
        client_returning(handler).chat([])
