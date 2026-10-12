import pytest
from fastapi.testclient import TestClient

from app.agent import Reply
from app.config import Settings
from app.errors import LlmUnavailable
from app.server import create_app
from app.tools.registry import ToolRegistry


class FakeLlm:
    def status(self):
        return {"reachable": True, "model_available": True, "model_loaded": False}


class FakeAgent:
    def __init__(self, error=None):
        self.error = error
        self.history = []
        self.registry = ToolRegistry()

    def reply(self, text):
        if self.error:
            raise self.error
        self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": f"eco {text}"}]
        return Reply(f"eco {text}", ["search_web"])

    def reset(self):
        self.history = []


def client_for(token="", error=None):
    settings = Settings(api_token=token)
    return TestClient(create_app(settings, agent_factory=lambda: FakeAgent(error), llm=FakeLlm()))


def test_health_reports_services():
    health = client_for().get("/health").json()
    assert health["status"] == "ok"
    assert health["services"]["ollama"]["reachable"] is True
    assert health["services"]["n8n"] == {"configured": False}
    assert health["auth_required"] is False


def test_create_message_returns_reply_and_tools():
    response = client_for().post("/chat/messages", json={"text": "hola"})
    assert response.status_code == 200
    assert response.json()["text"] == "eco hola"
    assert response.json()["tools_used"] == ["search_web"]
    assert "blopa_session" in response.cookies


def test_conversation_is_kept_per_session():
    client = client_for()
    client.post("/chat/messages", json={"text": "hola"})
    assert [m["content"] for m in client.get("/chat/messages").json()["messages"]] == ["hola", "eco hola"]
    assert client_for().get("/chat/messages").json()["messages"] == []


def test_sessions_do_not_share_history():
    app_client = client_for()
    other = TestClient(app_client.app)
    app_client.post("/chat/messages", json={"text": "secreto"})
    assert other.get("/chat/messages").json()["messages"] == []


def test_delete_messages_resets_conversation():
    client = client_for()
    client.post("/chat/messages", json={"text": "hola"})
    assert client.delete("/chat/messages").status_code == 204
    assert client.get("/chat/messages").json()["messages"] == []


def test_empty_message_is_rejected():
    assert client_for().post("/chat/messages", json={"text": ""}).status_code == 422


def test_llm_errors_become_clear_503():
    response = client_for(error=LlmUnavailable("http://ollama:11434")).post("/chat/messages", json={"text": "hola"})
    assert response.status_code == 503
    assert "No puedo conectar con Ollama" in response.json()["detail"]


@pytest.mark.parametrize("header", [None, "Bearer equivocado", "secreto"])
def test_token_is_required_when_configured(header):
    headers = {"Authorization": header} if header else {}
    response = client_for(token="secreto").post("/chat/messages", json={"text": "hola"}, headers=headers)
    assert response.status_code == 401


def test_valid_token_is_accepted():
    client = client_for(token="secreto")
    response = client.post("/chat/messages", json={"text": "hola"}, headers={"Authorization": "Bearer secreto"})
    assert response.status_code == 200


def test_health_stays_open_with_token():
    assert client_for(token="secreto").get("/health").json()["auth_required"] is True


def test_serves_web_interface(tmp_path):
    (tmp_path / "index.html").write_text("<title>BLOPA</title>")
    app = create_app(Settings(), agent_factory=FakeAgent, llm=FakeLlm(), web_dir=tmp_path)
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "<title>BLOPA</title>" in response.text
