import unittest
from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.literature import LiteratureSearchResult
from backend.tools.literature_search import LiteratureSearchTool
from backend.agents.research_orchestrator import ResearchOrchestrator


class LiteratureSearchToolTests(unittest.TestCase):
    @patch("backend.tools.literature_search.httpx.get")
    def test_successful_literature_search(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "total": 1,
            "data": [{"paperId": "paper-1", "title": "Crop Disease Detection", "authors": [{"name": "A. Researcher"}], "abstract": "A paper abstract.", "year": 2024, "url": "https://example.org/paper-1", "citationCount": 12}],
        }
        mock_get.return_value = response

        result = LiteratureSearchTool().search("crop disease detection")

        self.assertTrue(result.success)
        self.assertEqual(result.total_results, 1)
        self.assertEqual(result.papers[0].title, "Crop Disease Detection")
        self.assertEqual(result.papers[0].authors, ["A. Researcher"])

    @patch("backend.tools.literature_search.httpx.get")
    def test_empty_search_results(self, mock_get):
        response = Mock()
        response.json.return_value = {"total": 0, "data": []}
        mock_get.return_value = response

        result = LiteratureSearchTool().search("no matching papers")

        self.assertTrue(result.success)
        self.assertEqual(result.papers, [])
        self.assertEqual(result.total_results, 0)

    @patch("backend.tools.literature_search.httpx.get", side_effect=httpx.ConnectError("offline"))
    def test_external_api_failure(self, _mock_get):
        result = LiteratureSearchTool().search("crop disease detection")

        self.assertFalse(result.success)
        self.assertEqual(result.papers, [])
        self.assertIn("Semantic Scholar search failed", result.error)


class LiteratureRouteTests(unittest.TestCase):
    @patch("backend.agents.research_orchestrator.LiteratureSearchTool.search")
    def test_structured_response_validation(self, mock_search):
        mock_search.return_value = LiteratureSearchResult(
            query="crop disease detection",
            total_results=1,
            papers=[{"title": "Crop Disease Detection", "authors": ["A. Researcher"], "abstract": "The abstract explains the method.", "year": 2024, "paper_url": "https://example.org/paper-1", "citation_count": 12, "source_id": "paper-1"}],
        )
        response = TestClient(app).post("/api/research/literature", json={"research_question": "Can machine learning improve crop disease detection?"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["papers"][0]["source_id"], "paper-1")
        self.assertEqual(body["agent_state"]["tool_used"], "semantic_scholar_literature_search")
        self.assertEqual(body["agent_state"]["status"], "literature_research_completed")

    def test_phase_one_plan_route_remains_registered(self):
        included_router = next(route for route in app.routes if hasattr(route, "original_router"))
        self.assertTrue(any(route.path == "/plan" for route in included_router.original_router.routes))


class FallbackWorkflowTests(unittest.TestCase):
    question = "Can machine learning improve crop disease detection?"

    @staticmethod
    def successful_result(source="Semantic Scholar"):
        return LiteratureSearchResult(
            query=FallbackWorkflowTests.question,
            source=source,
            total_results=1,
            papers=[{"title": "Crop Disease Detection", "authors": ["A. Researcher"], "abstract": "The abstract explains the method.", "year": 2024, "paper_url": "https://example.org/paper-1", "citation_count": 12, "source_id": "paper-1"}],
        )

    @patch("backend.agents.research_orchestrator.OpenAlexSearchTool.search")
    @patch("backend.agents.research_orchestrator.LiteratureSearchTool.search")
    def test_semantic_scholar_success_does_not_use_fallback(self, primary_search, fallback_search):
        primary_search.return_value = self.successful_result()

        response = ResearchOrchestrator().research_literature(self.question)

        self.assertEqual(response.agent_state.tool_used, "semantic_scholar_literature_search")
        self.assertEqual(len(response.agent_state.tool_history), 1)
        fallback_search.assert_not_called()

    @patch("backend.agents.research_orchestrator.OpenAlexSearchTool.search")
    @patch("backend.agents.research_orchestrator.LiteratureSearchTool.search")
    def test_semantic_scholar_429_uses_openalex_fallback(self, primary_search, fallback_search):
        primary_search.return_value = LiteratureSearchResult(query=self.question, success=False, error="Semantic Scholar search failed: HTTP 429 Too Many Requests")
        fallback_search.return_value = self.successful_result(source="OpenAlex")

        response = ResearchOrchestrator().research_literature(self.question)

        self.assertEqual(response.agent_state.tool_used, "openalex_literature_search")
        self.assertEqual(response.agent_state.status, "literature_research_completed")
        self.assertEqual(response.agent_state.adaptation, "Semantic Scholar failed; switched to OpenAlex.")
        self.assertEqual(len(response.agent_state.tool_history), 2)
        self.assertEqual(response.papers[0].title, "Crop Disease Detection")

    @patch("backend.agents.research_orchestrator.OpenAlexSearchTool.search")
    @patch("backend.agents.research_orchestrator.LiteratureSearchTool.search")
    def test_generic_primary_failure_uses_openalex_fallback(self, primary_search, fallback_search):
        primary_search.return_value = LiteratureSearchResult(query=self.question, success=False, error="Semantic Scholar search failed: connection timeout")
        fallback_search.return_value = self.successful_result(source="OpenAlex")

        response = ResearchOrchestrator().research_literature(self.question)

        fallback_search.assert_called_once()
        self.assertEqual(response.agent_state.tool_history[1].provider, "OpenAlex")
        self.assertEqual(response.papers_found, 1)

    @patch("backend.agents.research_orchestrator.OpenAlexSearchTool.search")
    @patch("backend.agents.research_orchestrator.LiteratureSearchTool.search")
    def test_both_provider_failures_return_clean_state_without_papers(self, primary_search, fallback_search):
        primary_search.return_value = LiteratureSearchResult(query=self.question, success=False, error="Semantic Scholar search failed: HTTP 429")
        fallback_search.return_value = LiteratureSearchResult(query=self.question, source="OpenAlex", success=False, error="OpenAlex search failed: connection timeout")

        response = ResearchOrchestrator().research_literature(self.question)

        self.assertEqual(response.agent_state.status, "tool_failed")
        self.assertEqual(response.papers, [])
        self.assertEqual(response.findings, [])
        self.assertEqual(len(response.agent_state.tool_history), 2)


if __name__ == "__main__":
    unittest.main()
