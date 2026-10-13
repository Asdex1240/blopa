from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth import require_token
from app.home.client import HomeAssistantError
from app.home.tuya import TuyaLinkError


def require_tuya(request: Request):
    if request.app.state.tuya is None:
        raise HTTPException(status_code=404, detail="Home Assistant no está configurado.")
    return request.app.state.tuya


router = APIRouter(prefix="/accounts", dependencies=[Depends(require_token)])


class LinkIn(BaseModel):
    user_code: str = Field(min_length=4, max_length=40)


def failed(error):
    status = 422 if isinstance(error, TuyaLinkError) else 502
    return HTTPException(status_code=status, detail=str(error))


@router.get("")
def list_accounts(tuya=Depends(require_tuya)):
    return {"accounts": tuya.list()}


@router.post("/tuya/links", status_code=201)
def create_link(payload: LinkIn, tuya=Depends(require_tuya)):
    try:
        return tuya.start(payload.user_code)
    except (TuyaLinkError, HomeAssistantError) as error:
        raise failed(error)


@router.post("/tuya/links/{link_id}/confirmations")
def create_confirmation(link_id: str, tuya=Depends(require_tuya)):
    try:
        return tuya.confirm(link_id)
    except (TuyaLinkError, HomeAssistantError) as error:
        raise failed(error)


@router.delete("/tuya/links/{link_id}", status_code=204)
def delete_link(link_id: str, tuya=Depends(require_tuya)):
    try:
        tuya.cancel(link_id)
    except HomeAssistantError:
        pass


@router.post("/tuya/refreshes", status_code=202)
def create_refresh(tuya=Depends(require_tuya)):
    try:
        tuya.refresh()
    except HomeAssistantError as error:
        raise failed(error)
    return {"refreshing": True}
