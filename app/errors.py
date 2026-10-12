class BlopaError(Exception):
    pass


class LlmUnavailable(BlopaError):
    def __init__(self, url):
        super().__init__(
            f"No puedo conectar con Ollama en {url}. "
            "Revisa que el contenedor esté arriba: docker compose up -d ollama"
        )


class ModelMissing(BlopaError):
    def __init__(self, model):
        super().__init__(
            f"El modelo {model} no está descargado. "
            f"Descárgalo con: docker compose exec ollama ollama pull {model}"
        )


class LlmFailed(BlopaError):
    def __init__(self, detail):
        super().__init__(f"Ollama respondió con un error: {detail}")
