from pydantic import BaseModel, Field


class ExperimentAnalysisRequest(BaseModel):
    """Request model for experiment-result analysis."""

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

    results: list[dict] = Field(
        min_length=1,
    )

    best_model: str = Field(
        min_length=1,
    )


class ExperimentAnalysis(BaseModel):
    """Structured analysis generated from actual experiment results."""

    summary: str

    best_model: str

    key_findings: list[str] = Field(
        default_factory=list,
    )

    interpretation: str

    limitations: list[str] = Field(
        default_factory=list,
    )

    recommendations: list[str] = Field(
        default_factory=list,
    )


class ExperimentAnalysisAgentState(BaseModel):
    """Track the current state of the experiment-analysis agent."""

    current_goal: str

    current_action: str

    tool_used: str | None = None

    decision: str

    next_action: str

    status: str


class ExperimentAnalysisResponse(BaseModel):
    """Complete response returned by the experiment-analysis agent."""

    success: bool

    research_question: str

    dataset_id: str

    dataset_name: str

    analysis: ExperimentAnalysis

    agent_state: ExperimentAnalysisAgentState

    status: str

    error: str | None = None