from pathlib import Path

from app.agent import Agent
from app.automations.repository import AutomationRepository
from app.automations.runner import AutomationRunner
from app.config import Settings
from app.database import Database
from app.home.client import HomeAssistantClient
from app.home.devices import DeviceDirectory
from app.home.matter import MatterPairing
from app.home.socket import HomeAssistantSocket
from app.llm import OllamaClient
from app.search.duckduckgo import DuckDuckGoSearch
from app.tools.date_time import DateTimeTool
from app.tools.home import HomeControlDeviceTool, HomeDeviceStatusTool, HomeListDevicesTool
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


def build_home(settings, transport=None):
    if not (settings.ha_url and settings.ha_token):
        return None
    client = HomeAssistantClient(settings.ha_url, settings.ha_token, transport=transport)
    return DeviceDirectory(client, HomeAssistantSocket(settings.ha_url, settings.ha_token))


def build_matter(settings):
    if not (settings.ha_url and settings.ha_token and settings.matter_url):
        return None
    return MatterPairing(HomeAssistantSocket(settings.ha_url, settings.ha_token), settings.matter_url)


def build_registry(settings, automations=None, runner=None, home=None):
    tools = [
        DateTimeTool(settings.timezone),
        SearchWebTool(DuckDuckGoSearch()),
        ReadPageTool(),
    ]
    if automations and runner:
        tools.append(RunAutomationTool(automations, runner))
    if home:
        tools += [HomeListDevicesTool(home), HomeDeviceStatusTool(home), HomeControlDeviceTool(home)]
    return ToolRegistry(tools)


def build_agent(settings=None, llm=None, automations=None, runner=None, home=None):
    settings = settings or Settings.from_env()
    if automations is None:
        automations, runner = build_automations(settings)
    if home is None:
        home = build_home(settings)
    return Agent(
        llm or build_llm(settings),
        build_registry(settings, automations, runner, home),
        history_limit=settings.history_limit,
        context=DateTimeTool(settings.timezone).call,
    )
