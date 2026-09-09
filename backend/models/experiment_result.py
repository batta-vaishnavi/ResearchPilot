from pydantic import BaseModel, Field


class ExperimentResult(BaseModel):
    model_name: str

    # Regression metrics
    mae: float | None = None
    rmse: float | None = None
    r2: float | None = None

    # Classification metrics
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    roc_auc: float | None = None


class ExperimentRunRequest(BaseModel):
    research_question: str = Field(
        min_length=10,
        max_length=2000,
    )

    dataset_id: str = Field(
        min_length=1,
    )

    dataset_name: str = Field(
        min_length=1,
    )

    target_column: str = Field(
        min_length=1,
    )

    task_type: str = Field(
        min_length=1,
    )


class ExperimentRunResponse(BaseModel):
    success: bool

    research_question: str | None = None

    dataset_id: str
    dataset_name: str | None = None

    target_column: str | None = None

    task_type: str | None = None

    train_rows: int | None = None
    test_rows: int | None = None

    results: list[ExperimentResult] = Field(
        default_factory=list,
    )

    best_model: str | None = None

    selection_metric: str = "F1"

    status: str

    error: str | None = None