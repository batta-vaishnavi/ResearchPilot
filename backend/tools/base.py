"""Shared contract for literature providers."""

from typing import Protocol

from backend.models.literature import LiteratureSearchResult


class LiteratureSearchProvider(Protocol):
    name: str
    provider_name: str

    def search(self, query: str, max_papers: int = 5) -> LiteratureSearchResult: ...
