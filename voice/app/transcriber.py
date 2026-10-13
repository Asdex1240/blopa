import os
import threading
import time

from faster_whisper import WhisperModel

DEFAULT_HOTWORDS = "Steren ping"


class Transcriber:
    def __init__(self, model_name=None, compute_type=None, model_dir=None):
        self.model_name = model_name or os.environ.get("WHISPER_MODEL", "small")
        self.compute_type = compute_type or os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
        self.model_dir = model_dir or os.environ.get("WHISPER_MODEL_DIR", "/models")
        self.hotwords = os.environ.get("WHISPER_HOTWORDS", DEFAULT_HOTWORDS)
        self.model = None
        self.lock = threading.Lock()

    def load(self):
        with self.lock:
            if self.model is None:
                self.model = WhisperModel(self.model_name, device="cpu", compute_type=self.compute_type, download_root=self.model_dir)
        return self.model

    def transcribe(self, audio, language="es"):
        started = time.monotonic()
        segments, info = self.load().transcribe(
            audio,
            language=language,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
            hotwords=self.hotwords or None,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return {
            "text": text,
            "language": info.language,
            "duration": round(info.duration, 2),
            "elapsed": round(time.monotonic() - started, 2),
            "model": self.model_name,
        }
