"""AI agent responsible for planning ML experiments."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.models.experiment import (
    ExperimentPlan,
    ExperimentPlanRequest,
    ExperimentPlanResponse,
)

load_dotenv()


class ExperimentPlanningAgent:
    """Create a structured ML experiment plan using Gemini."""

    name = "gemini_experiment_planning"

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

    def plan(
        self,
        request: ExperimentPlanRequest,
    ) -> ExperimentPlanResponse:

        if not self.client:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        result = self._call_gemini(request)

        return ExperimentPlanResponse(
            success=True,
            plan=result,
            agent_state={
                "current_goal": request.research_question,
                "current_action": "Planning machine-learning experiments.",
                "tool_used": self.name,
                "decision": (
                    f"Created an experiment plan for "
                    f"{request.task_type} using "
                    f"{request.dataset_name}."
                ),
                "next_action": (
                    "Execute the planned preprocessing and "
                    "machine-learning experiments."
                ),
                "status": "completed",
            },
            status="completed",
        )

    def _call_gemini(
        self,
        request: ExperimentPlanRequest,
    ) -> ExperimentPlan:

        prompt = f"""
You are ResearchPilot's experiment planning agent.

Create a rigorous but practical machine-learning experiment plan
using ONLY the supplied research and dataset information.

Do NOT claim that any model has already been trained.
Do NOT invent experimental results.
Do NOT invent dataset properties.

Research question:
{request.research_question}

Dataset:
{request.dataset_name}

OpenML dataset ID:
{request.dataset_id}

Target column:
{request.target_column}

Task type:
{request.task_type}

Number of numerical columns:
{len(request.numerical_columns)}

Number of categorical columns:
{len(request.categorical_columns)}

Prepared feature count:
{request.prepared_feature_count}

Choose appropriate machine-learning models for the task.

For regression, consider models such as:
- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

For classification, consider appropriate classification algorithms.

Include:
1. A simple baseline model.
2. Several suitable candidate models.
3. Appropriate evaluation metrics.
4. A validation strategy.
5. Preprocessing summary.
6. Experiment steps.
7. A recommended model based on methodological suitability ONLY.

Important:
The recommended model is a recommendation before training.
Do not state that it is the best-performing model.

For regression, appropriate metrics may include:
- MAE
- RMSE
- R²

For classification, appropriate metrics may include:
- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

Return only structured data matching the supplied response schema.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExperimentPlan,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty experiment plan."
            )

        return ExperimentPlan.model_validate_json(
            response.text
        )