import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.models.experiment_analysis import (
    ExperimentAnalysis,
    ExperimentAnalysisAgentState,
    ExperimentAnalysisResponse,
)

load_dotenv()


class ExperimentAnalysisAgent:
    """Analyze actual machine-learning experiment results."""

    name = "gemini_experiment_analysis"

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        self.client = (
            genai.Client(api_key=api_key)
            if api_key
            else None
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash-lite",
        )

    def analyze(
        self,
        research_question: str,
        dataset_id: str,
        dataset_name: str,
        target_column: str,
        task_type: str,
        results: list[dict],
        best_model: str,
    ) -> ExperimentAnalysisResponse:

        if not self.client:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        # Convert experiment results into a clear JSON representation.
        # This prevents Gemini from confusing the current experiment
        # with previous experiments.
        import json

        results_json = json.dumps(
            results,
            indent=2,
            default=str,
        )

        prompt = f"""
You are ResearchPilot's experiment analysis agent.

You are analyzing ONE CURRENT research experiment.

CRITICAL RULE:
Use ONLY the information provided in this prompt.

Do NOT use information from previous conversations,
previous experiments, previous datasets, or previous research questions.

The current research question is:
{research_question}

The current dataset is:
{dataset_name}

The current dataset ID is:
{dataset_id}

The current target column is:
{target_column}

The current machine-learning task is:
{task_type}

The experiment runner selected this model as the best model:
{best_model}

The ACTUAL results from the current experiment are:

{results_json}

==================================================
ANALYSIS RULES
==================================================

1. Analyze ONLY the current experiment.

2. Keep the analysis directly related to the current
   research question and current dataset.

3. NEVER mention student academic performance unless
   the CURRENT research question, dataset, or target
   actually concerns students or academic performance.

4. NEVER mention house prices unless the CURRENT
   research question, dataset, or target actually
   concerns house prices.

5. Do NOT copy conclusions from another research run.

6. Do NOT invent:
   - datasets
   - target variables
   - metrics
   - experiments
   - feature importance
   - correlations
   - statistical significance
   - causal relationships
   - validation results

7. Use the exact reported metrics from the experiment.

8. For regression:
   - Lower MAE is better.
   - Lower RMSE is better.
   - Higher R² is better.

9. For classification:
   - Higher Accuracy is generally better.
   - Higher Precision is generally better.
   - Higher Recall is generally better.
   - Higher F1-score is generally better.
   - Higher ROC-AUC is generally better.

10. Do not call a model "highly accurate" unless the
    supplied metrics clearly support that conclusion.

11. Do not claim that the model causes anything.

12. Clearly distinguish actual experiment findings
    from recommendations for future experiments.

==================================================
REQUIRED ANALYSIS
==================================================

Provide:

1. Experiment summary
   - What was tested?
   - On which dataset?
   - For which target?
   - For which task?

2. Best model
   - Identify the supplied best model.
   - Explain why it was selected using the reported metrics.

3. Key findings
   - Compare the evaluated models.
   - Use only the supplied numbers.

4. Interpretation
   - Explain what the metrics mean for THIS research question.
   - Be careful about overclaiming.

5. Limitations
   - Mention only limitations supported by the supplied
     experiment information.

6. Recommended next steps
   - Suggest practical future experiments.
   - Clearly label them as future work.

IMPORTANT:
The final analysis must be specific to THIS research question,
THIS dataset, THIS target column, and THESE experiment results.

Do not produce generic student-performance conclusions.
Do not reuse conclusions from previous runs.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExperimentAnalysis,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty experiment-analysis response."
            )

        analysis = ExperimentAnalysis.model_validate_json(
            response.text
        )

        return ExperimentAnalysisResponse(
            success=True,
            research_question=research_question,
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            analysis=analysis,
            agent_state=ExperimentAnalysisAgentState(
                current_goal=research_question,
                current_action=(
                    "Analyzing the current machine-learning "
                    "experiment results."
                ),
                tool_used=self.name,
                decision=(
                    f"{analysis.best_model} was identified as the "
                    "best-performing model based strictly on "
                    "the supplied current experiment results."
                ),
                next_action=(
                    "Review the current findings and determine "
                    "whether additional experiments are needed."
                ),
                status="completed",
            ),
            status="completed",
        )