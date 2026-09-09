import logging

from fastapi import APIRouter, HTTPException, status

from backend.models.dataset_preparation import (
    DatasetPreparationRequest,
    DatasetPreparationResult,
)
from backend.tools.dataset_preparer import DatasetPreparer

from backend.agents.experiment_planner import ExperimentPlanningAgent
from backend.models.experiment import (
    ExperimentPlanRequest,
    ExperimentPlanResponse,
)

from backend.models.experiment_result import (
    ExperimentRunRequest,
    ExperimentRunResponse,
)

from backend.agents.research_report_agent import ResearchReportAgent
from backend.models.research_report import (
    ResearchReportRequest,
    ResearchReportResponse,
)

from backend.agents.research_pipeline import ResearchPipelineAgent
from backend.models.research_pipeline import (
    ResearchPipelineRequest,
    ResearchPipelineResponse,
)

from backend.agents.experiment_analyzer import ExperimentAnalysisAgent
from backend.models.experiment_analysis import (
    ExperimentAnalysisRequest,
    ExperimentAnalysisResponse,
)

from backend.tools.experiment_runner import ExperimentRunner

from backend.agents.dataset_evaluator import DatasetEvaluationAgent
from backend.agents.dataset_inspection_agent import DatasetInspectionAgent
from backend.agents.research_orchestrator import ResearchOrchestrator

from backend.models.dataset import (
    DatasetEvaluationRequest,
    DatasetEvaluationResponse,
    DatasetInspectionRequest,
    DatasetInspectionResult,
    DatasetSearchResult,
)

from backend.models.literature import LiteratureResearchResponse
from backend.models.research import (
    ResearchPlan,
    ResearchPlanRequest,
)

from backend.tools.dataset_inspector import DatasetInspector
from backend.tools.dataset_search import DatasetSearchTool


logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# 01. RESEARCH PLAN
# ============================================================

@router.post(
    "/plan",
    response_model=ResearchPlan,
)
def create_research_plan(
    payload: ResearchPlanRequest,
) -> ResearchPlan:
    """Analyze a research question and create a structured plan."""

    try:
        return ResearchOrchestrator().create_plan(
            payload.research_question.strip()
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Research-plan generation failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The planning agent could not generate "
                "a research plan. Please try again."
            ),
        ) from error


# ============================================================
# 02. LITERATURE
# ============================================================

@router.post(
    "/literature",
    response_model=LiteratureResearchResponse,
)
def research_literature(
    payload: ResearchPlanRequest,
) -> LiteratureResearchResponse:
    """Search and summarize published literature."""

    try:
        return ResearchOrchestrator().research_literature(
            payload.research_question.strip()
        )

    except Exception as error:
        logger.exception(
            "Literature research failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The literature research agent could not "
                "complete the search."
            ),
        ) from error


# ============================================================
# 03. DATASET DISCOVERY
# ============================================================

@router.post(
    "/datasets",
    response_model=DatasetSearchResult,
)
def discover_datasets(
    payload: ResearchPlanRequest,
) -> DatasetSearchResult:
    """Find public OpenML dataset candidates."""

    try:
        return DatasetSearchTool().search(
            payload.research_question.strip()
        )

    except Exception as error:
        logger.exception(
            "Dataset discovery failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The dataset search tool could not "
                "find suitable datasets."
            ),
        ) from error


# ============================================================
# 04. DATASET EVALUATION
# ============================================================

@router.post(
    "/datasets/evaluate",
    response_model=DatasetEvaluationResponse,
)
def evaluate_datasets(
    payload: DatasetEvaluationRequest,
) -> DatasetEvaluationResponse:
    """Compare candidate datasets and select the best one."""

    try:
        return DatasetEvaluationAgent().evaluate(
            payload.research_question.strip(),
            payload.datasets,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Dataset evaluation failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The dataset evaluation agent could not "
                "compare the candidates."
            ),
        ) from error


# ============================================================
# 05. DATASET INSPECTION
# ============================================================

@router.post(
    "/datasets/inspect",
    response_model=DatasetInspectionResult,
)
def inspect_dataset(
    request: DatasetInspectionRequest,
) -> DatasetInspectionResult:
    """Inspect the schema and quality of an OpenML dataset."""

    try:
        inspector = DatasetInspector()

        result = inspector.inspect(
            request.dataset_id
        )

        return DatasetInspectionResult.model_validate(
            result
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Dataset inspection failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The dataset inspector could not "
                "inspect the selected dataset."
            ),
        ) from error


# ============================================================
# 05B. DATASET ANALYSIS
# ============================================================

@router.post(
    "/datasets/analyze",
)
def analyze_dataset(
    request: DatasetInspectionRequest,
):
    """Analyze the inspected dataset and determine next action."""

    try:
        inspection = DatasetInspector().inspect(
            request.dataset_id
        )

        inspection_result = (
            DatasetInspectionResult.model_validate(
                inspection
            )
        )

        return DatasetInspectionAgent().analyze(
            research_question=(
                "Analyze the selected dataset for "
                "machine learning suitability."
            ),
            inspection=inspection_result,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Dataset inspection analysis failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The dataset inspection analysis agent "
                "could not analyze the selected dataset."
            ),
        ) from error


