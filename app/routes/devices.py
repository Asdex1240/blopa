from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth import require_token
from app.home.client import HomeAssistantError
from app.home.devices import DeviceNotFound, InvalidAction
from app.home.matter import MatterError


def require_home(request: Request):
    if request.app.state.home is None:
        raise HTTPException(status_code=404, detail="Home Assistant no está configurado.")


router = APIRouter(prefix="/devices", dependencies=[Depends(require_token), Depends(require_home)])


class ActionIn(BaseModel):
    action: str
    value: float | None = None


class DeviceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class PairingIn(BaseModel):
    code: str = Field(min_length=11, max_length=80)
    wifi_ssid: str | None = Field(default=None, max_length=64)
    wifi_password: str | None = Field(default=None, max_length=128)


def require_matter(request: Request):
    if request.app.state.matter is None:
        raise HTTPException(status_code=404, detail="Matter no está configurado (MATTER_URL).")
    return request.app.state.matter


@router.get("")
def list_devices(request: Request):
    return {"devices": [device.to_dict() for device in request.app.state.home.list()]}


@router.get("/discovered")
def list_discovered(matter=Depends(require_matter)):
    try:
        return {"devices": matter.discover()}
    except MatterError as error:
        raise HTTPException(status_code=502, detail=str(error))


@router.post("/pairings", status_code=201)
def create_pairing(payload: PairingIn, matter=Depends(require_matter)):
    try:
        matter.pair(payload.code, payload.wifi_ssid or None, payload.wifi_password)
    except MatterError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except HomeAssistantError as error:
        raise HTTPException(status_code=502, detail=f"No se pudo emparejar: {error}")
    return {"paired": True}


@router.get("/{entity_id}")
def get_device(entity_id: str, request: Request):
    try:
        return request.app.state.home.get(entity_id).to_dict()
    except DeviceNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.patch("/{entity_id}")
def update_device(entity_id: str, payload: DeviceUpdate, request: Request):
    try:
        return request.app.state.home.rename(entity_id, payload.name).to_dict()
    except DeviceNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))
    except InvalidAction as error:
        raise HTTPException(status_code=422, detail=str(error))


@router.post("/{entity_id}/actions", status_code=202)
def create_action(entity_id: str, payload: ActionIn, request: Request):
    directory = request.app.state.home
    try:
        device = directory.get(entity_id)
        directory.control(device, payload.action, payload.value)
    except DeviceNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))
    except InvalidAction as error:
        raise HTTPException(status_code=422, detail=str(error))
    return {"entity_id": entity_id, "action": payload.action, "accepted": True}
