import { useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/* =========================================================
   PIPELINE STAGES
========================================================= */

const stages = [
  {
    key: "research_planning",
    number: "01",
    label: "Research Plan",
    icon: "◈",
  },
  {
    key: "literature_research",
    number: "02",
    label: "Literature",
    icon: "⌕",
  },
  {
    key: "dataset_discovery",
    number: "03",
    label: "Datasets",
    icon: "▦",
  },
  {
    key: "dataset_evaluation",
    number: "04",
    label: "Evaluation",
    icon: "◉",
  },
  {
    key: "dataset_inspection",
    number: "05",
    label: "Inspection",
    icon: "⌗",
  },
  {
    key: "dataset_preparation",
    number: "06",
    label: "Preparation",
    icon: "⚙",
  },
  {
    key: "experiment_planning",
    number: "07",
    label: "Experiment Plan",
    icon: "◇",
  },
  {
    key: "experiment_execution",
    number: "08",
    label: "Experiments",
    icon: "⚗",
  },
  {
    key: "experiment_analysis",
    number: "09",
    label: "Analysis",
    icon: "⌁",
  },
  {
    key: "final_report",
    number: "10",
    label: "Report",
    icon: "▤",
  },
];

/* =========================================================
   REUSABLE COMPONENTS
========================================================= */

function SectionTitle({ eyebrow, title, description }) {
  return (
    <div className="mb-6">
      {eyebrow && (
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400">
          {eyebrow}
        </p>
      )}

      <h2 className="text-2xl font-bold tracking-tight text-white">
        {title}
      </h2>

      {description && (
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
          {description}
        </p>
      )}
    </div>
  );
}

function GlassCard({ children, className = "" }) {
  return (
    <section
      className={`rounded-2xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/10 backdrop-blur-xl ${className}`}
    >
      {children}
    </section>
  );
}

function StatCard({ label, value, description }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.04] p-4">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-2 break-words text-2xl font-bold text-white">
        {value ?? "—"}
      </p>

      {description && (
        <p className="mt-1 text-xs text-slate-500">
          {description}
        </p>
      )}
    </div>
  );
}

function Tag({ children }) {
  return (
    <span className="inline-flex rounded-full border border-indigo-400/20 bg-indigo-400/10 px-3 py-1 text-xs font-medium text-indigo-300">
      {children}
    </span>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/40 p-5 text-center">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-white">
        {value ?? "—"}
      </p>
    </div>
  );
}


/* =========================================================
   EXPERIMENT HELPERS
========================================================= */

function isClassificationResults(results) {
  return Array.isArray(results) && results.some(
    (model) => model?.accuracy !== null && model?.accuracy !== undefined
  );
}

