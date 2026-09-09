"""Agentic analysis of factual OpenML dataset inspection results."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from backend.models.dataset import (
    DatasetAgentState,
    DatasetInspectionResult,
)

load_dotenv()


class InspectionAnalysisLLMResult(BaseModel):
    """Structured Gemini response for dataset inspection analysis."""

    analysis: str
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    recommendation: str
    next_action: str


class DatasetInspectionAgent:
    """Analyze an inspected dataset and decide the next research action."""

    name = "gemini_dataset_inspection_analysis"

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def analyze(
        self,
        research_question: str,
        inspection: DatasetInspectionResult,
    ) -> dict:
        """Analyze factual inspection results without inventing dataset facts."""

        if not inspection.success:
            return {
                "status": "inspection_failed",
                "analysis": (
                    "Dataset inspection failed, so the dataset "
                    "cannot be assessed reliably."
                ),
                "strengths": [],
                "limitations": ["The dataset could not be inspected."],
                "recommendation": (
                    "Inspect the dataset again or choose another dataset."
                ),
                "agent_state": DatasetAgentState(
                    current_goal=research_question,
                    current_action="Analyzing dataset inspection results.",
                    tool_used=self.name,
                    decision="The dataset inspection failed.",
                    next_action=(
                        "Retry dataset inspection or select another dataset."
                    ),
                    status="inspection_failed",
                ),
            }

        if not self.client:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        prompt = f"""
You are ResearchPilot's dataset inspection analysis agent.

Analyze ONLY the factual dataset inspection information supplied below.

Do NOT invent:
- columns
- values
- target variables
- missing values
- model results
- accuracy
- correlations
- statistical findings
- preprocessing results

If information is not supplied, say that it is unavailable.

Original research question:
{research_question}

Actual dataset inspection:
{inspection.model_dump_json(indent=2)}

Your task:

1. Determine whether the inspected dataset is suitable for the research question.
2. Explain the most important strengths.
3. Identify limitations or risks visible from the inspection.
4. Decide the next concrete research action.

Pay particular attention to:
- number of rows
- number of predictor columns
- numerical versus categorical features
- missing values
- duplicate rows
- target availability
- target column
- whether the target appears appropriate based ONLY on the supplied metadata

Do not claim that a machine-learning model has been trained.
Do not claim that preprocessing has been performed.
Do not claim that model performance has been measured.

Return concise, factual reasoning.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InspectionAnalysisLLMResult,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty dataset inspection analysis."
            )

        result = InspectionAnalysisLLMResult.model_validate_json(
            response.text
        )

        return {
            "status": "completed",
            "analysis": result.analysis,
            "strengths": result.strengths,
            "limitations": result.limitations,
            "recommendation": result.recommendation,
            "agent_state": DatasetAgentState(
                current_goal=research_question,
                current_action=(
                    "Analyzing factual dataset inspection results."
                ),
                tool_used=self.name,
                decision=result.recommendation,
                next_action=result.next_action,
                status="completed",
            ),
        }