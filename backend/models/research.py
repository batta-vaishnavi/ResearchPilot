from pydantic import BaseModel, Field


class ResearchPlanRequest(BaseModel):
    research_question: str = Field(min_length=10, max_length=2_000, description="The research question for the agent to analyze.")


class ResearchPlan(BaseModel):
    research_goal: str = Field(description="The high-level aim of the research.")
    research_objective: str = Field(description="A focused, measurable objective.")
    proposed_hypothesis: str = Field(description="A testable proposed hypothesis.")
    required_steps: list[str] = Field(description="Ordered research steps to take.")
    suggested_experiments: list[str] = Field(description="Candidate experiments to run later.")
    evaluation_metrics: list[str] = Field(description="Metrics appropriate to the plan.")
    current_status: str = Field(description="The current state of the agent's work.")
