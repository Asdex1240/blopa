import time
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.auth import require_token
from app.config import Settings
from app.errors import BlopaError
from app.factory import build_agent, build_llm
from app.sessions import SessionStore

SESSION_COOKIE = "blopa_session"
WEB_DIR = Path(__file__).resolve().parent.parent / "web" / "dist"


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def create_app(settings=None, agent_factory=None, llm=None, web_dir=WEB_DIR):
    settings = settings or Settings.from_env()
    llm = llm or build_llm(settings)
    agent_factory = agent_factory or (lambda: build_agent(settings, llm))
    app = FastAPI(title="BLOPA", docs_url=None, redoc_url=None)
    app.state.settings = settings
    app.state.sessions = SessionStore(agent_factory)
    app.state.llm = llm
    app.state.tools = [tool["function"]["name"] for tool in agent_factory().registry.schemas()]

    @app.exception_handler(BlopaError)
    def blopa_error(request, error):
        return JSONResponse(status_code=503, content={"detail": str(error)})

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "model": settings.model,
            "timezone": settings.timezone,
            "auth_required": bool(settings.api_token),
            "tools": app.state.tools,
            "services": {
                "ollama": llm.status(),
                "n8n": {"configured": False},
                "home_assistant": {"configured": False},
            },
        }

    @app.get("/chat/messages", dependencies=[Depends(require_token)])
    def list_messages(request: Request, response: Response):
        session = open_session(request, response)
        return {"messages": session.agent.history}

    @app.post("/chat/messages", dependencies=[Depends(require_token)])
    def create_message(message: MessageIn, request: Request, response: Response):
        session = open_session(request, response)
        started = time.monotonic()
        with session.lock:
            reply = session.agent.reply(message.text.strip())
        return {
            "text": reply.text,
            "tools_used": reply.tools_used,
            "elapsed": round(time.monotonic() - started, 1),
        }

    @app.delete("/chat/messages", status_code=204, dependencies=[Depends(require_token)])
    def delete_messages(request: Request, response: Response):
        session = open_session(request, response)
        with session.lock:
            session.agent.reset()

    def open_session(request, response):
        session_id, session = app.state.sessions.fetch(request.cookies.get(SESSION_COOKIE))
        response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="strict", max_age=6 * 3600)
        return session

    if Path(web_dir).is_dir():
        app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")

    return app

