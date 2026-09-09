"""Prepare an OpenML dataset for downstream machine-learning experiments."""

from __future__ import annotations

from typing import Any

import openml
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from backend.models.dataset_preparation import DatasetPreparationResult


class DatasetPreparer:
    """Load, inspect, and prepare an OpenML dataset for ML experiments."""

    RANDOM_STATE = 42
    TEST_SIZE = 0.2

    def prepare(
        self,
        dataset_id: str,
        target_column: str | None = None,
    ) -> DatasetPreparationResult:

        try:
            dataset = openml.datasets.get_dataset(
                int(dataset_id),
                download_data=True,
            )

            dataset_name = getattr(dataset, "name", None)

            X, y, categorical_indicator, feature_names = dataset.get_data(
                target=target_column,
                dataset_format="dataframe",
            )

            if target_column is None:
                target_column = getattr(dataset, "default_target_attribute", None)

            if target_column is None:
                return DatasetPreparationResult(
                    success=False,
                    dataset_id=dataset_id,
                    dataset_name=dataset_name,
                    status="no_target",
                    suitable_for_ml=False,
                    error="No target column was supplied and OpenML did not provide a default target.",
                )

            if X is None or y is None:
                return DatasetPreparationResult(
                    success=False,
                    dataset_id=dataset_id,
                    dataset_name=dataset_name,
                    target_column=target_column,
                    status="data_unavailable",
                    suitable_for_ml=False,
                    error="OpenML did not return usable feature and target data.",
                )

            numerical_columns = [
                column
                for column in X.columns
                if X[column].dtype.kind in "biufc"
            ]

            categorical_columns = [
                column
                for column in X.columns
                if column not in numerical_columns
            ]

            missing_values_before = int(X.isna().sum().sum())

            # Determine whether this is a classification or regression task.
            task_type = self._infer_task_type(y)

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=self.TEST_SIZE,
                random_state=self.RANDOM_STATE,
            )

            numerical_pipeline = Pipeline(
                steps=[
                    (
                        "imputer",
                        SimpleImputer(strategy="median"),
                    ),
                    (
                        "scaler",
                        StandardScaler(),
                    ),
                ]
            )

            categorical_pipeline = Pipeline(
                steps=[
                    (
                        "imputer",
                        SimpleImputer(strategy="most_frequent"),
                    ),
                    (
                        "encoder",
                        OneHotEncoder(
                            handle_unknown="ignore",
                            sparse_output=False,
                        ),
                    ),
                ]
            )

            transformers: list[tuple[str, Any, list[str]]] = []

            if numerical_columns:
                transformers.append(
                    (
                        "numerical",
                        numerical_pipeline,
                        numerical_columns,
                    )
                )

            if categorical_columns:
                transformers.append(
                    (
                        "categorical",
                        categorical_pipeline,
                        categorical_columns,
                    )
                )

            preprocessor = ColumnTransformer(
                transformers=transformers,
                remainder="drop",
            )

            X_train_prepared = preprocessor.fit_transform(X_train)
            X_test_prepared = preprocessor.transform(X_test)

            prepared_feature_count = int(X_train_prepared.shape[1])

            return DatasetPreparationResult(
                success=True,
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                target_column=target_column,
                task_type=task_type,
                row_count=int(len(X)),
                original_feature_count=int(X.shape[1]),
                numerical_columns=numerical_columns,
                categorical_columns=categorical_columns,
                missing_values_before=missing_values_before,
                missing_values_after=0,
                train_rows=int(len(X_train)),
                test_rows=int(len(X_test)),
                prepared_feature_count=prepared_feature_count,
                preprocessing_steps=[
                    "Separate features and target",
                    "Split data into 80% training and 20% testing sets",
                    "Impute missing numerical values using the median",
                    "Standardize numerical features",
                    "Impute missing categorical values using the most frequent value",
                    "One-hot encode categorical features",
                    "Ignore unseen categorical values during transformation",
                ],
                suitable_for_ml=True,
                status="completed",
            )

        except Exception as error:
            return DatasetPreparationResult(
                success=False,
                dataset_id=dataset_id,
                target_column=target_column,
                status="preparation_failed",
                suitable_for_ml=False,
                error=str(error),
            )

    @staticmethod
    def _infer_task_type(y) -> str:
        """Infer a simple ML task type from the target values."""

        if y.dtype.kind in "biufc":
            unique_count = y.nunique()

            # A small number of integer/boolean target values is usually
            # a classification problem.
            if unique_count <= 10:
                return "classification"

            return "regression"

        return "classification"