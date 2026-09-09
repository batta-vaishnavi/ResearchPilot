"""Dynamic OpenML dataset discovery tool for ResearchPilot."""

from __future__ import annotations

import re
from typing import Any

import openml

from backend.models.dataset import (
    DatasetCandidate,
    DatasetSearchResult,
)


class DatasetSearchTool:
    """Discover and rank OpenML datasets based on the research question."""

    name = "openml_dataset_search"
    provider_name = "OpenML"

    def search(
        self,
        query: str,
        max_datasets: int = 5,
    ) -> DatasetSearchResult:
        """Search OpenML datasets using terms from the actual research question."""

        max_datasets = max(1, min(max_datasets, 10))
        normalized_query = self._normalize_query(query)

        try:
            # OpenML's catalogue is used as the discovery source.
            raw_data = openml.datasets.list_datasets(
                size=5000
            )

            if raw_data is None:
                return self._empty_result(normalized_query)

            if isinstance(raw_data, dict):
                items = list(raw_data.values())
            else:
                items = raw_data.to_dict("records")

            terms = self._research_terms(query)

            candidates: list[tuple[int, dict[str, Any]]] = []

            for item in items:

                if not isinstance(item, dict):
                    continue

                dataset_id = str(
                    item.get("did")
                    or item.get("id")
                    or ""
                ).strip()

                if not dataset_id:
                    continue

                name = str(
                    item.get("name")
                    or ""
                )

                description = str(
                    item.get("description_160")
                    or item.get("description")
                    or ""
                )

                target = str(
                    item.get("default_target_attribute")
                    or item.get("target_feature")
                    or ""
                )

                text = " ".join(
                    [
                        name,
                        description,
                        target,
                    ]
                ).lower()

                score = self._score_dataset(
                    name=name,
                    description=description,
                    target=target,
                    text=text,
                    terms=terms,
                    item=item,
                )

                if score > 0:
                    candidates.append(
                        (score, item)
                    )

            # Highest relevance first.
            candidates.sort(
                key=lambda pair: pair[0],
                reverse=True,
            )

            datasets: list[DatasetCandidate] = []

            for _, item in candidates:

                if len(datasets) >= max_datasets:
                    break

                dataset_id = str(
                    item.get("did")
                    or item.get("id")
                    or ""
                )

                target_information = (
                    item.get("default_target_attribute")
                    or item.get("target_feature")
                    or item.get("target")
                    or item.get("target_attribute")
                    or item.get("default_target")
                )

                datasets.append(
                    DatasetCandidate(
                        dataset_id=dataset_id,
                        name=str(
                            item.get("name")
                            or "Unnamed dataset"
                        ),
                        description=(
                            item.get("description_160")
                            or item.get("description")
                        ),
                        url=(
                            f"https://www.openml.org/d/"
                            f"{dataset_id}"
                        ),
                        number_of_instances=self._as_int(
                            item.get("NumberOfInstances")
                        ),
                        number_of_features=self._as_int(
                            item.get("NumberOfFeatures")
                        ),
                        target_information=(
                            str(target_information)
                            if target_information
                            else None
                        ),
                        format=item.get("format"),
                    )
                )

            return DatasetSearchResult(
                query=normalized_query,
                datasets=datasets,
                source="OpenML",
                success=True,
                error=None,
            )

        except Exception as error:

            return DatasetSearchResult(
                query=normalized_query,
                datasets=[],
                source="OpenML",
                success=False,
                error=(
                    "OpenML dataset search failed: "
                    f"{error}"
                ),
            )

    # ------------------------------------------------------------------
    # Dataset relevance scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _score_dataset(
        name: str,
        description: str,
        target: str,
        text: str,
        terms: list[str],
        item: dict[str, Any],
    ) -> int:
        """Score a dataset according to the supplied research question.

        IMPORTANT:
        There are NO domain-specific student/education/house-price
        assumptions here. The score is derived from the actual query.
        """

        name_lower = name.lower()
        description_lower = description.lower()
        target_lower = target.lower()

        score = 0

        # --------------------------------------------------------------
        # 1. Exact research-term matches
        # --------------------------------------------------------------

        for term in terms:

            if not term:
                continue

            # Dataset name is the strongest signal.
            if term in name_lower:
                score += 30

            # Target is also highly important.
            if term in target_lower:
                score += 25

            # Description provides weaker evidence.
            if term in description_lower:
                score += 10

        # --------------------------------------------------------------
        # 2. Phrase-level matching
        # --------------------------------------------------------------

        # Compare common multi-word phrases from the question.
        phrase_candidates = DatasetSearchTool._important_phrases(
            terms
        )

        for phrase in phrase_candidates:

            if phrase in name_lower:
                score += 25

            elif phrase in description_lower:
                score += 12

        # --------------------------------------------------------------
        # 3. Target availability
        # --------------------------------------------------------------

        if target.strip():
            score += 8

        # --------------------------------------------------------------
        # 4. Dataset size
        # --------------------------------------------------------------

        instances = DatasetSearchTool._as_int(
            item.get("NumberOfInstances")
        )

        features = DatasetSearchTool._as_int(
            item.get("NumberOfFeatures")
        )

        if instances is not None:

            if instances >= 100:
                score += 3

            if instances >= 500:
                score += 5

            if instances >= 1000:
                score += 3

        if features is not None:

            if features >= 5:
                score += 3

            if features >= 10:
                score += 2

        return score

    # ------------------------------------------------------------------
    # Research-question processing
    # ------------------------------------------------------------------

    @staticmethod
    def _research_terms(
        query: str,
    ) -> list[str]:
        """Extract meaningful terms from the user's research question."""

        words = re.findall(
            r"[A-Za-z0-9]+",
            query.lower(),
        )

        ignored = {
            # Question words
            "can",
            "could",
            "would",
            "should",
            "is",
            "are",
            "was",
            "were",
            "what",
            "how",
            "why",
            "when",
            "where",
            "which",
            "who",

            # Articles / connectors
            "the",
            "a",
            "an",
            "and",
            "or",
            "of",
            "for",
            "from",
            "with",
            "without",
            "into",
            "on",
            "in",
            "to",
            "by",
            "using",

            # Generic ML words
            "machine",
            "learning",
            "model",
            "models",
            "algorithm",
            "algorithms",
            "predict",
            "predicting",
            "prediction",
            "predictions",
            "accurately",
            "accuracy",

            # Generic research words
            "research",
            "study",
            "investigate",
            "investigating",
            "analyze",
            "analysis",
            "dataset",
            "datasets",
            "data",
        }

        terms = [
            word
            for word in words
            if word not in ignored
            and len(word) >= 3
        ]

        # Remove duplicates while preserving order.
        return list(
            dict.fromkeys(terms)
        )

    @staticmethod
    def _important_phrases(
        terms: list[str],
    ) -> list[str]:
        """Build useful two-word phrases from query terms."""

        if len(terms) < 2:
            return []

        phrases = []

        for index in range(
            len(terms) - 1
        ):
            phrase = (
                f"{terms[index]} "
                f"{terms[index + 1]}"
            )

            phrases.append(phrase)

        return phrases

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_query(
        query: str,
    ) -> str:
        """Normalize the query for display/storage."""

        words = re.findall(
            r"[A-Za-z0-9]+",
            query.lower(),
        )

        return " ".join(
            words[:20]
        )

    @staticmethod
    def _as_int(
        value: Any,
    ) -> int | None:
        """Safely convert a value to an integer."""

        try:

            if value is None:
                return None

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _empty_result(
        query: str,
    ) -> DatasetSearchResult:
        """Return an empty but successful search result."""

        return DatasetSearchResult(
            query=query,
            datasets=[],
            source="OpenML",
            success=True,
            error=None,
        )