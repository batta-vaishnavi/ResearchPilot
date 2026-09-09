# ResearchPilot — Autonomous Research-to-Experiment Agent

ResearchPilot is a hackathon project for the Agentic AI Hackathon at IIT Bhubaneswar. Its long-term goal is to guide a research question through: **Goal → Observe → Plan → Act → Evaluate → Adapt → Re-plan → Final Outcome**.

## Current functionality

ResearchPilot currently runs this workflow:

```text
Research Question
→ Plan
→ Literature
→ Dataset Discovery
→ Dataset Evaluation
→ Dataset Selection
→ Next Action
```

- **Phase 1 — Research Planning:** Gemini creates a structured research plan.
- **Phase 2 — Literature Research:** Semantic Scholar is searched first. If it fails (including rate-limit responses), the agent records an adaptation and searches OpenAlex.
- **Phase 3A — OpenML Dataset Discovery:** Public OpenML candidates are returned with metadata supplied by OpenML.
- **Phase 3B — Autonomous Dataset Evaluation and Selection:** The evaluation agent compares those candidates against the original research question, scores them, selects one dataset, explains the decision, and proposes a next action.

Phase 3B is agentic because the system does not stop at search results. It evaluates multiple candidate datasets against the research goal and autonomously selects the most suitable candidate while explaining the decision.

Dataset downloading, experiment execution, databases, authentication, deployment, and persistent memory remain out of scope.

## Tech stack

- Frontend: React, Vite, Tailwind CSS
- Backend: Python, FastAPI
- AI: Gemini API (`google-genai`)
- Literature sources: Semantic Scholar Academic Graph API (primary) and OpenAlex Works API (fallback); neither requires a paid key
- Dataset source: OpenML public dataset API

## Setup

Copy `.env.example` to `.env` at the project root, then replace the placeholder with a valid Gemini key. Do not commit `.env`.

```powershell
Copy-Item .env.example .env
```

Run the backend:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
uvicorn backend.main:app --reload
```

The API runs at `http://localhost:8000`; API docs are at `http://localhost:8000/docs`.

In a second terminal, run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`).

## API

`POST /api/research/plan`

```json
{ "research_question": "Can transformer models improve early detection of crop disease from leaf images?" }
```

The response contains `research_goal`, `research_objective`, `proposed_hypothesis`, `required_steps`, `suggested_experiments`, `evaluation_metrics`, and `current_status`.

### Literature research API

`POST /api/research/literature`

```json
{ "research_question": "Can transformer models improve early detection of crop disease from leaf images?" }
```

The result contains selected `papers`, evidence-based `findings`, and an `agent_state`. The state records the public workflow: goal, action, selected tool, tool input, result summary, decision, next action, and status. If the external API fails, it returns a `tool_failed` state with no invented papers or findings.

### Dataset discovery API (Phase 3A)

`POST /api/research/datasets`

```json
{ "research_question": "Find datasets for crop disease image classification" }
```

The endpoint returns OpenML candidate metadata, including IDs, names, OpenML URLs, size, feature count, target metadata, and format where OpenML supplies it.

### Dataset evaluation API (Phase 3B)

`POST /api/research/datasets/evaluate`

```json
{
  "research_question": "Can machine learning predict student academic performance?",
  "datasets": [
    {
      "dataset_id": "42351",
      "name": "student_performance_por",
      "url": "https://www.openml.org/d/42351",
      "number_of_instances": 649,
      "number_of_features": 33,
      "target_information": "G3",
      "source": "OpenML"
    }
  ]
}
```

The agent evaluates only the supplied candidates, returns per-dataset scores and trade-offs, selects one dataset, and includes `agent_state` (`current_goal`, `current_action`, `tool_used`, `decision`, `next_action`, `status`). It does not invent OpenML metadata or download data.

## Tool architecture

`backend/tools/literature_search.py` isolates the Semantic Scholar primary provider, while `backend/tools/openalex_search.py` provides the OpenAlex fallback. The orchestrator decides to search, observes each provider result, and records concise tool history plus any adaptation in the UI state.

The literature workflow is: Semantic Scholar → use results, or on failure → record adaptation → OpenAlex → use results or return `tool_failed` with no papers/findings.

`backend/tools/dataset_search.py` discovers OpenML candidates. `backend/agents/dataset_evaluator.py` then compares those candidates with Gemini structured output and selects the best fit for the research question.

## Tests

Run the backend tests from the project root:

```powershell
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend\tests
```

## Project structure

```text
backend/       FastAPI application
  agents/      Research Orchestrator and Dataset Evaluation Agent
  models/      Pydantic schemas
  routes/      API endpoints
  tools/       External agent tools
  services/    Future external integrations
frontend/      React/Vite application
docs/          Architecture notes
```
