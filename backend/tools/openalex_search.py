"""OpenAlex fallback implementation of ResearchPilot's literature-search tool."""

import re

import httpx

from backend.models.literature import LiteratureSearchResult, Paper


class OpenAlexSearchTool:
    """Search OpenAlex's public works API and normalize results to Paper."""

    name = "openalex_literature_search"
    provider_name = "OpenAlex"
    _search_url = "https://api.openalex.org/works"

    def search(self, query: str, max_papers: int = 5) -> LiteratureSearchResult:
        max_papers = max(1, min(max_papers, 10))
        normalized_query = re.sub(r"[^\w\s-]", " ", query)
        normalized_query = " ".join(normalized_query.split())
        try:
            response = httpx.get(
                self._search_url,
                params={"search": normalized_query, "per-page": max_papers},
                headers={"User-Agent": "ResearchPilot/0.2"},
                timeout=10.0,
            )
            response.raise_for_status()
            payload = response.json()
            results = payload.get("results", [])
            if not isinstance(results, list):
                raise ValueError("OpenAlex returned an invalid results payload.")
        except (httpx.HTTPError, ValueError) as error:
            return LiteratureSearchResult(
                query=query,
                source=self.provider_name,
                success=False,
                error=f"OpenAlex search failed: {error}",
            )

        papers = [self._normalize_paper(item) for item in results if isinstance(item, dict)]
        return LiteratureSearchResult(
            query=query,
            papers=papers,
            total_results=payload.get("meta", {}).get("count", len(papers)),
            source=self.provider_name,
        )

    @staticmethod
    def _normalize_paper(item: dict) -> Paper:
        location = item.get("primary_location") or {}
        return Paper(
            title=item.get("title") or "Untitled paper",
            authors=[
                authorship.get("author", {}).get("display_name")
                for authorship in item.get("authorships", [])
                if authorship.get("author", {}).get("display_name")
            ],
            abstract=OpenAlexSearchTool._reconstruct_abstract(item.get("abstract_inverted_index")),
            year=item.get("publication_year"),
            paper_url=location.get("landing_page_url") or item.get("doi") or item.get("id"),
            citation_count=item.get("cited_by_count"),
            source_id=item.get("id"),
        )

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
        if not inverted_index:
            return None
        positions = {
            position: word
            for word, indexes in inverted_index.items()
            for position in indexes
        }
        return " ".join(positions[position] for position in sorted(positions))
