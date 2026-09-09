from pydantic import BaseModel, Field


class ResearchPipelineRequest(BaseModel):
    research_question: str = Field(
        min_length=10,
        max_length=2000,
    )


class ResearchPipelineResponse(BaseModel):
    success: bool
    research_question: str

    plan: dict | None = None
    literature: dict | None = None

    dataset_search: dict | None = None
    dataset_evaluation: dict | None = None
    dataset_inspection: dict | None = None
    dataset_preparation: dict | None = None

    experiment_plan: dict | None = None
    experiment_results: dict | None = None
    experiment_analysis: dict | None = None

    final_report: dict | None = None

    current_stage: str
    completed_stages: list[str] = Field(
        default_factory=list
    )

    error: str | None = None