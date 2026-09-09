from pydantic import BaseModel, Field


class ResearchReportRequest(BaseModel):
    research_question: str = Field(
        min_length=10,
        max_length=2000,
    )

    research_plan: dict

    literature: dict

    dataset_inspection: dict

    experiment_results: list[dict]

    experiment_analysis: dict

    best_model: str


class ResearchReport(BaseModel):
    title: str

    research_question: str

    objective: str

    hypothesis: str

    literature_summary: str

    dataset_summary: str

    methodology: list[str] = Field(
        default_factory=list,
    )

    models_evaluated: list[str] = Field(
        default_factory=list,
    )

    results_summary: str

    best_model: str

    key_findings: list[str] = Field(
        default_factory=list,
    )

    limitations: list[str] = Field(
        default_factory=list,
    )

    future_work: list[str] = Field(
        default_factory=list,
    )

    conclusion: str


class ResearchReportAgentState(BaseModel):
    current_goal: str

    current_action: str

    tool_used: str | None = None

    decision: str

    next_action: str

    status: str


class ResearchReportResponse(BaseModel):
    success: bool

    report: ResearchReport

    agent_state: ResearchReportAgentState

    status: str

    error: str | None = None