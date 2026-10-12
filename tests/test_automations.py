import json

import httpx
import pytest

from app.automations.repository import AutomationRepository, DuplicateAutomation
from app.automations.runner import AutomationRunner
from app.database import Database
from app.tools.run_automation import RunAutomationTool


@pytest.fixture
def repository(tmp_path):
    return AutomationRepository(Database(tmp_path / "blopa.db"))


def runner_for(repository, handler):
    return AutomationRunner(repository, "http://n8n:5678", transport=httpx.MockTransport(handler))


def ping(repository, **overrides):
    fields = {"name": "Ping de prueba", "description": "Prueba la conexión con n8n", "webhook_path": "blopa-ping"}
    return repository.create(**{**fields, **overrides})


def test_create_and_find_by_name_ignoring_case(repository):
    created = ping(repository)
    assert created.requires_confirmation is True
    assert repository.find_by_name("ping DE prueba") == created


def test_duplicate_names_are_rejected(repository):
    ping(repository)
    with pytest.raises(DuplicateAutomation):
        ping(repository, webhook_path="otro")


def test_update_ignores_unknown_columns(repository):
    automation = ping(repository)
    updated = repository.update(automation.id, description="Nueva", id=999, created_at="hack")
    assert updated.id == automation.id
    assert updated.description == "Nueva"
    assert updated.created_at == automation.created_at


def test_delete_removes_runs(repository):
    automation = ping(repository)
    repository.record_run(automation.id, True, 200, "ok", 10, "panel")
    assert repository.delete(automation.id)
    assert repository.runs() == []


def test_runner_posts_to_webhook_and_records_run(repository):
    sent = {}

    def handler(request):
        sent["url"] = str(request.url)
        sent["body"] = json.loads(request.content)
        return httpx.Response(200, json={"message": "Hola desde n8n"})

    automation = ping(repository)
    run = runner_for(repository, handler).run(automation, "hola", source="chat")
    assert sent["url"] == "http://n8n:5678/webhook/blopa-ping"
    assert sent["body"] == {"text": "hola", "source": "chat", "automation": "Ping de prueba"}
    assert run.ok is True
    assert "Hola desde n8n" in run.detail
    assert repository.last_runs()[automation.id] == run


def test_runner_records_n8n_errors(repository):
    automation = ping(repository)
    run = runner_for(repository, lambda request: httpx.Response(404, text="webhook not registered")).run(automation)
    assert run.ok is False
    assert run.status_code == 404


def test_runner_records_connection_failures(repository):
    def handler(request):
        raise httpx.ConnectError("refused")

    run = runner_for(repository, handler).run(ping(repository))
    assert run.ok is False
    assert "No pude conectar con n8n" in run.detail


def test_tool_lists_automations_in_schema(repository):
    ping(repository)
    tool = RunAutomationTool(repository, runner_for(repository, lambda request: httpx.Response(200)))
    schema = tool.schema()["function"]
    assert tool.available()
    assert schema["parameters"]["properties"]["name"]["enum"] == ["Ping de prueba"]
    assert "Prueba la conexión con n8n" in schema["description"]


def test_tool_is_unavailable_without_automations(repository):
    assert not RunAutomationTool(repository, None).available()


def test_tool_asks_confirmation_only_when_required(repository):
    ping(repository)
    ping(repository, name="Luces", webhook_path="luces", requires_confirmation=False)
    tool = RunAutomationTool(repository, None)
    assert "Ping de prueba" in tool.confirmation_for(name="Ping de prueba")
    assert tool.confirmation_for(name="Luces") is None


def test_tool_refuses_undeclared_automations(repository):
    tool = RunAutomationTool(repository, None)
    assert "No existe una automatización" in tool.call(name="borrar todo")


def test_tool_reports_result(repository):
    ping(repository)
    tool = RunAutomationTool(repository, runner_for(repository, lambda request: httpx.Response(200, text="listo")))
    assert "se ejecutó correctamente" in tool.call(name="Ping de prueba")
