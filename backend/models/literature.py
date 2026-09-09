from typing import Any

from pydantic import BaseModel, Field


class Paper(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    year: int | None = None
    paper_url: str | None = None
    citation_count: int | None = None
    source_id: str | None = None


class LiteratureSearchResult(BaseModel):
    query: str
    papers: list[Paper] = Field(default_factory=list)
    total_results: int = 0
    source: str = "Semantic Scholar"
    success: bool = True
    error: str | None = None


class LiteratureFinding(BaseModel):
    paper_title: str
    paper_id: str | None = None
    evidence_summary: str


class ToolExecution(BaseModel):
    provider: str
    tool_name: str
    tool_input: dict[str, Any] = Field(default_factory=dict)
    result_summary: str
    status: str


class ResearchState(BaseModel):
    current_goal: str
    current_action: str
    tool_used: str | None = None
    tool_input: dict[str, Any] = Field(default_factory=dict)
    tool_result_summary: str = ""
    decision: str
    next_action: str
    status: str
    adaptation: str | None = None
    tool_history: list[ToolExecution] = Field(default_factory=list)
    literature_findings: list[LiteratureFinding] = Field(default_factory=list)


class LiteratureResearchResponse(BaseModel):
    research_question: str
    papers_found: int = 0
    papers: list[Paper] = Field(default_factory=list)
    findings: list[LiteratureFinding] = Field(default_factory=list)
    agent_state: ResearchState
