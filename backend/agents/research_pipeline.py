from backend.agents.dataset_evaluator import DatasetEvaluationAgent
from backend.agents.experiment_analyzer import ExperimentAnalysisAgent
from backend.agents.experiment_planner import ExperimentPlanningAgent
from backend.agents.research_orchestrator import ResearchOrchestrator
from backend.agents.research_report_agent import ResearchReportAgent

from backend.models.experiment import ExperimentPlanRequest
from backend.models.research_pipeline import ResearchPipelineResponse

from backend.tools.dataset_inspector import DatasetInspector
from backend.tools.dataset_preparer import DatasetPreparer
from backend.tools.dataset_search import DatasetSearchTool
from backend.tools.experiment_runner import ExperimentRunner


class ResearchPipelineAgent:
    """Run the complete ResearchPilot research workflow."""

    def run(
        self,
        research_question: str,
    ) -> ResearchPipelineResponse:

        completed = []

        # ==================================================
        # 1. RESEARCH PLANNING
        # ==================================================

        orchestrator = ResearchOrchestrator()

        plan = orchestrator.create_plan(
            research_question
        )

        completed.append("research_planning")

        # ==================================================
        # 2. LITERATURE RESEARCH
        # ==================================================

        literature = orchestrator.research_literature(
            research_question
        )

        completed.append("literature_research")

        # ==================================================
        # 3. DATASET DISCOVERY
        # ==================================================

        dataset_search = DatasetSearchTool().search(
            research_question
        )

        completed.append("dataset_discovery")

        if not dataset_search.datasets:
            return ResearchPipelineResponse(
                success=False,
                research_question=research_question,
                plan=plan.model_dump(),
                literature=literature.model_dump(),
                dataset_search=dataset_search.model_dump(),
                current_stage="dataset_discovery",
                completed_stages=completed,
                error="No suitable dataset candidates were found.",
            )

        # ==================================================
        # 4. DATASET EVALUATION
        # ==================================================

        evaluation = DatasetEvaluationAgent().evaluate(
            research_question,
            dataset_search.datasets,
        )

        completed.append("dataset_evaluation")

        if not evaluation.selection:
            return ResearchPipelineResponse(
                success=False,
                research_question=research_question,
                plan=plan.model_dump(),
                literature=literature.model_dump(),
                dataset_search=dataset_search.model_dump(),
                dataset_evaluation=evaluation.model_dump(),
                current_stage="dataset_evaluation",
                completed_stages=completed,
                error="Dataset evaluation did not select a dataset.",
            )

        selected_id = evaluation.selection.selected_dataset_id

        selected_name = (
            evaluation.selection.selected_dataset_name
        )

        # ==================================================
        # 5. DATASET INSPECTION
        # ==================================================

        inspection = DatasetInspector().inspect(
            selected_id
        )

        completed.append("dataset_inspection")

        if not inspection.get("success", False):
            return ResearchPipelineResponse(
                success=False,
                research_question=research_question,
                plan=plan.model_dump(),
                literature=literature.model_dump(),
                dataset_search=dataset_search.model_dump(),
                dataset_evaluation=evaluation.model_dump(),
                dataset_inspection=inspection,
                current_stage="dataset_inspection",
                completed_stages=completed,
                error="Selected dataset inspection failed.",
            )

        # --------------------------------------------------
        # Get target column
        # --------------------------------------------------

        target_column = inspection.get(
            "target_column"
        )

        if not target_column:
            return ResearchPipelineResponse(
                success=False,
                research_question=research_question,
                plan=plan.model_dump(),
                literature=literature.model_dump(),
                dataset_search=dataset_search.model_dump(),
                dataset_evaluation=evaluation.model_dump(),
                dataset_inspection=inspection,
                current_stage="dataset_preparation",
                completed_stages=completed,
                error="No target column was identified.",
            )

        # --------------------------------------------------
        # IMPORTANT:
        # Get the task type from dataset inspection.
        # --------------------------------------------------

        task_type = inspection.get(
            "task_type",
            "classification",
        )

        task_type = str(task_type).lower().strip()

        if task_type not in {
            "classification",
            "regression",
        }:
            task_type = "classification"

        # ==================================================
        # 6. DATASET PREPARATION
        # ==================================================

        preparation = DatasetPreparer().prepare(
            dataset_id=selected_id,
            target_column=target_column,
        )

        completed.append("dataset_preparation")

        # ==================================================
        # 7. EXPERIMENT PLANNING
        # ==================================================

        experiment_plan_request = ExperimentPlanRequest(
            research_question=research_question,
            dataset_id=selected_id,
            dataset_name=selected_name,
            target_column=target_column,
            task_type=task_type,
            numerical_columns=inspection.get(
                "numerical_columns",
                [],
            ),
            categorical_columns=inspection.get(
                "categorical_columns",
                [],
            ),
            prepared_feature_count=(
                preparation.prepared_feature_count or 0
            ),
        )

        experiment_plan = ExperimentPlanningAgent().plan(
            experiment_plan_request
        )

        completed.append("experiment_planning")

        # ==================================================
        # 8. RUN EXPERIMENTS
        # ==================================================

        # IMPORTANT FIX:
        # Pass task_type to ExperimentRunner.
        #
        # Previously this was:
        #
        # ExperimentRunner().run(
        #     dataset_id=selected_id,
        #     target_column=target_column,
        # )
        #
        # That caused the runner to fall back to regression.

        experiment_results = ExperimentRunner().run(
            dataset_id=selected_id,
            target_column=target_column,
            task_type=task_type,
        )

        completed.append("experiment_execution")

        if not experiment_results.get(
            "success",
            False,
        ):
            return ResearchPipelineResponse(
                success=False,
                research_question=research_question,
                plan=plan.model_dump(),
                literature=literature.model_dump(),
                dataset_search=dataset_search.model_dump(),
                dataset_evaluation=evaluation.model_dump(),
                dataset_inspection=inspection,
                dataset_preparation=preparation.model_dump(),
                experiment_plan=experiment_plan.model_dump(),
                experiment_results=experiment_results,
                current_stage="experiment_execution",
                completed_stages=completed,
                error=(
                    "Machine-learning experiment "
                    "execution failed."
                ),
            )

        # ==================================================
        # 9. ANALYZE EXPERIMENT RESULTS
        # ==================================================

        analysis = ExperimentAnalysisAgent().analyze(
            research_question=research_question,
            dataset_id=selected_id,
            dataset_name=selected_name,
            target_column=target_column,
            task_type=task_type,
            results=experiment_results.get(
                "results",
                [],
            ),
            best_model=experiment_results.get(
                "best_model",
                "",
            ),
        )

        completed.append("experiment_analysis")

        # ==================================================
        # 10. FINAL RESEARCH REPORT
        # ==================================================

        report = ResearchReportAgent().generate(
            research_question=research_question,
            research_plan=plan.model_dump(),
            literature=literature.model_dump(),
            dataset_inspection=inspection,
            experiment_results=experiment_results.get(
                "results",
                [],
            ),
            experiment_analysis=analysis.analysis.model_dump(),
            best_model=experiment_results.get(
                "best_model",
                "",
            ),
        )

        completed.append("final_report")

        # ==================================================
        # COMPLETE
        # ==================================================

        return ResearchPipelineResponse(
            success=True,
            research_question=research_question,
            plan=plan.model_dump(),
            literature=literature.model_dump(),
            dataset_search=dataset_search.model_dump(),
            dataset_evaluation=evaluation.model_dump(),
            dataset_inspection=inspection,
            dataset_preparation=preparation.model_dump(),
            experiment_plan=experiment_plan.model_dump(),
            experiment_results=experiment_results,
            experiment_analysis=analysis.model_dump(),
            final_report=report.model_dump(),
            current_stage="completed",
            completed_stages=completed,
            error=None,
        )