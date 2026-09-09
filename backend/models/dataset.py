from pydantic import BaseModel, Field


class DatasetCandidate(BaseModel):
    dataset_id: str
    name: str
    description: str | None = None
    url: str
    number_of_instances: int | None = None
    number_of_features: int | None = None
    target_information: str | None = None
    format: str | None = None
    source: str = "OpenML"


class DatasetSearchResult(BaseModel):
    query: str
    datasets: list[DatasetCandidate] = Field(default_factory=list)
    source: str = "OpenML"
    success: bool = True
    error: str | None = None


class DatasetEvaluation(BaseModel):
    dataset_id: str
    dataset_name: str
    relevance_score: int = Field(ge=0, le=100, description="How well the dataset matches the research question.")
    size_score: int = Field(ge=0, le=100, description="Suitability of the reported instance count for ML work.")
    feature_score: int = Field(ge=0, le=100, description="Suitability of the reported feature count.")
    target_score: int = Field(ge=0, le=100, description="Whether supplied metadata includes a usable target.")
    ml_suitability_score: int = Field(ge=0, le=100, description="Overall fit for supervised machine learning given supplied metadata.")
    overall_score: int = Field(ge=0, le=100, description="Weighted overall suitability score.")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str


class DatasetSelection(BaseModel):
    selected_dataset_id: str
    selected_dataset_name: str
    selection_reason: str
    next_action: str


class DatasetEvaluationLLMResult(BaseModel):
    """Gemini structured output for candidate comparison. Agent state is filled after the call."""

    evaluations: list[DatasetEvaluation] = Field(default_factory=list)
    selection: DatasetSelection | None = None


class DatasetAgentState(BaseModel):
    current_goal: str
    current_action: str
    tool_used: str | None = None
    decision: str
    next_action: str
    status: str


class DatasetEvaluationRequest(BaseModel):
    research_question: str = Field(min_length=10, max_length=2_000, description="The original research question.")
    datasets: list[DatasetCandidate] = Field(min_length=1, description="OpenML candidates to evaluate.")


class DatasetEvaluationResponse(BaseModel):
    query: str
    evaluations: list[DatasetEvaluation] = Field(default_factory=list)
    selection: DatasetSelection | None = None
    agent_state: DatasetAgentState
    status: str
    error: str | None = None

class DatasetInspectionRequest(BaseModel):
    dataset_id: str = Field(
        min_length=1,
        description="OpenML dataset ID to inspect.",
    )


class DatasetInspectionResult(BaseModel):
    success: bool
    dataset_id: str
    dataset_name: str | None = None
    description: str | None = None

    row_count: int | None = None
    column_count: int | None = None

    column_names: list[str] = Field(default_factory=list)
    numerical_columns: list[str] = Field(default_factory=list)
    categorical_columns: list[str] = Field(default_factory=list)

    missing_values: dict[str, int] = Field(default_factory=dict)
    total_missing_values: int | None = None
    duplicate_rows: int | None = None

    target_column: str | None = None
    target_available: bool = False

    quality_issues: list[str] = Field(default_factory=list)
    suitable_for_ml: bool = False

    default_target_attribute: str | None = None
    source: str = "OpenML"

    error: str | None = None