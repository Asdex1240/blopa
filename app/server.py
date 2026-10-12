from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.errors import BlopaError
from app.factory import build_agent, build_automations, build_llm
from app.routes import automations, chat, health
from app.sessions import SessionStore

WEB_DIR = Path(__file__).resolve().parent.parent / "web" / "dist"


def create_app(settings=None, agent_factory=None, llm=None, web_dir=WEB_DIR, n8n_transport=None):
    settings = settings or Settings.from_env()
    llm = llm or build_llm(settings)
    repository, runner = build_automations(settings, transport=n8n_transport)
    agent_factory = agent_factory or (lambda: build_agent(settings, llm, repository, runner))

    app = FastAPI(title="BLOPA", docs_url=None, redoc_url=None)
    app.state.settings = settings
    app.state.llm = llm
    app.state.automations = repository
    app.state.runner = runner
    app.state.sessions = SessionStore(agent_factory)
    app.state.tools = agent_factory().registry.names()

    @app.exception_handler(BlopaError)
    def blopa_error(request, error):
        return JSONResponse(status_code=503, content={"detail": str(error)})

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(automations.router)

    if Path(web_dir).is_dir():
        app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")

    return app
