import io
import logging
import threading

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.transcriber import Transcriber

MAX_AUDIO_BYTES = 10 * 1024 * 1024

logger = logging.getLogger("uvicorn.error")


def load_in_background(transcriber):
    try:
        transcriber.load()
        logger.info("Modelo %s listo", transcriber.model_name)
    except Exception:
        logger.exception("No pude cargar el modelo %s", transcriber.model_name)


def create_app(transcriber=None):
    transcriber = transcriber or Transcriber()
    app = FastAPI(title="BLOPA voice", docs_url=None, redoc_url=None)

    @app.on_event("startup")
    def warm_up():
        threading.Thread(target=load_in_background, args=(transcriber,), daemon=True).start()

    @app.get("/health")
    def health():
        return {"status": "ok", "model": transcriber.model_name, "ready": transcriber.model is not None}

    @app.post("/transcriptions")
    async def create_transcription(audio: UploadFile = File(...), language: str = Form("es")):
        data = await audio.read()
        if not data:
            raise HTTPException(status_code=422, detail="El audio está vacío.")
        if len(data) > MAX_AUDIO_BYTES:
            raise HTTPException(status_code=413, detail="El audio es demasiado largo.")
        try:
            return transcriber.transcribe(io.BytesIO(data), language)
        except Exception as error:
            raise HTTPException(status_code=422, detail=f"No pude leer el audio: {error}")

    return app
