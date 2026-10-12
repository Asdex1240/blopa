import time

import httpx

from app.concerns.truncates_text import TruncatesText


class AutomationRunner(TruncatesText):
    max_chars = 800

    def __init__(self, repository, n8n_url, transport=None):
        self.repository = repository
        self.n8n_url = n8n_url.rstrip("/")
        self.http = httpx.Client(timeout=httpx.Timeout(30.0, connect=5.0), transport=transport)

    def webhook_url(self, automation):
        return f"{self.n8n_url}/webhook/{automation.webhook_path}"

    def status(self):
        try:
            reachable = self.http.get(f"{self.n8n_url}/healthz", timeout=2.0).is_success
        except httpx.HTTPError:
            reachable = False
        return {"configured": True, "reachable": reachable}

    def run(self, automation, text="", source="panel"):
        started = time.monotonic()
        ok, status_code, detail = self._call(automation, text, source)
        duration_ms = round((time.monotonic() - started) * 1000)
        return self.repository.record_run(automation.id, ok, status_code, detail, duration_ms, source)

    def _call(self, automation, text, source):
        payload = {"text": text, "source": source, "automation": automation.name}
        try:
            response = self.http.post(self.webhook_url(automation), json=payload)
        except httpx.TimeoutException:
            return False, None, "n8n no respondió a tiempo."
        except httpx.HTTPError as error:
            return False, None, f"No pude conectar con n8n: {error}"
        return response.is_success, response.status_code, self.truncate(response.text.strip())
