from pydantic import BaseModel, Field


class ExperimentModel(BaseModel):
    name: str
    model_type: str
    purpose: str
    expected_use: str


class ExperimentMetric(BaseModel):
    name: str
    purpose: str


class ExperimentPlanRequest(BaseModel):
    research_question: str = Field(
        min_length=10,
        max_length=2000,
        description="The original research question.",
    )

    dataset_id: str = Field(
        min_length=1,
        description="Selected OpenML dataset ID.",
    )

    dataset_name: str = Field(
        min_length=1,
        description="Selected dataset name.",
    )

    target_column: str = Field(
        min_length=1,
        description="Target column for prediction.",
    )

    task_type: str = Field(
        min_length=1,
        description="Machine learning task type, such as regression or classification.",
    )

    numerical_columns: list[str] = Field(
        default_factory=list,
    )

    categorical_columns: list[str] = Field(
        default_factory=list,
    )

    prepared_feature_count: int | None = None


class ExperimentPlan(BaseModel):
    research_question: str

    dataset_id: str
    dataset_name: str

    target_column: str
    task_type: str

    models: list[ExperimentModel] = Field(
        default_factory=list,
    )

    metrics: list[ExperimentMetric] = Field(
        default_factory=list,
    )

    validation_strategy: str

    preprocessing_summary: list[str] = Field(
        default_factory=list,
    )

    experiment_steps: list[str] = Field(
        default_factory=list,
    )

    baseline_model: str | None = None

    recommended_model: str | None = None

    rationale: str

    status: str = "planned"


class ExperimentPlanResponse(BaseModel):
    success: bool

    plan: ExperimentPlan | None = None

    agent_state: dict = Field(
        default_factory=dict,
    )

    status: str

    error: str | None = None