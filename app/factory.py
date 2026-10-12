from app.agent import Agent
from app.config import Settings
from app.llm import OllamaClient
from app.search.duckduckgo import DuckDuckGoSearch
from app.tools.date_time import DateTimeTool
from app.tools.read_page import ReadPageTool
from app.tools.registry import ToolRegistry
from app.tools.search_web import SearchWebTool


def build_registry(settings):
    return ToolRegistry([
        DateTimeTool(settings.timezone),
        SearchWebTool(DuckDuckGoSearch()),
        ReadPageTool(),
    ])


def build_agent(settings=None):
    settings = settings or Settings.from_env()
    return Agent(
        OllamaClient(settings),
        build_registry(settings),
        history_limit=settings.history_limit,
        context=DateTimeTool(settings.timezone).call,
    )
