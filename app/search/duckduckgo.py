from ddgs import DDGS


class DuckDuckGoSearch:
    def __init__(self, region="mx-es", timeout=10):
        self.region = region
        self.timeout = timeout

    def general(self, query, max_results):
        results = DDGS(timeout=self.timeout).text(query, region=self.region, max_results=max_results)
        return [
            {"title": item.get("title", ""), "url": item.get("href", ""), "snippet": item.get("body", "")}
            for item in results
        ]

    def news(self, query, max_results):
        results = DDGS(timeout=self.timeout).news(query, region=self.region, max_results=max_results)
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("body", ""),
                "source": item.get("source", ""),
                "date": item.get("date", ""),
            }
            for item in results
        ]
