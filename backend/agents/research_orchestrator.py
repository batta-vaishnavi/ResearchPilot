"""Goal-analysis agent for the first ResearchPilot milestone."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.models.research import ResearchPlan
from backend.models.literature import (
    LiteratureFinding,
    LiteratureResearchResponse,
    Paper,
    ResearchState,
    ToolExecution,
)
from backend.tools.literature_search import LiteratureSearchTool
from backend.tools.openalex_search import OpenAlexSearchTool

load_dotenv()


class ResearchOrchestrator:
    """Converts one research question into a structured research plan
    and performs the literature-research stage.
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(api_key=api_key) if api_key else None

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

    def create_plan(self, research_question: str) -> ResearchPlan:
        """Create the initial machine-learning research plan."""

        if not self.client:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        prompt = f"""
You are ResearchPilot's planning agent.

Analyze the user's research question and create an initial, practical,
machine-learning research plan.

This milestone only plans work. Do not claim to have searched literature,
found datasets, or run experiments.

IMPORTANT:
- Determine the machine-learning task from the research question.
- Do not arbitrarily convert a regression problem into classification.
- If the question asks to predict a numeric academic score, grade, mark,
  or continuous performance measure, plan a REGRESSION task.
- If the question explicitly asks to predict categories such as pass/fail,
  low/medium/high performance, plan a CLASSIFICATION task.
- Keep the research objective, hypothesis, experiments, and evaluation
  metrics consistent with the selected task.
- For regression, use metrics such as MAE, RMSE, and R².
- For classification, use metrics such as Accuracy, Precision, Recall,
  F1-score, and ROC-AUC.
- Do not assume a specific dataset or target column before dataset
  discovery and inspection.
- Do not invent a target variable such as G3 unless it has actually been
  discovered during a later dataset-inspection stage.
- The plan should remain general enough to work with different datasets
  that may be discovered for the research question.

For questions about predicting student academic performance, if the
research question does not explicitly specify pass/fail or another
category, prefer a regression-oriented research plan because academic
performance can be represented by a numeric grade or score.

Be specific, concise, and transparent about proposed work.

Research question:
{research_question}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResearchPlan,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty planning response."
            )

        return ResearchPlan.model_validate_json(response.text)

    def research_literature(
        self,
        research_question: str,
        max_papers: int = 5,
    ) -> LiteratureResearchResponse:
        """Run the literature-research stage.

        The user's research question is converted into a focused academic
        search query so that providers return papers relevant to the
        research domain instead of treating the question as a generic
        natural-language search.
        """

        max_papers = max(1, min(max_papers, 10))

        state = ResearchState(
            current_goal=research_question,
            current_action=(
                "Deciding whether literature research is needed."
            ),
            decision=(
                "Literature research is required to ground the "
                "research plan in published evidence."
            ),
            next_action=(
                "Search Semantic Scholar for relevant papers."
            ),
            status="tool_selected",
        )

        # ---------------------------------------------------------
        # Build a focused academic literature query.
        # ---------------------------------------------------------
        literature_query = self._build_literature_query(
            research_question
        )

        primary_tool = LiteratureSearchTool()

        tool_input = {
            "query": literature_query,
            "max_papers": max_papers,
        }

        search_result = primary_tool.search(
            literature_query,
            max_papers=max_papers,
        )

        state.tool_used = primary_tool.name
        state.tool_input = tool_input

        state.tool_history.append(
            self._tool_execution(
                primary_tool,
                tool_input,
                search_result,
            )
        )

        # ---------------------------------------------------------
        # Semantic Scholar failed -> use OpenAlex fallback.
        # ---------------------------------------------------------
        if not search_result.success:
            state.current_action = (
                "Observed the primary literature-search tool failure."
            )

            state.tool_result_summary = (
                search_result.error
                or "Semantic Scholar search failed."
            )

            state.decision = (
                "Primary literature search failed; "
                "switching to fallback provider."
            )

            state.next_action = (
                "Search OpenAlex for relevant academic papers."
            )

            state.status = "fallback_selected"

            state.adaptation = (
                "Semantic Scholar failed; switched to OpenAlex."
            )

            fallback_tool = OpenAlexSearchTool()

            fallback_result = fallback_tool.search(
                literature_query,
                max_papers=max_papers,
            )

            fallback_tool_input = {
                "query": literature_query,
                "max_papers": max_papers,
            }

            state.tool_used = fallback_tool.name
            state.tool_input = fallback_tool_input

            state.tool_history.append(
                self._tool_execution(
                    fallback_tool,
                    fallback_tool_input,
                    fallback_result,
                )
            )

            search_result = fallback_result

            if not fallback_result.success:
                state.current_action = (
                    "Observed that both literature-search "
                    "providers failed."
                )

                state.tool_result_summary = (
                    f"Primary: "
                    f"{state.tool_history[0].result_summary} "
                    f"Fallback: "
                    f"{fallback_result.error or 'OpenAlex search failed.'}"
                )

                state.decision = (
                    "Neither provider returned source material; "
                    "do not create findings."
                )

                state.next_action = (
                    "Retry later or refine the research question."
                )

                state.status = "tool_failed"

                return LiteratureResearchResponse(
                    research_question=research_question,
                    agent_state=state,
                )

        # ---------------------------------------------------------
        # No papers returned.
        # ---------------------------------------------------------
        if not search_result.papers:
            state.current_action = (
                "Observed that the literature search returned no papers."
            )

            state.tool_result_summary = (
                f"{search_result.source} returned zero papers."
            )

            state.decision = (
                "No literature findings can be supported "
                "by the search result."
            )

            state.next_action = (
                "Refine the query with more specific research terms."
            )

            state.status = "completed_no_results"

            return LiteratureResearchResponse(
                research_question=research_question,
                agent_state=state,
            )

        # ---------------------------------------------------------
        # Select the strongest initial papers.
        # ---------------------------------------------------------
        selected_papers = search_result.papers[:3]

        findings = [
            self._create_finding(paper)
            for paper in selected_papers
        ]

        state.current_action = (
            "Reviewed relevance-ranked papers and selected "
            "the strongest initial evidence."
        )

        state.tool_result_summary = (
            f"{search_result.source} returned "
            f"{search_result.total_results} matching papers; "
            f"selected {len(selected_papers)} for review."
        )

        state.decision = (
            "Use the selected papers as initial evidence, "
            "then compare methods and limitations in the "
            "next planning step."
        )

        state.next_action = (
            "Synthesize the selected literature into the research plan."
        )

        state.status = "literature_research_completed"

        state.literature_findings = findings

        return LiteratureResearchResponse(
            research_question=research_question,
            papers_found=search_result.total_results,
            papers=selected_papers,
            findings=findings,
            agent_state=state,
        )

    @staticmethod
    def _build_literature_query(
        research_question: str,
    ) -> str:
        """Create a focused academic search query.

        This keeps the user's original research question while adding
        domain-specific terminology that helps academic search engines
        retrieve relevant papers.
        """

        question_lower = research_question.lower()

        # Student academic-performance research.
        if (
            "student" in question_lower
            and (
                "academic" in question_lower
                or "performance" in question_lower
                or "grade" in question_lower
                or "score" in question_lower
            )
        ):
            return (
                f"{research_question} "
                "student academic performance prediction "
                "machine learning educational data mining"
            )

        # Generic ML prediction questions.
        return (
            f"{research_question} "
            "machine learning prediction "
            "supervised learning empirical study"
        )

    @staticmethod
    def _tool_execution(
        tool,
        tool_input: dict,
        result,
    ) -> ToolExecution:
        """Record an observable tool execution."""

        if result.success:
            summary = (
                f"{result.source} returned "
                f"{result.total_results} matching papers."
            )
            status = "success"
        else:
            summary = (
                result.error
                or f"{result.source} search failed."
            )
            status = "failed"

        return ToolExecution(
            provider=tool.provider_name,
            tool_name=tool.name,
            tool_input=tool_input,
            result_summary=summary,
            status=status,
        )

    @staticmethod
    def _create_finding(
        paper: Paper,
    ) -> LiteratureFinding:
        """Create a concise evidence finding from a paper."""

        if paper.abstract:
            summary = (
                paper.abstract
                .strip()
                .split(".")[0]
                .strip()
            )

            summary = (
                f"{summary}."
                if summary
                else (
                    "Abstract available; review the paper "
                    "for details."
                )
            )
        else:
            summary = (
                "No abstract was returned; review the paper "
                "before drawing conclusions."
            )

        return LiteratureFinding(
            paper_title=paper.title,
            paper_id=paper.source_id,
            evidence_summary=summary[:350],
        )