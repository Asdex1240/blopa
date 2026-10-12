from app.agent import Agent
from app.config import Settings
from app.llm import OllamaClient


def build_agent(settings=None):
    settings = settings or Settings.from_env()
    return Agent(OllamaClient(settings), history_limit=settings.history_limit)
