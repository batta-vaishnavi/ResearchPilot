# Architecture

ResearchPilot currently implements:

```text
Research Question
→ Plan
→ Literature
→ Dataset Discovery
→ Dataset Evaluation
→ Dataset Selection
→ Next Action
```

```text
React UI
  → POST /api/research/plan
      ResearchOrchestrator → Gemini structured JSON → ResearchPlan
  → POST /api/research/literature
      Semantic Scholar tool
        ↓ on tool failure / HTTP 429
      OpenAlex fallback tool
  → POST /api/research/datasets
      DatasetSearchTool → OpenML candidates
  → POST /api/research/datasets/evaluate
      DatasetEvaluationAgent → Gemini structured comparison → selected dataset
```

## Phase ownership

- **Phase 1 — Research Planning:** Gemini produces a schema-validated plan. It does not claim to have searched literature or found datasets.
- **Phase 2 — Literature Research:** Semantic Scholar is the primary source. On failure, the agent records an adaptation and uses OpenAlex. If both fail, it returns `tool_failed` with no fabricated papers or findings.
- **Phase 3A — OpenML Dataset Discovery:** Public dataset metadata is retrieved and ranked as candidates. This stage does not download data or train models.
- **Phase 3B — Autonomous Dataset Evaluation and Selection:** The evaluation agent reasons over the supplied OpenML metadata, scores each candidate against the original research question, selects one dataset, explains the decision, and proposes a next action.

Phase 3B is agentic: the system does not simply return search results. It evaluates multiple candidate datasets against the research goal and autonomously selects the most suitable candidate while explaining the decision.

## Module boundaries

- `backend/routes/` owns HTTP concerns.
- `backend/models/` owns request/response schemas.
- `backend/agents/` owns planning and dataset evaluation decisions.
- `backend/tools/` owns external source integrations and structured tool results.
- `backend/services/` is reserved for future integrations.

Dataset downloading and model training are not part of this milestone.
