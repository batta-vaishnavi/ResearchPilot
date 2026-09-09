"""Inspect an OpenML dataset and return factual schema and quality information."""

from __future__ import annotations

from typing import Any

import openml


class DatasetInspector:
    """Retrieve and inspect an OpenML dataset without using an LLM."""

    name = "openml_dataset_inspector"
    provider_name = "OpenML"

    def inspect(self, dataset_id: str) -> dict[str, Any]:
        """Inspect an OpenML dataset using its dataset ID."""

        try:
            # ---------------------------------------------------------
            # 1. Download dataset metadata and data
            # ---------------------------------------------------------

            dataset = openml.datasets.get_dataset(
                int(dataset_id),
                download_data=True,
                download_qualities=True,
                download_features_meta_data=True,
            )

            # Get the complete dataframe.
            # We intentionally do NOT pass dataset.default_target_attribute
            # here because some OpenML datasets do not provide one.
            data, targets, categorical_indicator, attribute_names = (
                dataset.get_data(
                    dataset_format="dataframe",
                    target=None,
                )
            )

            if data is None:
                raise ValueError("OpenML returned no dataframe.")

            data = data.copy()

            # ---------------------------------------------------------
            # 2. Basic dimensions
            # ---------------------------------------------------------

            row_count = int(data.shape[0])
            column_count = int(data.shape[1])

            column_names = [
                str(column)
                for column in data.columns
            ]

            # ---------------------------------------------------------
            # 3. Missing values
            # ---------------------------------------------------------

            missing_values = {
                str(column): int(data[column].isna().sum())
                for column in data.columns
                if int(data[column].isna().sum()) > 0
            }

            total_missing = sum(missing_values.values())

            # ---------------------------------------------------------
            # 4. Duplicate rows
            # ---------------------------------------------------------

            duplicate_rows = int(
                data.duplicated().sum()
            )

            # ---------------------------------------------------------
            # 5. Numerical columns
            # ---------------------------------------------------------

            numerical_columns = [
                str(column)
                for column in data.select_dtypes(
                    include=["number"]
                ).columns
            ]

            # ---------------------------------------------------------
            # 6. Categorical columns
            # ---------------------------------------------------------

            categorical_columns = [
                str(column)
                for column in data.select_dtypes(
                    include=["object", "category", "bool"]
                ).columns
            ]

            # ---------------------------------------------------------
            # 7. Detect target column
            # ---------------------------------------------------------

            target_column = self._detect_target_column(
                dataset=dataset,
                data=data,
                targets=targets,
            )

            # ---------------------------------------------------------
            # 8. Quality assessment
            # ---------------------------------------------------------

            quality_issues: list[str] = []

            if row_count == 0:
                quality_issues.append(
                    "Dataset contains no rows."
                )

            if column_count == 0:
                quality_issues.append(
                    "Dataset contains no columns."
                )

            if total_missing > 0:
                quality_issues.append(
                    f"Dataset contains {total_missing} missing values."
                )

            if duplicate_rows > 0:
                quality_issues.append(
                    f"Dataset contains {duplicate_rows} duplicate rows."
                )

            if not target_column:
                quality_issues.append(
                    "No target column could be identified from OpenML metadata."
                )

            # ---------------------------------------------------------
            # 9. Determine ML suitability
            # ---------------------------------------------------------

            suitable = (
                row_count > 0
                and column_count > 1
                and bool(target_column)
                and target_column in column_names
            )

            # ---------------------------------------------------------
            # 10. Determine task type
            # ---------------------------------------------------------

            task_type = self._detect_task_type(
                data=data,
                target_column=target_column,
            )

            # ---------------------------------------------------------
            # 11. Return inspection result
            # ---------------------------------------------------------

            return {
                "success": True,
                "dataset_id": str(dataset_id),
                "dataset_name": dataset.name,
                "description": getattr(
                    dataset,
                    "description",
                    None,
                ),

                "row_count": row_count,
                "column_count": column_count,
                "column_names": column_names,

                "numerical_columns": numerical_columns,
                "categorical_columns": categorical_columns,

                "missing_values": missing_values,
                "total_missing_values": total_missing,

                "duplicate_rows": duplicate_rows,

                "target_column": target_column,
                "target_available": bool(target_column),

                "task_type": task_type,

                "quality_issues": quality_issues,
                "suitable_for_ml": suitable,

                "default_target_attribute": getattr(
                    dataset,
                    "default_target_attribute",
                    None,
                ),

                "source": self.provider_name,
            }

        except Exception as error:

            return {
                "success": False,

                "dataset_id": str(dataset_id),
                "dataset_name": None,
                "description": None,

                "row_count": None,
                "column_count": None,
                "column_names": [],

                "numerical_columns": [],
                "categorical_columns": [],

                "missing_values": {},
                "total_missing_values": None,

                "duplicate_rows": None,

                "target_column": None,
                "target_available": False,

                "task_type": None,

                "quality_issues": [],

                "suitable_for_ml": False,

                "default_target_attribute": None,

                "source": self.provider_name,

                "error": (
                    f"OpenML dataset inspection failed: {error}"
                ),
            }

    # =============================================================
    # TARGET DETECTION
    # =============================================================

    @staticmethod
    def _detect_target_column(
        dataset,
        data,
        targets,
    ) -> str | None:
        """
        Detect the target column using OpenML metadata first,
        then the returned target object, then feature metadata.
        """

        column_names = [
            str(column)
            for column in data.columns
        ]

        # ---------------------------------------------------------
        # Method 1: OpenML default target
        # ---------------------------------------------------------

        default_target = getattr(
            dataset,
            "default_target_attribute",
            None,
        )

        if default_target:
            # OpenML can sometimes return multiple targets
            if isinstance(default_target, str):
                candidates = [
                    item.strip()
                    for item in default_target.split(",")
                ]

                for candidate in candidates:
                    if candidate in column_names:
                        return candidate

        # ---------------------------------------------------------
        # Method 2: Returned targets object
        # ---------------------------------------------------------

        if targets is not None:

            # Pandas Series
            if hasattr(targets, "name"):
                target_name = targets.name

                if (
                    target_name is not None
                    and str(target_name) in column_names
                ):
                    return str(target_name)

            # Pandas DataFrame
            if hasattr(targets, "columns"):
                target_columns = list(
                    targets.columns
                )

                for target in target_columns:
                    if str(target) in column_names:
                        return str(target)

        # ---------------------------------------------------------
        # Method 3: OpenML feature metadata
        # ---------------------------------------------------------

        try:
            features = getattr(
                dataset,
                "features",
                None,
            )

            if features:

                if hasattr(features, "values"):
                    feature_values = features.values()
                else:
                    feature_values = features

                for feature in feature_values:

                    is_target = getattr(
                        feature,
                        "is_target",
                        False,
                    )

                    feature_name = getattr(
                        feature,
                        "name",
                        None,
                    )

                    if (
                        is_target
                        and feature_name
                        and str(feature_name) in column_names
                    ):
                        return str(feature_name)

        except Exception:
            pass

        # ---------------------------------------------------------
        # Method 4: Look for clearly named target columns.
        #
        # This is only used when the name itself strongly indicates
        # a target. We do NOT blindly choose the last column.
        # ---------------------------------------------------------

        target_names = [
            "target",
            "label",
            "class",
            "y",
            "outcome",
            "score",
            "grade",
            "final_grade",
            "final_score",
            "performance",
            "academic_performance",
        ]

        normalized_columns = {
            str(column).lower().strip(): str(column)
            for column in column_names
        }

        for target_name in target_names:

            if target_name in normalized_columns:
                return normalized_columns[target_name]

        # ---------------------------------------------------------
        # Nothing reliable found
        # ---------------------------------------------------------

        return None

    # =============================================================
    # TASK DETECTION
    # =============================================================

    @staticmethod
    def _detect_task_type(
        data,
        target_column: str | None,
    ) -> str | None:
        """Determine whether the target looks like regression or classification."""

        if not target_column:
            return None

        if target_column not in data.columns:
            return None

        target = data[target_column]

        # Boolean / categorical targets -> classification
        if (
            str(target.dtype) == "bool"
            or str(target.dtype) == "object"
            or str(target.dtype) == "category"
        ):
            return "classification"

        # Numeric target
        if hasattr(target, "nunique"):

            unique_values = int(
                target.dropna().nunique()
            )

            total_values = int(
                target.dropna().shape[0]
            )

            if total_values == 0:
                return None

            # Very small number of unique numeric values
            # generally indicates classification.
            if unique_values <= 10:
                return "classification"

            return "regression"

        return None