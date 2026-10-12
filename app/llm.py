import httpx

from app.errors import LlmFailed, LlmUnavailable, ModelMissing


class OllamaClient:
    def __init__(self, settings, transport=None):
        self.settings = settings
        self.http = httpx.Client(
            base_url=settings.ollama_url,
            timeout=httpx.Timeout(settings.request_timeout, connect=5.0),
            transport=transport,
        )

    def chat(self, messages, tools=None):
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "stream": False,
            "think": self.settings.think,
            "options": {"num_ctx": self.settings.num_ctx, "num_predict": self.settings.max_tokens},
        }
        if tools:
            payload["tools"] = tools
        return self._post("/api/chat", payload)["message"]

    def _post(self, path, payload):
        try:
            response = self.http.post(path, json=payload)
        except (httpx.ConnectError, httpx.ConnectTimeout):
            raise LlmUnavailable(self.settings.ollama_url)
        except httpx.TimeoutException:
            raise LlmFailed("tardó demasiado en responder")
        if response.status_code == 404:
            raise ModelMissing(self.settings.model)
        if response.is_error:
            raise LlmFailed(self._error_detail(response))
        return response.json()

    def _error_detail(self, response):
        try:
            return response.json().get("error", response.text)
        except ValueError:
            return response.text