function safeMetric(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatMetric(value) {
  const number = safeMetric(value);
  return number === null ? "—" : number.toFixed(4);
}

function getBestExperimentResult(results) {
  if (!Array.isArray(results) || results.length === 0) return null;
  const classification = isClassificationResults(results);
  const valid = results.filter((model) =>
    safeMetric(classification ? model?.f1 : model?.rmse) !== null
  );
  if (!valid.length) return results[0];
  return valid.reduce((best, current) => {
    const cv = safeMetric(classification ? current.f1 : current.rmse);
    const bv = safeMetric(classification ? best.f1 : best.rmse);
    if (cv === null) return best;
    if (bv === null) return current;
    return classification ? (cv > bv ? current : best) : (cv < bv ? current : best);
  }, valid[0]);
}

/* =========================================================
   PIPELINE
========================================================= */

function Pipeline({ completedStages, isLoading }) {
  return (
    <GlassCard className="mb-8">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400">
            Agentic Workflow
          </p>

          <p className="mt-1 text-sm text-slate-500">
            ResearchPilot autonomous pipeline
          </p>
        </div>

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-indigo-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-400" />
            Agent working
          </div>
        )}

        {!isLoading && completedStages.length > 0 && (
          <Tag>{completedStages.length}/10 stages completed</Tag>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 md:grid-cols-5 lg:grid-cols-10">
        {stages.map((stage) => {
          const completed = completedStages.includes(stage.key);

          return (
            <div
              key={stage.key}
              className={`rounded-xl border p-3 transition-all duration-500 ${
                completed
                  ? "border-indigo-400/30 bg-indigo-500/10"
                  : "border-white/10 bg-white/[0.025]"
              }`}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`text-lg ${
                    completed ? "text-indigo-300" : "text-slate-600"
                  }`}
                >
                  {stage.icon}
                </span>

                <span className="text-[10px] font-semibold text-slate-600">
                  {stage.number}
                </span>
              </div>

              <p
                className={`mt-3 text-xs font-semibold ${
                  completed ? "text-white" : "text-slate-500"
                }`}
              >
                {stage.label}
              </p>

              {completed && (
                <p className="mt-1 text-[10px] text-indigo-300">
                  Completed
                </p>
              )}
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
}

/* =========================================================
   MODEL COMPARISON BAR CHART
========================================================= */

function ModelComparisonChart({ results }) {
  if (!Array.isArray(results) || results.length === 0) return null;

  const classification = isClassificationResults(results);
  const metricKey = classification ? "f1" : "rmse";
  const metricLabel = classification ? "F1-score" : "RMSE";

  const chartData = results
    .map((model) => ({ model: model?.model_name ?? "Unknown model", value: safeMetric(model?.[metricKey]) }))
    .filter((item) => item.model && item.value !== null);

  if (!chartData.length) return null;
  const maxValue = Math.max(...chartData.map((item) => item.value));

  return (
    <div className="mt-8 rounded-2xl border border-white/10 bg-black/20 p-6">
      <div className="mb-8">
        <p className="text-lg font-semibold text-white">Model Performance Comparison</p>
        <p className="mt-1 text-sm text-slate-500">
          {metricLabel} comparison across the evaluated {classification ? "classification" : "regression"} models.
        </p>
        <p className="mt-2 text-xs text-indigo-300">
          {classification ? "Higher F1-score indicates better classification performance." : "Lower RMSE indicates better prediction performance."}
        </p>
      </div>

      <div className="space-y-7">
        {chartData.map((item, index) => {
          const percentage = maxValue > 0 ? (item.value / maxValue) * 100 : 0;
          return (
            <div key={item.model}>
              <div className="mb-2 flex items-center justify-between gap-4">
                <div className="flex min-w-0 items-center gap-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-500/15 text-xs font-bold text-indigo-300">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="truncate text-sm font-medium text-slate-300">{item.model}</span>
                </div>
                <span className="shrink-0 text-sm font-bold text-white">{item.value.toFixed(4)}</span>
              </div>
              <div className="h-10 w-full overflow-hidden rounded-xl border border-white/5 bg-slate-900/80">
                <div className="flex h-full items-center rounded-xl bg-indigo-500 px-4 transition-all duration-1000" style={{ width: `${Math.max(percentage, 4)}%` }}>
                  {percentage > 18 && <span className="text-xs font-bold text-white">{metricLabel}</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 flex justify-between text-[10px] text-slate-600">
        <span>0</span><span>{maxValue > 0 ? (maxValue / 2).toFixed(2) : "0"}</span><span>{maxValue.toFixed(2)}</span>
      </div>
    </div>
  );
}

/* =========================================================
   MODEL RESULTS
========================================================= */

function ModelResults({ results }) {
  if (!Array.isArray(results) || results.length === 0) return null;
  const classification = isClassificationResults(results);
  const bestModel = getBestExperimentResult(results);
  if (!bestModel) return null;

  const metricPairs = (model) => classification
    ? [["Accuracy", model.accuracy], ["Precision", model.precision], ["Recall", model.recall], ["F1-score", model.f1], ["ROC-AUC", model.roc_auc]]
    : [["MAE", model.mae], ["RMSE", model.rmse], ["R²", model.r2]];

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-2xl border border-indigo-400/30 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-transparent p-6">
        <div className="absolute right-[-40px] top-[-40px] h-32 w-32 rounded-full bg-indigo-500/10 blur-2xl" />
        <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2"><span className="text-lg">🏆</span><p className="text-xs font-bold uppercase tracking-[0.2em] text-indigo-300">Best Performing Model</p></div>
            <h3 className="mt-2 text-2xl font-black text-white">{bestModel.model_name}</h3>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
              {classification ? "Selected based on the highest F1-score among the evaluated classification models." : "Selected based on the lowest RMSE among the evaluated regression models."}
            </p>
          </div>
          <div className="rounded-xl border border-indigo-400/20 bg-black/20 px-6 py-4 text-center">
            <p className="text-xs uppercase tracking-wider text-slate-500">{classification ? "F1-score" : "RMSE"}</p>
            <p className="mt-1 text-3xl font-black text-indigo-300">{formatMetric(classification ? bestModel.f1 : bestModel.rmse)}</p>
          </div>
        </div>
      </div>

      <div>
        <div className="mb-4"><p className="text-sm font-semibold text-white">Model Metrics</p><p className="mt-1 text-xs text-slate-500">Performance of every {classification ? "classification" : "regression"} model evaluated by ResearchPilot.</p></div>
        <div className="grid gap-4 md:grid-cols-3">
          {results.map((model) => {
            const isBest = model.model_name === bestModel.model_name;
            return (
              <div key={model.model_name} className={`relative overflow-hidden rounded-2xl border p-5 transition-all ${isBest ? "border-indigo-400/40 bg-indigo-400/10 shadow-lg shadow-indigo-950/20" : "border-white/10 bg-slate-950/40"}`}>
                {isBest && <div className="absolute right-4 top-4"><span className="rounded-full border border-indigo-400/30 bg-indigo-400/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-indigo-300">Best</span></div>}
                <p className="pr-12 text-base font-bold text-white">{model.model_name}</p>
                <div className={`mt-5 grid gap-2 ${classification ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-3"}`}>
                  {metricPairs(model).map(([label, value]) => (
                    <div key={label} className="rounded-xl border border-white/5 bg-black/20 p-3 text-center">
                      <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
                      <p className="mt-2 text-lg font-bold text-white">{formatMetric(value)}</p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <div className="mb-4"><p className="text-sm font-semibold text-white">Detailed Comparison</p><p className="mt-1 text-xs text-slate-500">{classification ? "Higher Accuracy, Precision, Recall, F1-score and ROC-AUC generally indicate better classification performance." : "Lower MAE and RMSE are better; higher R² indicates better variance explanation."}</p></div>
        <div className="overflow-hidden rounded-2xl border border-white/10"><div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left">
            <thead className="border-b border-white/10 bg-white/[0.03]"><tr>
              <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Model</th>
              {(classification ? ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"] : ["MAE", "RMSE", "R²"]).map((label) => <th key={label} className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</th>)}
              <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Status</th>
            </tr></thead>
            <tbody>{results.map((model, index) => {
              const isBest = model.model_name === bestModel.model_name;
              const values = metricPairs(model).map(([, value]) => value);
              return <tr key={model.model_name} className={`border-b border-white/5 last:border-0 ${isBest ? "bg-indigo-400/5" : "bg-black/10"}`}>
                <td className="px-5 py-4"><div className="flex items-center gap-3"><div className={`flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold ${isBest ? "bg-indigo-400/20 text-indigo-300" : "bg-white/5 text-slate-500"}`}>{index + 1}</div><span className="font-medium text-white">{model.model_name}</span></div></td>
                {values.map((value, i) => <td key={i} className="px-5 py-4 font-mono text-sm text-slate-300">{formatMetric(value)}</td>)}
                <td className="px-5 py-4">{isBest ? <span className="inline-flex rounded-full border border-indigo-400/20 bg-indigo-400/10 px-3 py-1 text-xs font-semibold text-indigo-300">🏆 Best model</span> : <span className="text-xs text-slate-600">Evaluated</span>}</td>
              </tr>;
            })}</tbody>
          </table>
        </div></div>
      </div>
    </div>
  );
}

/* =========================================================
   MAIN APP/* =========================================================
   MAIN APP
========================================================= */

function App() {
  const [question, setQuestion] = useState(
    "Can machine learning predict student academic performance?"
  );

  const [research, setResearch] = useState(null);

  const [error, setError] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const completedStages =
    research?.completed_stages ?? [];

  /* =======================================================
     START RESEARCH
  ======================================================= */

  async function startResearch(event) {
    event.preventDefault();

    const researchQuestion = question.trim();

    if (researchQuestion.length < 10) {
      setError(
        "Please enter a research question with at least 10 characters."
      );
      return;
    }

    setIsLoading(true);
    setError("");
    setResearch(null);

    try {
      const response = await fetch(
        `${API_URL}/api/research/run`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            research_question: researchQuestion,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
            "Research pipeline could not be completed."
        );
      }

      if (!data.success) {
        throw new Error(
          data.error ??
            "Research pipeline could not be completed."
        );
      }

      console.log("Research response:", data);

      setResearch(data);
    } catch (requestError) {
      console.error(
        "Research request failed:",
        requestError
      );

      setError(
        requestError.message ??
          "Something went wrong."
      );
    } finally {
      setIsLoading(false);
    }
  }

  /* =======================================================
     EXTRACT RESULTS
  ======================================================= */

  const plan = research?.plan;

  const literature =
    research?.literature;

  const datasetSearch =
    research?.dataset_search;

  const datasetEvaluation =
    research?.dataset_evaluation;

  const preparation =
    research?.dataset_preparation;

  const experimentPlan =
    research?.experiment_plan;

  const experimentResults =
    research?.experiment_results;

  const analysis =
    research?.experiment_analysis?.analysis;

  const report =
    research?.final_report?.report;

  const selectedDataset =
    datasetEvaluation?.selection
      ?.selected_dataset_name;

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#060714] px-4 py-8 text-white sm:px-6 lg:px-8">
      {/* ===================================================
          BACKGROUND
      =================================================== */}

      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[-15%] top-[-10%] h-[500px] w-[500px] rounded-full bg-indigo-600/15 blur-[120px]" />

        <div className="absolute right-[-10%] top-[20%] h-[500px] w-[500px] rounded-full bg-purple-600/10 blur-[130px]" />

        <div className="absolute bottom-[-15%] left-[30%] h-[450px] w-[450px] rounded-full bg-blue-600/10 blur-[130px]" />

        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,.25) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.25) 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />
      </div>

      <div className="mx-auto w-full max-w-7xl min-w-0">
        {/* =================================================
            HEADER
        ================================================= */}

        <header className="mb-8 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-indigo-400/30 bg-indigo-500/20 text-2xl font-black text-white shadow-lg shadow-indigo-900/20">
              R
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-3xl font-black tracking-tight sm:text-4xl">
                  Research
                  <span className="text-indigo-400">
                    Pilot
                  </span>
                </h1>

                <span className="rounded-full border border-indigo-400/30 bg-indigo-400/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-indigo-300">
                  AI Research Agent
                </span>
              </div>

              <p className="mt-1 text-sm text-slate-500">
                Autonomous research planning · Evidence discovery ·
                Dataset intelligence
              </p>
            </div>
          </div>

          <div className="rounded-full border border-white/10 bg-white/[0.03] px-5 py-2.5 text-xs text-slate-400 backdrop-blur-xl">
            Agentic AI Hackathon · IIT Bhubaneswar
          </div>
        </header>

        {/* =================================================
            PIPELINE
        ================================================= */}

        <Pipeline
          completedStages={completedStages}
          isLoading={isLoading}
        />

        {/* =================================================
            HERO
        ================================================= */}

        <section className="relative mb-8 overflow-hidden rounded-3xl border border-white/10 bg-white/[0.035] p-7 shadow-2xl backdrop-blur-xl sm:p-10">
          <div className="absolute right-[-100px] top-[-100px] h-[350px] w-[350px] rounded-full border border-indigo-400/10">
            <div className="absolute inset-10 rounded-full border border-indigo-400/10">
              <div className="absolute inset-10 rounded-full border border-indigo-400/10" />
            </div>
          </div>

          <div className="relative max-w-4xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-400/30 bg-indigo-400/10 px-4 py-2 text-xs font-semibold text-indigo-300">
              <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-400" />
              Autonomous Research Intelligence
            </div>

            <h2 className="text-4xl font-black leading-tight tracking-tight sm:text-6xl">
              Turn a question into
              <span className="block text-indigo-400">
                research-ready intelligence.
              </span>
            </h2>

            <p className="mt-6 max-w-3xl text-base leading-7 text-slate-400 sm:text-lg">
              ResearchPilot plans your research, searches literature,
              discovers datasets, evaluates candidates, runs experiments,
              analyzes results, and generates a final research report —
              all through one agentic workflow.
            </p>

            {/* =================================================
                QUESTION FORM
            ================================================= */}

            <form
              onSubmit={startResearch}
              className="mt-8 rounded-2xl border border-white/10 bg-black/20 p-3 backdrop-blur-xl"
            >
              <label
                htmlFor="research-question"
                className="sr-only"
              >
                Research question
              </label>

              <textarea
                id="research-question"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="Enter your research question..."
                className="min-h-28 w-full resize-none bg-transparent p-4 text-base text-white outline-none placeholder:text-slate-600"
              />

              <div className="flex flex-col gap-3 border-t border-white/10 pt-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="px-3 text-xs text-slate-500">
                  Ask a question that can be investigated using evidence,
                  datasets, and machine-learning experiments.
                </p>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="rounded-xl bg-indigo-500 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-indigo-950/40 transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isLoading
                    ? "Researching..."
                    : "Start Research →"}
                </button>
              </div>
            </form>

            {isLoading && (
              <div className="mt-5 flex items-center gap-3 rounded-xl border border-indigo-400/20 bg-indigo-400/5 p-4 text-sm text-indigo-300">
                <span className="h-3 w-3 animate-ping rounded-full bg-indigo-400" />
                ResearchPilot is executing the autonomous research
                pipeline...
              </div>
            )}

            {error && (
              <div className="mt-5 rounded-xl border border-red-400/20 bg-red-400/5 p-4 text-sm text-red-300">
                <strong>Pipeline error:</strong>{" "}
                {error}
              </div>
            )}
          </div>
        </section>

        {/* =================================================
            RESULTS
        ================================================= */}

        {research && (
          <div className="space-y-8">
            {/* =================================================
                OVERVIEW
            ================================================= */}

            <GlassCard>
              <SectionTitle
                eyebrow="Research Overview"
                title="Research pipeline completed"
                description={
                  research.research_question
                }
              />

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <StatCard
                  label="Pipeline status"
                  value={
                    research.status ?? "Completed"
                  }
                />

                <StatCard
                  label="Completed stages"
                  value={`${completedStages.length}/10`}
                />

                <StatCard
                  label="Selected dataset"
                  value={
                    selectedDataset ?? "—"
                  }
                />

                <StatCard
                  label="Task type"
                  value={
                    experimentPlan?.plan?.task_type ??
                    experimentResults?.task_type ??
                    "Regression"
                  }
                />
              </div>
            </GlassCard>

            {/* =================================================
                RESEARCH PLAN
            ================================================= */}

            {plan && (
              <GlassCard>
                <SectionTitle
                  eyebrow="01 · Research Planning"
                  title={plan.research_goal}
                  description={
                    plan.research_objective
                  }
                />

                <div className="grid gap-5 lg:grid-cols-2">
                  <div className="rounded-xl border border-indigo-400/20 bg-indigo-400/5 p-5">
                    <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                      Proposed hypothesis
                    </p>

                    <p className="mt-3 leading-7 text-slate-300">
                      {plan.proposed_hypothesis}
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-white/[0.025] p-5">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Evaluation metrics
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {(plan.evaluation_metrics ?? []).map(
                        (metric) => (
                          <Tag key={metric}>
                            {metric}
                          </Tag>
                        )
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-5 grid gap-5 md:grid-cols-2">
                  <div>
                    <p className="mb-3 text-sm font-semibold text-white">
                      Research steps
                    </p>

                    <div className="space-y-2">
                      {(plan.required_steps ?? []).map(
                        (step, index) => (
                          <div
                            key={step}
                            className="flex gap-3 rounded-lg border border-white/5 bg-white/[0.025] p-3 text-sm text-slate-400"
                          >
                            <span className="font-bold text-indigo-400">
                              {String(index + 1).padStart(
                                2,
                                "0"
                              )}
                            </span>

                            {step}
                          </div>
                        )
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="mb-3 text-sm font-semibold text-white">
                      Suggested experiments
                    </p>

                    <div className="space-y-2">
                      {(plan.suggested_experiments ?? []).map(
                        (experiment) => (
                          <div
                            key={experiment}
                            className="rounded-lg border border-white/5 bg-white/[0.025] p-3 text-sm text-slate-400"
                          >
                            {experiment}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              </GlassCard>
            )}

            {/* =================================================
                LITERATURE
            ================================================= */}

            {literature && (
              <GlassCard>
                <SectionTitle
                  eyebrow="02 · Evidence Discovery"
                  title="Literature intelligence"
                  description="Published research discovered by the agent."
                />

                <div className="mb-5 grid gap-4 sm:grid-cols-3">
                  <StatCard
                    label="Papers found"
                    value={
                      literature.papers_found ?? 0
                    }
                  />

                  <StatCard
                    label="Search provider"
                    value={
                      literature.agent_state
                        ?.tool_history?.[0]
                        ?.provider ??
                      "Research agent"
                    }
                  />

                  <StatCard
                    label="Agent status"
                    value={
                      literature.agent_state
                        ?.status ?? "completed"
                    }
                  />
                </div>

                {literature.papers?.length > 0 && (
                  <div className="grid gap-4 lg:grid-cols-2">
                    {literature.papers.map(
                      (paper) => (
                        <article
                          key={
                            paper.source_id ??
                            paper.title
                          }
                          className="min-w-0 overflow-hidden rounded-xl border border-white/10 bg-black/20 p-5"
                        >
                          <h3 className="break-words font-semibold leading-6 text-white">
                            {paper.title}
                          </h3>

                          <p className="mt-2 break-words text-xs text-slate-500">
                            {paper.year ??
                              "Year unavailable"}
                            {" · "}
                            {paper.authors?.join(
                              ", "
                            ) ||
                              "Authors unavailable"}
                          </p>

                          {paper.abstract && (
                            <p className="mt-4 text-sm leading-6 text-slate-400">
                              {paper.abstract.slice(
                                0,
                                400
                              )}
                              {paper.abstract
                                .length > 400
                                ? "…"
                                : ""}
                            </p>
                          )}

                          {paper.paper_url && (
                            <a
                              href={paper.paper_url}
                              target="_blank"
                              rel="noreferrer"
                              className="mt-4 inline-block text-sm font-semibold text-indigo-400 hover:text-indigo-300"
                            >
                              Read paper ↗
                            </a>
                          )}
                        </article>
                      )
                    )}
                  </div>
                )}
              </GlassCard>
            )}

            {/* =================================================
                DATASETS
            ================================================= */}

            {datasetSearch && (
              <GlassCard>
                <SectionTitle
                  eyebrow="03 · Dataset Intelligence"
                  title="Candidate datasets"
                  description="Public datasets discovered and evaluated by the research agent."
                />

                <div className="mb-5 grid gap-4 sm:grid-cols-3">
                  <StatCard
                    label="Candidates"
                    value={
                      datasetSearch.datasets
                        ?.length ?? 0
                    }
                  />

                  <StatCard
                    label="Selected"
                    value={
                      selectedDataset ??
                      "Pending"
                    }
                  />

                  <StatCard
                    label="Preparation"
                    value={
                      preparation?.status ??
                      "Completed"
                    }
                  />
                </div>

                {datasetSearch.datasets?.length > 0 && (
                  <div className="grid gap-4 md:grid-cols-2">
                    {datasetSearch.datasets.map(
                      (dataset) => {
                        const isSelected =
                          String(
                            dataset.dataset_id
                          ) ===
                          String(
                            datasetEvaluation
                              ?.selection
                              ?.selected_dataset_id
                          );

                        return (
                          <article
                            key={
                              dataset.dataset_id
                            }
                            className={`min-w-0 overflow-hidden rounded-xl border p-5 transition ${
                              isSelected
                                ? "border-indigo-400/40 bg-indigo-400/10"
                                : "border-white/10 bg-black/20"
                            }`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <h3 className="break-words font-semibold text-white">
                                  {dataset.name}
                                </h3>

                                <p className="mt-1 text-xs text-slate-500">
                                  OpenML ID{" "}
                                  {
                                    dataset.dataset_id
                                  }
                                </p>
                              </div>

                              {isSelected && (
                                <Tag>
                                  Selected
                                </Tag>
                              )}
                            </div>

                            <div className="mt-4 flex gap-2">
                              <Tag>
                                {dataset.number_of_instances ??
                                  "?"}{" "}
                                rows
                              </Tag>

                              <Tag>
                                {dataset.number_of_features ??
                                  "?"}{" "}
                                features
                              </Tag>
                            </div>

                            <p className="mt-4 text-sm leading-6 text-slate-400">
                              {dataset.description ??
                                "No description available."}
                            </p>
                          </article>
                        );
                      }
                    )}
                  </div>
                )}
              </GlassCard>
            )}

            {/* =================================================
                DATASET EVALUATION
            ================================================= */}

            {datasetEvaluation && (
              <GlassCard>
                <SectionTitle
                  eyebrow="04 · Agent Decision"
                  title="Dataset evaluation & selection"
                  description="The agent compares candidate datasets and selects the most suitable one for the research objective."
                />

                {datasetEvaluation.selection && (
                  <div className="mb-6 rounded-2xl border border-indigo-400/30 bg-indigo-400/10 p-6">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          Selected Dataset
                        </p>

                        <h3 className="mt-2 text-2xl font-bold text-white">
                          {
                            datasetEvaluation
                              .selection
                              .selected_dataset_name
                          }
                        </h3>

                        <p className="mt-1 text-sm text-slate-400">
                          ID{" "}
                          {
                            datasetEvaluation
                              .selection
                              .selected_dataset_id
                          }
                        </p>
                      </div>

                      <div className="rounded-xl border border-indigo-400/20 bg-black/20 px-5 py-4">
                        <p className="text-xs text-slate-500">
                          Agent decision
                        </p>

                        <p className="mt-1 max-w-md text-sm text-slate-300">
                          {
                            datasetEvaluation
                              .selection
                              .selection_reason
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {datasetEvaluation.evaluations?.length >
                  0 && (
                  <div className="grid gap-4 md:grid-cols-2">
                    {datasetEvaluation.evaluations.map(
                      (evaluation) => (
                        <article
                          key={
                            evaluation.dataset_id
                          }
                          className="rounded-xl border border-white/10 bg-black/20 p-5"
                        >
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-white">
                              {
                                evaluation.dataset_name
                              }
                            </h3>

                            <span className="text-lg font-bold text-indigo-300">
                              {
                                evaluation.overall_score
                              }
                            </span>
                          </div>

                          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
                            <MetricCard
                              label="Relevance"
                              value={
                                evaluation.relevance_score
                              }
                            />

                            <MetricCard
                              label="Size"
                              value={
                                evaluation.size_score
                              }
                            />

                            <MetricCard
                              label="Features"
                              value={
                                evaluation.feature_score
                              }
                            />

                            <MetricCard
                              label="Target"
                              value={
                                evaluation.target_score
                              }
                            />

                            <MetricCard
                              label="ML"
                              value={
                                evaluation.ml_suitability_score
                              }
                            />
                          </div>

                          <p className="mt-4 text-sm leading-6 text-slate-400">
                            {
                              evaluation.recommendation
                            }
                          </p>
                        </article>
                      )
                    )}
                  </div>
                )}
              </GlassCard>
            )}

            {/* =================================================
                EXPERIMENTS
            ================================================= */}

            {(experimentPlan ||
              experimentResults) && (
              <GlassCard>
                <SectionTitle
                  eyebrow="05 · Machine Learning"
                  title="Experiment laboratory"
                  description={`ResearchPilot trains multiple ${isClassificationResults(experimentResults?.results) ? "classification" : "regression"} models, compares their performance, and identifies the strongest candidate using appropriate evaluation metrics.`}
                />

                {experimentPlan?.plan && (
                  <div className="mb-6 grid gap-4 md:grid-cols-3">
                    <StatCard
                      label="Baseline model"
                      value={
                        experimentPlan.plan
                          .baseline_model
                      }
                    />

                    <StatCard
                      label="Planned candidate"
                      value={
                        experimentPlan.plan
                          .recommended_model
                      }
                    />

                    <StatCard
                      label="Validation strategy"
                      value={
                        experimentResults?.task_type === "classification"
                          ? "80/20 stratified train-test split"
                          : "80/20 train-test split"
                      }
                    />
                  </div>
                )}

                {experimentResults && (
                  <>
                    <div className="mb-6 rounded-xl border border-indigo-400/20 bg-indigo-400/5 p-5">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <p className="text-xs uppercase tracking-wider text-indigo-300">
                            Best performing model
                          </p>

                          <h3 className="mt-1 text-xl font-bold text-white">
                            {
                              experimentResults.best_model
                            }
                          </h3>
                        </div>

                        <Tag>
                          Selection metric:{" "}
                          {
                            experimentResults.selection_metric
                          }
                        </Tag>
                      </div>
                    </div>

                    <ModelResults
                      results={
                        experimentResults.results
                      }
                    />

                    <ModelComparisonChart
                      results={
                        experimentResults.results
                      }
                    />
                  </>
                )}
              </GlassCard>
            )}

            {/* =================================================
                06 · AI ANALYSIS
            ================================================= */}

            {analysis && (
              <GlassCard>
                <SectionTitle
                  eyebrow="06 · AI Analysis"
                  title="What did the experiment reveal?"
                  description="ResearchPilot interprets the experimental evidence, compares model behavior, identifies limitations, and recommends the next research actions."
                />

                {/* TOP SUMMARY */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-2xl border border-indigo-400/30 bg-indigo-400/10 p-5">
                    <p className="text-xs uppercase tracking-wider text-indigo-300">
                      Strongest candidate
                    </p>

                    <p className="mt-3 break-words text-lg font-bold text-white">
                      {
                        experimentResults?.best_model ??
                        "—"
                      }
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Selected by model evaluation
                    </p>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-black/20 p-5">
                    <p className="text-xs uppercase tracking-wider text-slate-500">{isClassificationResults(experimentResults?.results) ? "Best F1-score" : "Best RMSE"}</p>
                    <p className="mt-3 text-2xl font-black text-white">{(() => { const results = experimentResults?.results ?? []; const best = getBestExperimentResult(results); return best ? formatMetric(isClassificationResults(results) ? best.f1 : best.rmse) : "—"; })()}</p>
                    <p className="mt-1 text-xs text-slate-600">{isClassificationResults(experimentResults?.results) ? "Higher is better" : "Lower is better"}</p>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-black/20 p-5">
                    <p className="text-xs uppercase tracking-wider text-slate-500">{isClassificationResults(experimentResults?.results) ? "Best Accuracy" : "Best R²"}</p>
                    <p className="mt-3 text-2xl font-black text-white">{(() => { const results = experimentResults?.results ?? []; const values = results.map((model) => safeMetric(isClassificationResults(results) ? model.accuracy : model.r2)).filter((v) => v !== null); return values.length ? Math.max(...values).toFixed(4) : "—"; })()}</p>
                    <p className="mt-1 text-xs text-slate-600">{isClassificationResults(experimentResults?.results) ? "Higher is better" : "Variance explained"}</p>
                  </div>

                  <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/5 p-5">
                    <p className="text-xs uppercase tracking-wider text-emerald-300">
                      Analysis status
                    </p>

                    <p className="mt-3 text-lg font-bold text-white">
                      Complete
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Evidence interpreted
                    </p>
                  </div>
                </div>

                {/* EXPERIMENT SUMMARY */}
                {analysis.experiment_summary && (
                  <div className="mt-6 rounded-2xl border border-white/10 bg-black/20 p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/15 text-sm font-bold text-indigo-300">
                        01
                      </span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          Experiment summary
                        </p>

                        <p className="text-sm font-semibold text-white">
                          What was tested?
                        </p>
                      </div>
                    </div>

                    <p className="mt-4 leading-7 text-slate-300">
                      {analysis.experiment_summary}
                    </p>
                  </div>
                )}

                {/* INTERPRETATION */}
                <div className="mt-5 rounded-2xl border border-indigo-400/20 bg-indigo-400/5 p-6">
                  <div className="flex items-center gap-3">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/15 text-sm font-bold text-indigo-300">
                      02
                    </span>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                        Interpretation
                      </p>

                      <p className="text-sm font-semibold text-white">
                        What does the evidence mean?
                      </p>
                    </div>
                  </div>

                  <p className="mt-4 leading-7 text-slate-300">
                    {analysis.interpretation ??
                      analysis.summary}
                  </p>

                  {experimentResults?.best_model && (
                    <div className="mt-5 rounded-xl border border-indigo-400/20 bg-black/20 p-4">
                      <p className="text-xs uppercase tracking-wider text-indigo-300">
                        Model selection insight
                      </p>

                      <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm text-slate-300">
                          <span className="font-semibold text-white">
                            {
                              experimentResults.best_model
                            }
                          </span>{" "}
                          was selected as the strongest model using the appropriate metric for this task.
                        </p>

                        {experimentResults.results?.length >
                          0 && (
                          <span className="shrink-0 rounded-lg border border-indigo-400/20 bg-indigo-400/10 px-3 py-2 text-sm font-bold text-indigo-300">
                            {isClassificationResults(experimentResults.results) ? "F1" : "RMSE"}{" "}{(() => { const best = getBestExperimentResult(experimentResults.results); return best ? formatMetric(isClassificationResults(experimentResults.results) ? best.f1 : best.rmse) : "—"; })()}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* KEY FINDINGS */}
                {analysis.key_findings?.length > 0 && (
                  <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-6">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">✦</span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          03 · Evidence
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          Key findings
                        </h3>
                      </div>
                    </div>

                    <p className="mt-1 text-sm text-slate-500">
                      The most important observations extracted from
                      the experimental results.
                    </p>

                    <div className="mt-5 space-y-3">
                      {analysis.key_findings.map(
                        (finding, index) => (
                          <div
                            key={`${finding}-${index}`}
                            className="flex gap-4 rounded-xl border border-white/5 bg-white/[0.025] p-4"
                          >
                            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-500/15 text-xs font-bold text-indigo-300">
                              {String(index + 1).padStart(
                                2,
                                "0"
                              )}
                            </span>

                            <span className="text-sm leading-6 text-slate-300">
                              {finding}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* RECOMMENDATIONS */}
                {analysis.recommendations?.length > 0 && (
                  <div className="mt-5 rounded-2xl border border-indigo-400/20 bg-indigo-400/5 p-6">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">→</span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          04 · Research Direction
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          Recommended next steps
                        </h3>
                      </div>
                    </div>

                    <p className="mt-1 text-sm text-slate-500">
                      Actions that can improve the reliability and
                      predictive performance of future experiments.
                    </p>

                    <div className="mt-5 space-y-3">
                      {analysis.recommendations.map(
                        (recommendation, index) => (
                          <div
                            key={`${recommendation}-${index}`}
                            className="flex gap-4 rounded-xl border border-indigo-400/10 bg-black/20 p-4"
                          >
                            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-500/15 text-xs font-bold text-indigo-300">
                              {index + 1}
                            </span>

                            <span className="text-sm leading-6 text-slate-300">
                              {recommendation}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* LIMITATIONS */}
                {analysis.limitations?.length > 0 && (
                  <div className="mt-5 rounded-2xl border border-amber-400/20 bg-amber-400/5 p-6">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">⚠</span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                          05 · Research Caveats
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          Research limitations
                        </h3>
                      </div>
                    </div>

                    <p className="mt-1 text-sm text-slate-500">
                      Factors that should be considered before drawing
                      strong conclusions from the current experiment.
                    </p>

                    <div className="mt-5 space-y-3">
                      {analysis.limitations.map(
                        (limitation, index) => (
                          <div
                            key={`${limitation}-${index}`}
                            className="flex gap-3 rounded-xl border border-amber-400/10 bg-black/20 p-4"
                          >
                            <span className="text-amber-400">
                              ⚠
                            </span>

                            <span className="text-sm leading-6 text-slate-300">
                              {limitation}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* TAKEAWAY */}
                <div className="mt-5 rounded-2xl border border-white/10 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent p-6">
                  <div className="flex items-center gap-3">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/15 text-sm">06</span>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">Research Takeaway</p>
                      <h3 className="text-lg font-bold text-white">What this means</h3>
                    </div>
                  </div>
                  <p className="mt-4 leading-7 text-slate-300">
                    {analysis?.interpretation ?? "The current experiment provides an initial benchmark for the selected research question. Results should be interpreted together with the validation strategy, dataset characteristics, and possible overfitting or data leakage."}
                  </p>
                  {experimentResults?.best_model && (
                    <div className="mt-5 flex flex-wrap gap-3">
                      <Tag>Best model: {experimentResults.best_model}</Tag>
                      {experimentResults.results?.length > 0 && (() => {
                        const classification = isClassificationResults(experimentResults.results);
                        const best = getBestExperimentResult(experimentResults.results);
                        return best ? <Tag>{classification ? "F1" : "RMSE"}: {formatMetric(classification ? best.f1 : best.rmse)}</Tag> : null;
                      })()}
                    </div>
                  )}
                </div>
              </GlassCard>
            )}

            {/* =================================================
                07 · FINAL RESEARCH REPORT
            ================================================= */}

            {report && (
              <section className="relative overflow-hidden rounded-3xl border border-indigo-400/30 bg-gradient-to-br from-indigo-950/80 via-slate-950/90 to-purple-950/60 p-7 shadow-2xl sm:p-10">
                {/* Decorative elements */}
                <div className="absolute right-[-100px] top-[-100px] h-80 w-80 rounded-full bg-indigo-500/10 blur-3xl" />

                <div className="absolute bottom-[-120px] left-[-80px] h-72 w-72 rounded-full bg-purple-500/10 blur-3xl" />

                <div className="absolute right-10 top-10 hidden h-24 w-24 rounded-full border border-indigo-400/10 md:block">
                  <div className="absolute inset-3 rounded-full border border-indigo-400/10">
                    <div className="absolute inset-3 rounded-full border border-indigo-400/10" />
                  </div>
                </div>

                <div className="relative">
                  {/* REPORT HEADER */}
                  <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                    <div className="max-w-4xl">
                      <div className="mb-4 flex flex-wrap items-center gap-3">
                        <span className="rounded-full border border-indigo-400/30 bg-indigo-400/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.2em] text-indigo-300">
                          07 · Final Research Report
                        </span>

                        <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-300">
                          Research complete
                        </span>
                      </div>

                      <h2 className="text-3xl font-black leading-tight text-white sm:text-4xl lg:text-5xl">
                        {report.title}
                      </h2>

                      <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
                        ResearchPilot synthesized the planning,
                        evidence discovery, dataset evaluation,
                        machine-learning experiments, and AI analysis
                        into the final research conclusion below.
                      </p>
                    </div>

                    {/* BEST MODEL */}
                    <div className="shrink-0 rounded-2xl border border-indigo-400/30 bg-black/30 p-5 text-center backdrop-blur-xl lg:min-w-[220px]">
                      <div className="mb-2 text-xl">
                        🏆
                      </div>

                      <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                        Best model
                      </p>

                      <p className="mt-2 text-base font-black leading-6 text-indigo-300">
                        {report.best_model ??
                          experimentResults?.best_model ??
                          "—"}
                      </p>

                      {experimentResults?.results?.length >
                        0 && (
                        <p className="mt-2 text-xs text-slate-500">
                          {isClassificationResults(experimentResults.results) ? "F1" : "RMSE"}{" "}{(() => { const best = getBestExperimentResult(experimentResults.results); return best ? formatMetric(isClassificationResults(experimentResults.results) ? best.f1 : best.rmse) : "—"; })()}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* REPORT SNAPSHOT */}
                  <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="rounded-2xl border border-white/10 bg-black/25 p-5">
                      <p className="text-xs uppercase tracking-wider text-slate-500">
                        Dataset
                      </p>

                      <p className="mt-2 break-words font-bold text-white">
                        {selectedDataset ??
                          "—"}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/25 p-5">
                      <p className="text-xs uppercase tracking-wider text-slate-500">
                        Models evaluated
                      </p>

                      <p className="mt-2 text-2xl font-black text-white">
                        {experimentResults?.results
                          ?.length ?? 0}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/25 p-5">
                      <p className="text-xs uppercase tracking-wider text-slate-500">{isClassificationResults(experimentResults?.results) ? "Best F1-score" : "Best RMSE"}</p>
                      <p className="mt-2 text-2xl font-black text-indigo-300">{(() => { const results = experimentResults?.results ?? []; const best = getBestExperimentResult(results); return best ? formatMetric(isClassificationResults(results) ? best.f1 : best.rmse) : "—"; })()}</p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/25 p-5">
                      <p className="text-xs uppercase tracking-wider text-slate-500">{isClassificationResults(experimentResults?.results) ? "Best Accuracy" : "Best R²"}</p>
                      <p className="mt-2 text-2xl font-black text-indigo-300">{(() => { const results = experimentResults?.results ?? []; const classification = isClassificationResults(results); const values = results.map((model) => safeMetric(classification ? model.accuracy : model.r2)).filter((v) => v !== null); return values.length ? Math.max(...values).toFixed(4) : "—"; })()}</p>
                    </div>
                  </div>

                  {/* OBJECTIVE */}
                  <div className="mt-6 rounded-2xl border border-white/10 bg-black/25 p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/15 text-sm font-bold text-indigo-300">
                        01
                      </span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          Research Objective
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          What was the study designed to investigate?
                        </h3>
                      </div>
                    </div>

                    <p className="mt-4 leading-7 text-slate-300">
                      {report.objective ??
                        plan?.research_objective ??
                        "The study evaluates whether machine-learning models can answer the selected research question using the chosen dataset and target."}
                    </p>
                  </div>

                  {/* CONCLUSION */}
                  <div className="mt-5 rounded-2xl border border-indigo-400/20 bg-indigo-400/5 p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/15 text-sm font-bold text-indigo-300">
                        02
                      </span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          Research Conclusion
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          What did the research establish?
                        </h3>
                      </div>
                    </div>

                    <p className="mt-4 text-base leading-8 text-slate-200">
                      {report.conclusion}
                    </p>
                  </div>

                  {/* RESULTS SUMMARY */}
                  <div className="mt-5 rounded-2xl border border-white/10 bg-black/25 p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/15 text-sm font-bold text-indigo-300">
                        03
                      </span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          Experimental Evidence
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          Results summary
                        </h3>
                      </div>
                    </div>

                    <p className="mt-4 leading-7 text-slate-300">
                      {report.results_summary}
                    </p>
                  </div>

                  {/* MODEL RESULTS */}
                  {experimentResults?.results?.length > 0 && (
                    <div className="mt-5">
                      <div className="mb-4">
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">04 · Model Evaluation</p>
                        <h3 className="mt-1 text-xl font-bold text-white">Performance at a glance</h3>
                        <p className="mt-1 text-sm text-slate-500">
                          Comparison of the {isClassificationResults(experimentResults.results) ? "classification" : "regression"} models evaluated during the experiment.
                        </p>
                      </div>
                      <div className="grid gap-4 md:grid-cols-3">
                        {experimentResults.results.map((model, index) => {
                          const classification = isClassificationResults(experimentResults.results);
                          const isBest = model.model_name === experimentResults.best_model;
                          const values = classification
                            ? [["Accuracy", model.accuracy], ["Precision", model.precision], ["Recall", model.recall], ["F1", model.f1], ["ROC-AUC", model.roc_auc]]
                            : [["MAE", model.mae], ["RMSE", model.rmse], ["R²", model.r2]];
                          return (
                            <div key={model.model_name} className={`rounded-2xl border p-5 ${isBest ? "border-indigo-400/40 bg-indigo-400/10" : "border-white/10 bg-black/20"}`}>
                              <div className="flex items-start justify-between gap-3">
                                <div className="flex items-center gap-3">
                                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-xs font-bold text-slate-400">{String(index + 1).padStart(2, "0")}</span>
                                  <p className="text-sm font-bold text-white">{model.model_name}</p>
                                </div>
                                {isBest && <span className="rounded-full border border-indigo-400/20 bg-indigo-400/10 px-2 py-1 text-[9px] font-bold uppercase tracking-wider text-indigo-300">Best</span>}
                              </div>
                              <div className={`mt-5 grid gap-2 ${classification ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-3"}`}>
                                {values.map(([label, value]) => (
                                  <div key={label} className="rounded-xl bg-black/20 p-3 text-center">
                                    <p className="text-[9px] uppercase tracking-wider text-slate-600">{label}</p>
                                    <p className="mt-1 text-sm font-bold text-slate-300">{formatMetric(value)}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* INTERPRETATION */}
                  <div className="mt-6 rounded-2xl border border-white/10 bg-black/25 p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/15 text-sm font-bold text-indigo-300">
                        05
                      </span>

                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                          Evidence Interpretation
                        </p>

                        <h3 className="text-lg font-bold text-white">
                          What should researchers take away?
                        </h3>
                      </div>
                    </div>

                    <p className="mt-4 leading-7 text-slate-300">
                      {analysis?.interpretation ??
                        "The experimental results provide an initial benchmark for the selected research question. Further validation is needed before making strong claims about model generalization."}
                    </p>
                  </div>

                  {/* LIMITATIONS + NEXT STEPS */}
                  <div className="mt-5 grid gap-5 lg:grid-cols-2">
                    <div className="rounded-2xl border border-amber-400/20 bg-amber-400/5 p-6">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">
                          ⚠
                        </span>

                        <div>
                          <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                            06 · Limitations
                          </p>

                          <h3 className="text-lg font-bold text-white">
                            Important caveats
                          </h3>
                        </div>
                      </div>

                      <div className="mt-5 space-y-3">
                        {(analysis?.limitations ??
                          []).map(
                          (limitation, index) => (
                            <div
                              key={`${limitation}-${index}`}
                              className="flex gap-3 text-sm leading-6 text-slate-300"
                            >
                              <span className="text-amber-400">
                                •
                              </span>

                              <span>
                                {limitation}
                              </span>
                            </div>
                          )
                        )}

                        {(!analysis?.limitations ||
                          analysis.limitations
                            .length === 0) && (
                          <p className="text-sm leading-6 text-slate-400">
                            The current experiment is limited by
                            the dataset scope, model selection, and
                            available validation evidence.
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-indigo-400/20 bg-indigo-400/5 p-6">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">
                          →
                        </span>

                        <div>
                          <p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                            07 · Future Research
                          </p>

                          <h3 className="text-lg font-bold text-white">
                            Recommended direction
                          </h3>
                        </div>
                      </div>

                      <div className="mt-5 space-y-3">
                        {(analysis?.recommendations ??
                          []).map(
                          (recommendation, index) => (
                            <div
                              key={`${recommendation}-${index}`}
                              className="flex gap-3 text-sm leading-6 text-slate-300"
                            >
                              <span className="font-bold text-indigo-400">
                                {index + 1}.
                              </span>

                              <span>
                                {recommendation}
                              </span>
                            </div>
                          )
                        )}

                        {(!analysis?.recommendations ||
                          analysis.recommendations
                            .length === 0) && (
                          <p className="text-sm leading-6 text-slate-400">
                            Future work should explore feature
                            engineering, hyperparameter tuning,
                            additional algorithms, stronger
                            validation, and additional datasets.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* FINAL TAKEAWAY */}
                  <div className="mt-6 rounded-2xl border border-indigo-400/30 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-transparent p-6">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-[0.2em] text-indigo-300">
                          Final Research Takeaway
                        </p>

                        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
                          {report.conclusion ?? analysis?.interpretation ?? "The current experiment provides an initial, reproducible benchmark for the selected research question. Further validation is recommended before making strong claims about generalization."}
                        </p>
                      </div>

                      <div className="shrink-0 rounded-xl border border-indigo-400/20 bg-black/25 px-5 py-4 text-center">
                        <p className="text-[10px] uppercase tracking-wider text-slate-500">
                          Research status
                        </p>

                        <p className="mt-1 text-lg font-black text-emerald-300">
                          Complete
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}
          </div>
        )}

        {/* =================================================
            FOOTER
        ================================================= */}

        <footer className="py-10 text-center text-xs text-slate-600">
          ResearchPilot · Autonomous AI Research Workflow
        </footer>
      </div>
    </main>
  );
}

export default App;