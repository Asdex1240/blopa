import threading
from datetime import datetime

import httpx
import pytest

from app.tools.date_time import DateTimeTool
from app.tools.read_page import ReadPageTool
from app.tools.search_web import SearchWebTool
from app.url_guard import BlockedUrl, ensure_public


def public_resolver(host, port):
    return ["93.184.216.34"]


class FakeEngine:
    def __init__(self, results):
        self.results = results
        self.queries = []

    def general(self, query, max_results):
        self.queries.append(("general", query))
        return self.results

    def news(self, query, max_results):
        self.queries.append(("news", query))
        return self.results


def test_date_time_in_spanish():
    tool = DateTimeTool("America/Monterrey", clock=lambda tz: datetime(2026, 10, 12, 13, 45, tzinfo=tz))
    assert tool.call() == (
        "Hoy es lunes 12 de octubre de 2026, son las 13:45 (America/Monterrey). Fecha ISO: 2026-10-12."
    )


def test_search_formats_results_with_site():
    engine = FakeEngine([{"title": "Clima", "url": "https://www.meteored.mx/x", "snippet": "Soleado"}])
    output = SearchWebTool(engine).call("clima Monterrey")
    assert "Sitio: meteored.mx" in output
    assert "Soleado" in output


def test_search_news_uses_source_and_date():
    engine = FakeEngine([{
        "title": "Peregrinaciones", "url": "https://msn.com/a", "snippet": "...",
        "source": "Reporte Índigo", "date": "2026-10-12T19:31:00+00:00",
    }])
    output = SearchWebTool(engine).call("Monterrey", kind="news")
    assert engine.queries == [("news", "Monterrey")]
    assert "Sitio: Reporte Índigo" in output
    assert "(2026-10-12)" in output


def test_search_gives_up_when_engine_hangs():
    release = threading.Event()

    class HangingEngine:
        def general(self, query, max_results):
            release.wait(5)
            return []

    tool = SearchWebTool(HangingEngine())
    tool.time_limit = 0.1
    with pytest.raises(TimeoutError, match="no respondió"):
        tool.call("algo")
    release.set()


def test_search_without_results():
    assert "No encontré resultados" in SearchWebTool(FakeEngine([])).call("xyz")


@pytest.mark.parametrize("address", ["127.0.0.1", "192.168.1.1", "10.0.0.5", "172.18.0.2", "169.254.1.1", "::1"])
def test_guard_blocks_local_addresses(address):
    with pytest.raises(BlockedUrl, match="red local"):
        ensure_public("http://router/", resolver=lambda host, port: [address])


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com", "http://"])
def test_guard_blocks_other_schemes(url):
    with pytest.raises(BlockedUrl):
        ensure_public(url, resolver=public_resolver)


def test_guard_allows_public_address():
    assert ensure_public("https://example.com/", resolver=public_resolver) == "https://example.com/"


def page_tool(handler, resolver=public_resolver):
    return ReadPageTool(transport=httpx.MockTransport(handler), resolver=resolver)


def test_read_page_extracts_main_text():
    html = """<html><head><script>x()</script></head><body>
        <nav>Menú</nav><article><h1>Título</h1><p>Texto   importante.</p></article><footer>Pie</footer>
    </body></html>"""
    tool = page_tool(lambda request: httpx.Response(200, html=html))
    output = tool.call("https://example.com/nota")
    assert output == "Sitio: example.com\nTítulo\nTexto importante."


def test_read_page_rechecks_redirects():
    def handler(request):
        return httpx.Response(302, headers={"location": "http://192.168.1.1/admin"})

    def resolver(host, port):
        return ["192.168.1.1"] if host == "192.168.1.1" else ["93.184.216.34"]

    with pytest.raises(BlockedUrl):
        page_tool(handler, resolver).call("https://example.com/")


def test_read_page_rejects_binary_content():
    tool = page_tool(lambda request: httpx.Response(200, content=b"%PDF", headers={"content-type": "application/pdf"}))
    assert "no es texto legible" in tool.call("https://example.com/a.pdf")


def test_read_page_truncates_long_text():
    tool = page_tool(lambda request: httpx.Response(200, text="palabra " * 2000))
    assert len(tool.call("https://example.com/")) <= ReadPageTool.max_chars + 10
