import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.concerns.truncates_text import TruncatesText
from app.tools.base import Tool
from app.url_guard import resolve, ensure_public

NOISE_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg", "iframe"]
READABLE_TYPES = ("text/html", "text/plain", "application/xhtml+xml")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15"


class ReadPageTool(TruncatesText, Tool):
    name = "read_page"
    description = (
        "Lee el texto de una página web pública. Úsala cuando los resultados de search_web "
        "no tengan suficiente detalle; pasa la URL exacta de uno de los resultados."
    )
    parameters = {
        "type": "object",
        "properties": {"url": {"type": "string", "description": "URL completa de la página."}},
        "required": ["url"],
    }
    max_chars = 2500
    max_redirects = 5
    max_bytes = 2_000_000

    def __init__(self, transport=None, resolver=resolve):
        self.resolver = resolver
        self.http = httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=False,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "es-MX,es;q=0.9"},
            transport=transport,
        )

    def call(self, url):
        response = self._fetch(url)
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith(READABLE_TYPES):
            return f"La página {url} no es texto legible ({content_type or 'tipo desconocido'})."
        text = self._extract_text(response.text) if "html" in content_type else response.text
        if not text:
            return f"La página {url} no tiene texto legible."
        return self.truncate(f"Sitio: {response.url.host}\n{text}")

    def _fetch(self, url):
        for _ in range(self.max_redirects + 1):
            ensure_public(url, self.resolver)
            response = self.http.get(url)
            if not response.is_redirect:
                response.raise_for_status()
                if len(response.content) > self.max_bytes:
                    raise ValueError("la página es demasiado grande")
                return response
            url = urljoin(url, response.headers["location"])
        raise ValueError("la página redirige demasiadas veces")

    def _extract_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(NOISE_TAGS):
            tag.decompose()
        root = soup.find("article") or soup.find("main") or soup.body or soup
        return re.sub(r"\s*\n\s*", "\n", re.sub(r"[ \t]+", " ", root.get_text("\n"))).strip()
