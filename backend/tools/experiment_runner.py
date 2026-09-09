"""Execute machine-learning experiments on an OpenML dataset."""

from __future__ import annotations

import openml

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression,
)
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class ExperimentRunner:
    """Train and compare models based on the detected task type."""

    RANDOM_STATE = 42
    TEST_SIZE = 0.2

    def run(
        self,
        dataset_id: str,
        target_column: str,
        task_type: str = "classification",
    ) -> dict:

        try:
            task_type = task_type.lower().strip()

            if task_type not in {
                "classification",
                "regression",
            }:
                task_type = "classification"

            # --------------------------------------------------
            # LOAD DATASET
            # --------------------------------------------------

            dataset = openml.datasets.get_dataset(
                int(dataset_id),
                download_data=True,
            )

            X, y, _, _ = dataset.get_data(
                target=target_column,
                dataset_format="dataframe",
            )

            if X is None or y is None:
                raise ValueError(
                    "OpenML did not return usable feature and target data."
                )

            # --------------------------------------------------
            # REMOVE TARGET-LEAKAGE COLUMNS
            # --------------------------------------------------

            leakage_columns = []

            target_lower = target_column.lower()

            for column in X.columns:

                column_lower = str(column).lower()

                # Direct copy of the target
                if column_lower == target_lower:
                    leakage_columns.append(column)
                    continue

                # Diabetes-130-Hospitals specific leakage.
                #
                # readmit_30_days is derived from readmission
                # information. Keeping the original readmission
                # label would allow the model to see the answer.
                if (
                    target_lower == "readmit_30_days"
                    and column_lower in {
                        "readmitted",
                        "readmission",
                        "readmission_status",
                    }
                ):
                    leakage_columns.append(column)

            if leakage_columns:
                X = X.drop(
                    columns=leakage_columns,
                    errors="ignore",
                )

            # --------------------------------------------------
            # REMOVE COMPLETELY EMPTY COLUMNS
            # --------------------------------------------------

            empty_columns = [
                column
                for column in X.columns
                if X[column].isna().all()
            ]

            if empty_columns:
                X = X.drop(
                    columns=empty_columns,
                    errors="ignore",
                )

            if X.shape[1] == 0:
                raise ValueError(
                    "No usable feature columns remain after preprocessing."
                )

            # --------------------------------------------------
            # FEATURE TYPES
            # --------------------------------------------------

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
                        SimpleImputer(
                            strategy="most_frequent"
                        ),
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

            transformers = []

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
            )

            # --------------------------------------------------
            # TRAIN / TEST SPLIT
            # --------------------------------------------------

            stratify = None

            if task_type == "classification":

                # Stratification can fail when a class has
                # only one example.
                class_counts = y.value_counts()

                if (
                    len(class_counts) > 1
                    and class_counts.min() >= 2
                ):
                    stratify = y

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=self.TEST_SIZE,
                random_state=self.RANDOM_STATE,
                stratify=stratify,
            )

            # ==================================================
            # CLASSIFICATION
            # ==================================================

            if task_type == "classification":

                models = {
                    "Logistic Regression": LogisticRegression(
                        max_iter=1000,
                        random_state=self.RANDOM_STATE,
                    ),

                    "Random Forest Classifier": RandomForestClassifier(
                        n_estimators=150,
                        random_state=self.RANDOM_STATE,
                        n_jobs=-1,
                    ),

                    "Gradient Boosting Classifier": GradientBoostingClassifier(
                        random_state=self.RANDOM_STATE,
                    ),
                }

                results = []

                for model_name, model in models.items():

                    pipeline = Pipeline(
                        steps=[
                            (
                                "preprocessor",
                                preprocessor,
                            ),
                            (
                                "model",
                                model,
                            ),
                        ]
                    )

                    pipeline.fit(
                        X_train,
                        y_train,
                    )

                    predictions = pipeline.predict(
                        X_test
                    )

                    accuracy = accuracy_score(
                        y_test,
                        predictions,
                    )

                    precision = precision_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0,
                    )

                    recall = recall_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0,
                    )

                    f1 = f1_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0,
                    )

                    # --------------------------------------------------
                    # ROC-AUC
                    # --------------------------------------------------

                    roc_auc = None

                    try:

                        probabilities = (
                            pipeline.predict_proba(X_test)
                        )

                        if probabilities.shape[1] == 2:

                            roc_auc = roc_auc_score(
                                y_test,
                                probabilities[:, 1],
                            )

                        else:

                            roc_auc = roc_auc_score(
                                y_test,
                                probabilities,
                                multi_class="ovr",
                            )

                    except Exception:
                        roc_auc = None

                    results.append(
                        {
                            "model_name": model_name,

                            "accuracy": round(
                                float(accuracy),
                                4,
                            ),

                            "precision": round(
                                float(precision),
                                4,
                            ),

                            "recall": round(
                                float(recall),
                                4,
                            ),

                            "f1": round(
                                float(f1),
                                4,
                            ),

                            "roc_auc": (
                                round(
                                    float(roc_auc),
                                    4,
                                )
                                if roc_auc is not None
                                else None
                            ),
                        }
                    )

                if not results:
                    raise ValueError(
                        "No classification models produced results."
                    )

                # Higher F1 is better.
                best_result = max(
                    results,
                    key=lambda item: item["f1"],
                )

                return {
                    "success": True,

                    "dataset_id": dataset_id,

                    "dataset_name": getattr(
                        dataset,
                        "name",
                        None,
                    ),

                    "target_column": target_column,

                    "task_type": "classification",

                    "train_rows": len(X_train),

                    "test_rows": len(X_test),

                    "results": results,

                    "best_model": best_result[
                        "model_name"
                    ],

                    "selection_metric": "F1",

                    "status": "completed",

                    "error": None,
                }

            # ==================================================
            # REGRESSION
            # ==================================================

            models = {
                "Linear Regression": LinearRegression(),

                "Random Forest Regressor": RandomForestRegressor(
                    n_estimators=150,
                    random_state=self.RANDOM_STATE,
                    n_jobs=-1,
                ),

                "Gradient Boosting Regressor": GradientBoostingRegressor(
                    random_state=self.RANDOM_STATE,
                ),
            }

            results = []

            for model_name, model in models.items():

                pipeline = Pipeline(
                    steps=[
                        (
                            "preprocessor",
                            preprocessor,
                        ),
                        (
                            "model",
                            model,
                        ),
                    ]
                )

                pipeline.fit(
                    X_train,
                    y_train,
                )

                predictions = pipeline.predict(
                    X_test
                )

                mae = mean_absolute_error(
                    y_test,
                    predictions,
                )

                rmse = mean_squared_error(
                    y_test,
                    predictions,
                ) ** 0.5

                r2 = r2_score(
                    y_test,
                    predictions,
                )

                results.append(
                    {
                        "model_name": model_name,

                        "mae": round(
                            float(mae),
                            4,
                        ),

                        "rmse": round(
                            float(rmse),
                            4,
                        ),

                        "r2": round(
                            float(r2),
                            4,
                        ),
                    }
                )

            if not results:
                raise ValueError(
                    "No regression models produced results."
                )

            # Lower RMSE is better.
            best_result = min(
                results,
                key=lambda item: item["rmse"],
            )

            return {
                "success": True,

                "dataset_id": dataset_id,

                "dataset_name": getattr(
                    dataset,
                    "name",
                    None,
                ),

                "target_column": target_column,

                "task_type": "regression",

                "train_rows": len(X_train),

                "test_rows": len(X_test),

                "results": results,

                "best_model": best_result[
                    "model_name"
                ],

                "selection_metric": "RMSE",

                "status": "completed",

                "error": None,
            }

        except Exception as error:

            return {
                "success": False,

                "dataset_id": dataset_id,

                "dataset_name": None,

                "target_column": target_column,

                "task_type": task_type,

                "train_rows": None,

                "test_rows": None,

                "results": [],

                "best_model": None,

                "selection_metric": (
                    "F1"
                    if task_type == "classification"
                    else "RMSE"
                ),

                "status": "experiment_failed",

                "error": str(error),
            }