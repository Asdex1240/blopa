from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.auth import require_token
from app.automations.repository import DuplicateAutomation

WEBHOOK_PATH = r"^[A-Za-z0-9][A-Za-z0-9_\-]*(/[A-Za-z0-9_\-]+)*$"


def require_n8n(request: Request):
    if request.app.state.automations is None:
        raise HTTPException(status_code=404, detail="n8n no está configurado.")


router = APIRouter(dependencies=[Depends(require_token), Depends(require_n8n)])


class AutomationIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    description: str = Field(min_length=1, max_length=300)
    webhook_path: str = Field(min_length=1, max_length=120, pattern=WEBHOOK_PATH)
    requires_confirmation: bool = True


class AutomationPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    description: str | None = Field(default=None, min_length=1, max_length=300)
    webhook_path: str | None = Field(default=None, min_length=1, max_length=120, pattern=WEBHOOK_PATH)
    requires_confirmation: bool | None = None


class RunIn(BaseModel):
    text: str = Field(default="", max_length=2000)


def present(request, automation, last_run=None):
    return {
        **automation.to_dict(),
        "webhook_url": request.app.state.runner.webhook_url(automation),
        "last_run": last_run and last_run.to_dict(),
    }


def find(request, automation_id):
    automation = request.app.state.automations.get(automation_id)
    if automation is None:
        raise HTTPException(status_code=404, detail="La automatización no existe.")
    return automation


def conflict(error):
    return HTTPException(status_code=409, detail=str(error))


@router.get("/automations")
def list_automations(request: Request):
    repository = request.app.state.automations
    last_runs = repository.last_runs()
    return {"automations": [present(request, item, last_runs.get(item.id)) for item in repository.list()]}


@router.post("/automations", status_code=201)
def create_automation(payload: AutomationIn, request: Request):
    try:
        automation = request.app.state.automations.create(**payload.model_dump())
    except DuplicateAutomation as error:
        raise conflict(error)
    return present(request, automation)


@router.patch("/automations/{automation_id}")
def update_automation(automation_id: int, payload: AutomationPatch, request: Request):
    find(request, automation_id)
    try:
        automation = request.app.state.automations.update(automation_id, **payload.model_dump(exclude_none=True))
    except DuplicateAutomation as error:
        raise conflict(error)
    return present(request, automation)


@router.delete("/automations/{automation_id}", status_code=204)
def delete_automation(automation_id: int, request: Request):
    find(request, automation_id)
    request.app.state.automations.delete(automation_id)


@router.get("/automations/{automation_id}/runs")
def list_runs(automation_id: int, request: Request, limit: int = Query(default=20, ge=1, le=200)):
    find(request, automation_id)
    return {"runs": [run.to_dict() for run in request.app.state.automations.runs(automation_id, limit)]}


@router.post("/automations/{automation_id}/runs", status_code=201)
def create_run(automation_id: int, payload: RunIn, request: Request):
    automation = find(request, automation_id)
    return request.app.state.runner.run(automation, payload.text, source="panel").to_dict()


@router.get("/automation-runs")
def list_all_runs(request: Request, limit: int = Query(default=50, ge=1, le=200)):
    return {"runs": [run.to_dict() for run in request.app.state.automations.runs(limit=limit)]}
