from pathlib import Path

from app.agent import Agent
from app.automations.repository import AutomationRepository
from app.automations.runner import AutomationRunner
from app.config import Settings
from app.database import Database
from app.llm import OllamaClient
from app.search.duckduckgo import DuckDuckGoSearch
from app.tools.date_time import DateTimeTool
from app.tools.read_page import ReadPageTool
from app.tools.registry import ToolRegistry
from app.tools.run_automation import RunAutomationTool
from app.tools.search_web import SearchWebTool


def build_llm(settings):
    return OllamaClient(settings)


def build_automations(settings, transport=None):
    if not settings.n8n_url:
        return None, None
    repository = AutomationRepository(Database(Path(settings.data_dir) / "blopa.db"))
    return repository, AutomationRunner(repository, settings.n8n_url, transport=transport)


def build_registry(settings, automations=None, runner=None):
    tools = [
        DateTimeTool(settings.timezone),
        SearchWebTool(DuckDuckGoSearch()),
        ReadPageTool(),
    ]
    if automations and runner:
        tools.append(RunAutomationTool(automations, runner))
    return ToolRegistry(tools)


def build_agent(settings=None, llm=None, automations=None, runner=None):
    settings = settings or Settings.from_env()
    if automations is None:
        automations, runner = build_automations(settings)
    return Agent(
        llm or build_llm(settings),
        build_registry(settings, automations, runner),
        history_limit=settings.history_limit,
        context=DateTimeTool(settings.timezone).call,
    )
