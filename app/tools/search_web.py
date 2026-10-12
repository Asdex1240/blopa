from urllib.parse import urlparse

from app.concerns.time_limited import TimeLimited
from app.concerns.truncates_text import TruncatesText
from app.tools.base import Tool


class SearchWebTool(TimeLimited, TruncatesText, Tool):
    name = "search_web"
    description = (
        "Busca en internet información actual: noticias, precios, clima, vuelos, eventos, "
        "resultados deportivos o cualquier dato que pueda haber cambiado. "
        "Usa kind='news' para noticias y kind='general' para todo lo demás."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Qué buscar, en español y con palabras clave concretas."},
            "kind": {"type": "string", "enum": ["general", "news"], "description": "Tipo de búsqueda."},
        },
        "required": ["query"],
    }
    max_results = 5

    def __init__(self, engine):
        self.engine = engine

    def call(self, query, kind="general"):
        search = self.engine.news if kind == "news" else self.engine.general
        results = self.within_time_limit(search, query, self.max_results)
        if not results:
            return f"No encontré resultados para «{query}». Intenta con otras palabras."
        return self.truncate("\n\n".join(self._format(number, item) for number, item in enumerate(results, 1)))

    def _format(self, number, item):
        site = item.get("source") or urlparse(item["url"]).netloc.removeprefix("www.")
        date = f" ({item['date'][:10]})" if item.get("date") else ""
        return f"[{number}] {item['title']}{date}\nSitio: {site}\nURL: {item['url']}\n{item['snippet']}"
