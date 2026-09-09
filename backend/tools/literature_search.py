"""Semantic Scholar implementation of ResearchPilot's literature-search tool."""

import httpx

from backend.models.literature import LiteratureSearchResult, Paper


class LiteratureSearchTool:
    """Search public academic papers without requiring an application API key."""

    name = "semantic_scholar_literature_search"
    provider_name = "Semantic Scholar"
    _search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    _fields = "title,authors,abstract,year,url,citationCount"

    def search(self, query: str, max_papers: int = 5) -> LiteratureSearchResult:
        max_papers = max(1, min(max_papers, 10))
        try:
            response = httpx.get(
                self._search_url,
                params={"query": query, "limit": max_papers, "fields": self._fields},
                headers={"User-Agent": "ResearchPilot/0.2"},
                timeout=10.0,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            return LiteratureSearchResult(
                query=query,
                success=False,
                error=f"Semantic Scholar search failed: {error}",
            )

        papers = [
            Paper(
                title=item.get("title") or "Untitled paper",
                authors=[author["name"] for author in item.get("authors", []) if author.get("name")],
                abstract=item.get("abstract"),
                year=item.get("year"),
                paper_url=item.get("url"),
                citation_count=item.get("citationCount"),
                source_id=item.get("paperId"),
            )
            for item in payload.get("data", [])
        ]
        return LiteratureSearchResult(
            query=query,
            papers=papers,
            total_results=payload.get("total", len(papers)),
            source=self.provider_name,
        )
