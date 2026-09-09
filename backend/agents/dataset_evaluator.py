"""Evaluate OpenML dataset candidates against the original research question."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.models.dataset import (
    DatasetAgentState,
    DatasetCandidate,
    DatasetEvaluation,
    DatasetEvaluationLLMResult,
    DatasetEvaluationResponse,
    DatasetSelection,
)

load_dotenv()


class DatasetEvaluationAgent:
    """Compare supplied OpenML candidates and select the best fit for the research goal."""

    name = "gemini_dataset_evaluation"

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def evaluate(self, research_question: str, datasets: list[DatasetCandidate]) -> DatasetEvaluationResponse:
        if not datasets:
            return self._empty_candidates_response(research_question)

        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Add it to your .env file.")

        llm_result = self._call_gemini(research_question, datasets)
        evaluations = self._align_with_candidates(llm_result.evaluations, datasets)
        if not evaluations:
            return DatasetEvaluationResponse(
                query=research_question,
                evaluations=[],
                selection=None,
                agent_state=DatasetAgentState(
                    current_goal=research_question,
                    current_action="Evaluating OpenML candidate datasets.",
                    tool_used=self.name,
                    decision="No usable evaluations were returned for the supplied candidates.",
                    next_action="Retry evaluation or refine the dataset search query.",
                    status="evaluation_failed",
                ),
                status="evaluation_failed",
                error="The evaluation agent returned no usable candidate assessments.",
            )

        selection = self._select_best(evaluations, llm_result.selection)
        return DatasetEvaluationResponse(
            query=research_question,
            evaluations=sorted(evaluations, key=lambda item: item.overall_score, reverse=True),
            selection=selection,
            agent_state=DatasetAgentState(
                current_goal=research_question,
                current_action="Evaluating OpenML candidate datasets.",
                tool_used=self.name,
                decision=f"{selection.selected_dataset_name} has the strongest overall fit.",
                next_action=selection.next_action,
                status="completed",
            ),
            status="completed",
        )

    def _call_gemini(self, research_question: str, datasets: list[DatasetCandidate]) -> DatasetEvaluationLLMResult:
        candidate_json = [self._public_metadata(dataset) for dataset in datasets]
        prompt = f"""
You are ResearchPilot's dataset evaluation agent.

Evaluate ONLY the OpenML dataset candidates supplied below. Do not invent datasets, IDs, names, instance counts, feature counts, targets, formats, or descriptions. If a field is null or missing, treat it as unavailable and mention that as a weakness. Do not claim a target attribute exists unless target_information is present in the supplied metadata.

If a field is null or missing, treat it as unavailable and mention that as a limitation. For target_information specifically, a null value means the target is unknown at the dataset-search stage; do not assume that the dataset has no target. Recommend verifying the target during dataset inspection.

Score each candidate against the original research question:
- relevance_score: fit of name/description to the research question
- size_score: usefulness of the reported number_of_instances (penalize unknown size)
- feature_score: usefulness of the reported number_of_features (penalize unknown feature count)
- target_score: suitability of the available target information for the research goal; if target_information is null or missing, do not assume that the dataset has no target, but assign a cautious score based on the dataset name and description and state that the target must be verified during dataset inspection
- ml_suitability_score: fit for supervised machine learning given only the supplied metadata
- overall_score: an integer 0-100 summary of the scores above

Identify concise strengths and weaknesses from the supplied metadata. Recommend how the dataset could be used, without claiming that experiments have already been run.

Select exactly one best candidate among the supplied datasets. Explain why it was selected and give a concrete next action such as inspecting the selected dataset schema and preparing it for experimentation. Do not recommend downloading or training steps that have not been implemented.

Research question:
{research_question}

Supplied OpenML candidates (JSON):
{candidate_json}
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DatasetEvaluationLLMResult,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty dataset-evaluation response.")
        return DatasetEvaluationLLMResult.model_validate_json(response.text)

    @staticmethod
    def _public_metadata(dataset: DatasetCandidate) -> dict:
        return dataset.model_dump()

    @staticmethod
    def _align_with_candidates(
        evaluations: list[DatasetEvaluation],
        datasets: list[DatasetCandidate],
    ) -> list[DatasetEvaluation]:
        by_id = {dataset.dataset_id: dataset for dataset in datasets}
        aligned: list[DatasetEvaluation] = []
        seen: set[str] = set()
        for evaluation in evaluations:
            candidate = by_id.get(evaluation.dataset_id)
            if candidate is None or evaluation.dataset_id in seen:
                continue
            seen.add(evaluation.dataset_id)
            aligned.append(
                evaluation.model_copy(
                    update={
                        "dataset_name": candidate.name,
                        "target_score": evaluation.target_score,
                    }
                )
            )
        return aligned

    @staticmethod
    def _select_best(
        evaluations: list[DatasetEvaluation],
        gemini_selection: DatasetSelection | None,
    ) -> DatasetSelection:
        best_score = max(item.overall_score for item in evaluations)
        top = [item for item in evaluations if item.overall_score == best_score]
        top_ids = {item.dataset_id for item in top}
        if gemini_selection and gemini_selection.selected_dataset_id in top_ids:
            chosen = next(item for item in top if item.dataset_id == gemini_selection.selected_dataset_id)
            return DatasetSelection(
                selected_dataset_id=chosen.dataset_id,
                selected_dataset_name=chosen.dataset_name,
                selection_reason=gemini_selection.selection_reason,
                next_action=gemini_selection.next_action,
            )
        chosen = top[0]
        return DatasetSelection(
            selected_dataset_id=chosen.dataset_id,
            selected_dataset_name=chosen.dataset_name,
            selection_reason=(
                gemini_selection.selection_reason
                if gemini_selection and gemini_selection.selected_dataset_id == chosen.dataset_id
                else f"{chosen.dataset_name} has the strongest overall fit (overall score {chosen.overall_score})."
            ),
            next_action=(
                gemini_selection.next_action
                if gemini_selection
                else "Inspect the selected dataset schema and prepare it for experimentation."
            ),
        )

    @staticmethod
    def _empty_candidates_response(research_question: str) -> DatasetEvaluationResponse:
        return DatasetEvaluationResponse(
            query=research_question,
            evaluations=[],
            selection=None,
            agent_state=DatasetAgentState(
                current_goal=research_question,
                current_action="Evaluating OpenML candidate datasets.",
                tool_used=None,
                decision="No candidates were available to compare.",
                next_action="Discover public datasets before evaluation.",
                status="no_candidates",
            ),
            status="no_candidates",
            error="No dataset candidates were provided for evaluation.",
        )