# ============================================================
# 06. DATASET PREPARATION
# ============================================================

@router.post(
    "/datasets/prepare",
    response_model=DatasetPreparationResult,
)
def prepare_dataset(
    request: DatasetPreparationRequest,
) -> DatasetPreparationResult:
    """Prepare the selected dataset for ML experiments."""

    try:
        preparer = DatasetPreparer()

        return preparer.prepare(
            dataset_id=request.dataset_id,
            target_column=request.target_column,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Dataset preparation failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The dataset preparation step could not "
                "prepare the selected dataset."
            ),
        ) from error


# ============================================================
# 07. EXPERIMENT PLANNING
# ============================================================

@router.post(
    "/experiments/plan",
    response_model=ExperimentPlanResponse,
)
def plan_experiments(
    request: ExperimentPlanRequest,
) -> ExperimentPlanResponse:
    """Create an ML experiment plan."""

    try:
        agent = ExperimentPlanningAgent()

        return agent.plan(
            request
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Experiment planning failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The experiment planning agent "
                "could not create an experiment plan."
            ),
        ) from error


# ============================================================
# 08. EXPERIMENT RUNNER
# ============================================================

@router.post(
    "/experiments/run",
    response_model=ExperimentRunResponse,
)
def run_experiments(
    request: ExperimentRunRequest,
) -> ExperimentRunResponse:
    """
    Run ML experiments.

    IMPORTANT:
    task_type is explicitly passed to ExperimentRunner.
    This prevents classification problems from accidentally
    being executed as regression problems.
    """

    try:

        runner = ExperimentRunner()

        # ----------------------------------------------------
        # IMPORTANT FIX
        # ----------------------------------------------------
        # Previously task_type was NOT passed here.
        #
        # That caused:
        #
        # classification
        #       ↓
        # default "regression"
        #       ↓
        # Linear Regression
        # Random Forest Regressor
        # Gradient Boosting Regressor
        #
        # Now we explicitly pass the task type.
        # ----------------------------------------------------

        result = runner.run(
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            task_type=request.task_type,
        )

        return ExperimentRunResponse(
            success=result["success"],
            research_question=request.research_question,
            dataset_id=result["dataset_id"],
            dataset_name=result.get("dataset_name"),
            target_column=result.get("target_column"),
            task_type=result.get("task_type"),
            train_rows=result.get("train_rows"),
            test_rows=result.get("test_rows"),
            results=result.get("results", []),
            best_model=result.get("best_model"),
            selection_metric=result.get(
                "selection_metric",
                "F1",
                ),
            status=result["status"],
            error=result.get("error"),
        )

    except ValueError as error:

        logger.exception(
            "Experiment validation failed"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:

        logger.exception(
            "Experiment execution failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The experiment runner could not "
                "execute the machine-learning experiments."
            ),
        ) from error


# ============================================================
# 09. EXPERIMENT ANALYSIS
# ============================================================

@router.post(
    "/experiments/analyze",
    response_model=ExperimentAnalysisResponse,
)
def analyze_experiments(
    request: ExperimentAnalysisRequest,
) -> ExperimentAnalysisResponse:
    """Analyze completed ML experiment results."""

    try:

        return ExperimentAnalysisAgent().analyze(
            research_question=request.research_question.strip(),
            dataset_id=request.dataset_id,
            dataset_name=request.dataset_name,
            target_column=request.target_column,
            task_type=request.task_type,
            results=request.results,
            best_model=request.best_model,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:

        logger.exception(
            "Experiment analysis failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The experiment analysis agent could not "
                "analyze the results."
            ),
        ) from error


# ============================================================
# 10. FINAL RESEARCH REPORT
# ============================================================

@router.post(
    "/report",
    response_model=ResearchReportResponse,
)
def generate_research_report(
    request: ResearchReportRequest,
) -> ResearchReportResponse:
    """Generate the final research report."""

    try:

        return ResearchReportAgent().generate(
            research_question=request.research_question.strip(),
            research_plan=request.research_plan,
            literature=request.literature,
            dataset_inspection=request.dataset_inspection,
            experiment_results=request.experiment_results,
            experiment_analysis=request.experiment_analysis,
            best_model=request.best_model,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:

        logger.exception(
            "Research report generation failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The research report agent could not "
                "generate the final report."
            ),
        ) from error


# ============================================================
# COMPLETE AUTONOMOUS PIPELINE
# ============================================================

@router.post(
    "/run",
    response_model=ResearchPipelineResponse,
)
def run_research_pipeline(
    request: ResearchPipelineRequest,
) -> ResearchPipelineResponse:
    """
    Run the complete ResearchPilot agentic workflow.

    Pipeline:

    1. Research Planning
    2. Literature Discovery
    3. Dataset Discovery
    4. Dataset Evaluation
    5. Dataset Inspection
    6. Dataset Preparation
    7. Experiment Planning
    8. Experiments
    9. Experiment Analysis
    10. Final Research Report
    """

    try:

        return ResearchPipelineAgent().run(
            request.research_question.strip()
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:

        logger.exception(
            "Research pipeline failed"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The ResearchPilot pipeline could not "
                "complete the research workflow."
            ),
        ) from error