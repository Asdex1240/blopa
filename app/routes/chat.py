import time

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from app.auth import require_token

SESSION_COOKIE = "blopa_session"
SESSION_SECONDS = 6 * 3600

router = APIRouter(prefix="/chat", dependencies=[Depends(require_token)])


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def open_session(request, response):
    session_id, session = request.app.state.sessions.fetch(request.cookies.get(SESSION_COOKIE))
    response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="strict", max_age=SESSION_SECONDS)
    return session


@router.get("/messages")
def list_messages(request: Request, response: Response):
    session = open_session(request, response)
    return {"messages": session.agent.history, "confirmation": session.agent.pending_confirmation}


@router.post("/messages")
def create_message(message: MessageIn, request: Request, response: Response):
    session = open_session(request, response)
    started = time.monotonic()
    with session.lock:
        reply = session.agent.reply(message.text.strip())
    return {
        "text": reply.text,
        "tools_used": reply.tools_used,
        "confirmation": reply.confirmation,
        "elapsed": round(time.monotonic() - started, 1),
    }


@router.delete("/messages", status_code=204)
def delete_messages(request: Request, response: Response):
    session = open_session(request, response)
    with session.lock:
        session.agent.reset()
