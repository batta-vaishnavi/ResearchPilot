import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.models.research_report import (
    ResearchReport,
    ResearchReportAgentState,
    ResearchReportResponse,
)

load_dotenv()


class ResearchReportAgent:
    """Generate a final research report from the completed ResearchPilot pipeline."""

    name = "gemini_research_report"

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        self.client = (
            genai.Client(api_key=api_key)
            if api_key
            else None
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

    def generate(
        self,
        research_question: str,
        research_plan: dict,
        literature: dict,
        dataset_inspection: dict,
        experiment_results: list[dict],
        experiment_analysis: dict,
        best_model: str,
    ) -> ResearchReportResponse:

        if not self.client:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        prompt = f"""
You are ResearchPilot's final research report agent.

Create a structured research report using ONLY the supplied
research artifacts.

Do not invent:
- experiments
- datasets
- papers
- metrics
- statistical significance
- feature importance
- causal relationships
- results that are not present in the supplied artifacts

Clearly distinguish observed experimental results from
future recommendations.

Research Question:
{research_question}

Research Plan:
{research_plan}

Literature Findings:
{literature}

Dataset Inspection:
{dataset_inspection}

Experiment Results:
{experiment_results}

Experiment Analysis:
{experiment_analysis}

Best Model:
{best_model}

Create a concise but complete final research report containing:

1. A meaningful title.
2. The research question.
3. Research objective.
4. Research hypothesis.
5. Literature summary.
6. Dataset summary.
7. Methodology.
8. Models evaluated.
9. Results summary.
10. Best model.
11. Key findings.
12. Limitations.
13. Future work.
14. Final conclusion.

Important:
- Use exact reported experiment metrics.
- Do not claim the model is highly accurate unless supported.
- Do not claim causation.
- If literature information is unavailable, explicitly state that
  the supplied literature artifact did not provide enough evidence.
- If some information is missing from the supplied artifacts,
  do not fabricate it.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResearchReport,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty research-report response."
            )

        report = ResearchReport.model_validate_json(
            response.text
        )

        return ResearchReportResponse(
            success=True,
            report=report,
            agent_state=ResearchReportAgentState(
                current_goal=research_question,
                current_action=(
                    "Generating the final research report "
                    "from completed research artifacts."
                ),
                tool_used=self.name,
                decision=(
                    "Compiled the available research planning, "
                    "dataset, experiment, and analysis results "
                    "into a final research report."
                ),
                next_action=(
                    "Review the final report and identify "
                    "whether additional experiments are required."
                ),
                status="completed",
            ),
            status="completed",
        )