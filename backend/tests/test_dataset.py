import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.dataset import DatasetSearchResult
from backend.tools.dataset_search import DatasetSearchTool


IRIS_RECORD = {
    "did": 61,
    "name": "iris",
    "format": "ARFF",
    "default_target_attribute": "class",
    "NumberOfInstances": 150.0,
    "NumberOfFeatures": 5.0,
    "description": "Classic iris flower classification dataset",
}


class DatasetSearchToolTests(unittest.TestCase):
    @patch("backend.tools.dataset_search.openml.datasets.list_datasets")
    def test_successful_openml_search(self, mock_list_datasets):
        mock_list_datasets.return_value = {61: IRIS_RECORD}

        result = DatasetSearchTool().search("iris classification")

        self.assertTrue(result.success)
        self.assertEqual(result.datasets[0].dataset_id, "61")
        self.assertEqual(result.datasets[0].number_of_instances, 150)
        self.assertEqual(result.datasets[0].target_information, "class")

    @patch("backend.tools.dataset_search.openml.datasets.list_datasets")
    def test_empty_openml_results(self, mock_list_datasets):
        mock_list_datasets.return_value = {}

        result = DatasetSearchTool().search("unknown data")

        self.assertTrue(result.success)
        self.assertEqual(result.datasets, [])

    @patch("backend.tools.dataset_search.openml.datasets.list_datasets", side_effect=RuntimeError("offline"))
    def test_openml_api_failure(self, _mock_list_datasets):
        result = DatasetSearchTool().search("iris")

        self.assertFalse(result.success)
        self.assertEqual(result.datasets, [])
        self.assertIn("OpenML dataset search failed", result.error)


class DatasetRouteTests(unittest.TestCase):
    @patch("backend.routes.research.DatasetSearchTool.search")
    def test_response_model_validation(self, mock_search):
        mock_search.return_value = DatasetSearchResult(
            query="iris",
            datasets=[{"dataset_id": "61", "name": "iris", "url": "https://www.openml.org/d/61", "number_of_instances": 150, "number_of_features": 5, "source": "OpenML"}],
        )

        response = TestClient(app).post("/api/research/datasets", json={"research_question": "Find datasets for iris classification"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["datasets"][0]["dataset_id"], "61")


if __name__ == "__main__":
    unittest.main()
