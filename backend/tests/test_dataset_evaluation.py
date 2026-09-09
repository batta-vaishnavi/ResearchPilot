import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.agents.dataset_evaluator import DatasetEvaluationAgent
from backend.main import app
from backend.models.dataset import (
    DatasetCandidate,
    DatasetEvaluation,
    DatasetEvaluationLLMResult,
    DatasetEvaluationResponse,
    DatasetSelection,
)


QUESTION = "Can machine learning predict student academic performance?"
CANDIDATES = [
    DatasetCandidate(
        dataset_id="42351",
        name="student_performance_por",
        description="Student Portuguese course performance.",
        url="https://www.openml.org/d/42351",
        number_of_instances=649,
        number_of_features=33,
        target_information="G3",
        format="ARFF",
    ),
    DatasetCandidate(
        dataset_id="45068",
        name="students_scores",
        description="Exam scores for students.",
        url="https://www.openml.org/d/45068",
        number_of_instances=1000,
        number_of_features=8,
        target_information=None,
        format="ARFF",
    ),
]


def evaluation(dataset_id: str, name: str, overall: int, **overrides) -> DatasetEvaluation:
    payload = {
        "dataset_id": dataset_id,
        "dataset_name": name,
        "relevance_score": overall,
        "size_score": 80,
        "feature_score": 75,
        "target_score": 90 if dataset_id == "42351" else 20,
        "ml_suitability_score": overall,
        "overall_score": overall,
        "strengths": ["Relevant to student performance"],
        "weaknesses": ["Limited metadata"],
        "recommendation": "Use as a candidate for supervised learning.",
    }
    payload.update(overrides)
    return DatasetEvaluation.model_validate(payload)


class DatasetEvaluationAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = DatasetEvaluationAgent()
        self.agent.client = object()

    @patch.object(DatasetEvaluationAgent, "_call_gemini")
    def test_multiple_candidates_successful_evaluation(self, mock_gemini):
        mock_gemini.return_value = DatasetEvaluationLLMResult(
            evaluations=[
                evaluation("42351", "student_performance_por", 92),
                evaluation("45068", "students_scores", 70),
            ],
            selection=DatasetSelection(
                selected_dataset_id="42351",
                selected_dataset_name="student_performance_por",
                selection_reason="Strongest relevance and a reported target.",
                next_action="Inspect the selected dataset schema and prepare it for experimentation.",
            ),
        )

        result = self.agent.evaluate(QUESTION, CANDIDATES)

        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.evaluations), 2)
        self.assertEqual(result.selection.selected_dataset_id, "42351")
        self.assertEqual(result.agent_state.tool_used, "gemini_dataset_evaluation")
        self.assertEqual(result.agent_state.status, "completed")
        self.assertIn("student_performance_por", result.agent_state.decision)
        mock_gemini.assert_called_once()

    @patch.object(DatasetEvaluationAgent, "_call_gemini")
    def test_agent_selects_highest_quality_candidate(self, mock_gemini):
        mock_gemini.return_value = DatasetEvaluationLLMResult(
            evaluations=[
                evaluation("42351", "student_performance_por", 91),
                evaluation("45068", "students_scores", 64),
            ],
            selection=DatasetSelection(
                selected_dataset_id="45068",
                selected_dataset_name="students_scores",
                selection_reason="Incorrect lower-scoring choice from the model.",
                next_action="Inspect the selected dataset schema and prepare it for experimentation.",
            ),
        )

        result = self.agent.evaluate(QUESTION, CANDIDATES)

        self.assertEqual(result.selection.selected_dataset_id, "42351")
        self.assertEqual(result.selection.selected_dataset_name, "student_performance_por")
        self.assertEqual(result.evaluations[0].dataset_id, "42351")


class DatasetEvaluationRouteTests(unittest.TestCase):
    def test_empty_candidate_list_is_rejected(self):
        response = TestClient(app).post(
            "/api/research/datasets/evaluate",
            json={"research_question": QUESTION, "datasets": []},
        )

        self.assertEqual(response.status_code, 422)

    @patch("backend.routes.research.DatasetEvaluationAgent.evaluate")
    def test_successful_route_response(self, mock_evaluate):
        mock_evaluate.return_value = DatasetEvaluationResponse(
            query=QUESTION,
            evaluations=[evaluation("42351", "student_performance_por", 92)],
            selection=DatasetSelection(
                selected_dataset_id="42351",
                selected_dataset_name="student_performance_por",
                selection_reason="Best overall fit.",
                next_action="Inspect the selected dataset schema and prepare it for experimentation.",
            ),
            agent_state={
                "current_goal": QUESTION,
                "current_action": "Evaluating OpenML candidate datasets.",
                "tool_used": "gemini_dataset_evaluation",
                "decision": "student_performance_por has the strongest overall fit.",
                "next_action": "Inspect the selected dataset schema and prepare it for experimentation.",
                "status": "completed",
            },
            status="completed",
        )

        response = TestClient(app).post(
            "/api/research/datasets/evaluate",
            json={"research_question": QUESTION, "datasets": [CANDIDATES[0].model_dump()]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["selection"]["selected_dataset_id"], "42351")

    @patch("backend.routes.research.DatasetEvaluationAgent.evaluate", side_effect=RuntimeError("Gemini offline"))
    def test_gemini_failure_returns_clean_error(self, _mock_evaluate):
        response = TestClient(app).post(
            "/api/research/datasets/evaluate",
            json={"research_question": QUESTION, "datasets": [CANDIDATES[0].model_dump()]},
        )

        self.assertEqual(response.status_code, 502)
        self.assertIn("dataset evaluation agent", response.json()["detail"])

    def test_existing_dataset_discovery_route_remains_registered(self):
        paths = set(app.openapi()["paths"].keys())

        self.assertIn("/api/research/datasets", paths)
        self.assertIn("/api/research/datasets/evaluate", paths)
        self.assertIn("/api/research/plan", paths)
        self.assertIn("/api/research/literature", paths)


if __name__ == "__main__":
    unittest.main()
