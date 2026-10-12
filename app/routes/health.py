from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request):
    state = request.app.state
    settings = state.settings
    return {
        "status": "ok",
        "model": settings.model,
        "timezone": settings.timezone,
        "auth_required": bool(settings.api_token),
        "tools": state.tools,
        "services": {
            "ollama": state.llm.status(),
            "n8n": state.runner.status() if state.runner else {"configured": False, "reachable": False},
            "home_assistant": {"configured": False},
        },
    }
