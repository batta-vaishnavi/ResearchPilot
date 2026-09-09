from pydantic import BaseModel, Field


class DatasetPreparationRequest(BaseModel):
    dataset_id: str = Field(
        min_length=1,
        description="OpenML dataset ID to prepare.",
    )
    target_column: str | None = Field(
        default=None,
        description="Target column. If omitted, the dataset's default target is used.",
    )


class DatasetPreparationResult(BaseModel):
    success: bool

    dataset_id: str
    dataset_name: str | None = None

    target_column: str | None = None
    task_type: str | None = None

    row_count: int | None = None
    original_feature_count: int | None = None

    numerical_columns: list[str] = Field(default_factory=list)
    categorical_columns: list[str] = Field(default_factory=list)

    missing_values_before: int = 0
    missing_values_after: int = 0

    train_rows: int | None = None
    test_rows: int | None = None

    prepared_feature_count: int | None = None

    preprocessing_steps: list[str] = Field(default_factory=list)

    suitable_for_ml: bool = False

    status: str
    error: str | None = None