from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.auth import require_token
from app.voice.transcription import TranscriptionError

MAX_AUDIO_BYTES = 10 * 1024 * 1024


def require_voice(request: Request):
    if request.app.state.voice is None:
        raise HTTPException(status_code=404, detail="El servicio de voz no está configurado (WHISPER_URL).")
    return request.app.state.voice


router = APIRouter(prefix="/voice", dependencies=[Depends(require_token)])


@router.post("/transcriptions")
async def create_transcription(audio: UploadFile = File(...), voice=Depends(require_voice)):
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=422, detail="No se grabó nada.")
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="La grabación es demasiado larga.")
    try:
        result = voice.transcribe(data, audio.filename or "audio.webm", audio.content_type or "application/octet-stream")
    except TranscriptionError as error:
        raise HTTPException(status_code=502, detail=str(error))
    if not result.get("text"):
        raise HTTPException(status_code=422, detail="No escuché nada. Intenta hablar más cerca del micrófono.")
    return result
