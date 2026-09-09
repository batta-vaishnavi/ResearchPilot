# ResearchPilot — Autonomous AI Research Agent

> **Transform a natural-language research question into a complete, evidence-backed machine-learning research workflow.**

ResearchPilot is an Agentic AI Hackathon project for **Tech Zephyr 4.0 at IIT Bhubaneswar**. Instead of acting as a simple chatbot or LLM wrapper, ResearchPilot coordinates a multi-stage workflow that plans the research, discovers evidence and datasets, evaluates candidates, inspects and prepares data, runs machine-learning experiments, analyzes results, and generates a final research report.

---

## 1. Problem Statement

Machine-learning experimentation often requires researchers to manually perform a long sequence of disconnected tasks:

- formulate a research objective and hypothesis
- search existing literature
- find appropriate datasets
- compare dataset suitability
- inspect the target and feature schema
- preprocess the data
- choose appropriate models and evaluation metrics
- run experiments
- compare models
- interpret results
- write a research conclusion

ResearchPilot turns this fragmented workflow into a single agentic research pipeline driven by a natural-language research question.

---

## 2. Target Users

ResearchPilot is designed primarily for:

- students learning AI, ML, and data science
- student researchers and hackathon teams
- early-stage researchers
- developers building machine-learning prototypes
- educators demonstrating end-to-end research workflows

---

## 3. Why an Agentic Solution?

A basic chatbot could generate a research plan, but it would not actually execute and evaluate the workflow.

ResearchPilot demonstrates agentic behavior through:

**Planning → Decision Making → Tool Interaction → Multi-step Execution → Evaluation → Adaptation → Final Outcome**

The system dynamically responds to the research question. Different questions can lead to different task types, datasets, targets, model families, and evaluation metrics.

For example:

- student-performance questions can become a **regression** workflow
- diabetes questions can become a **classification** workflow
- house-price questions can discover and evaluate housing datasets
- a literature-tool failure can be detected and communicated while downstream stages continue

The model selection is evidence-driven. The system does not assume that the planned model will always be the winner.

---

# 4. Proposed Solution

ResearchPilot accepts a research question and executes the following autonomous workflow:

```text
Research Question
       │
       ▼
01. Research Planning
       │
       ▼
02. Literature Research
       │
       ▼
03. Dataset Discovery
       │
       ▼
04. Dataset Evaluation & Selection
       │
       ▼
05. Dataset Inspection
       │
       ▼
06. Dataset Preparation
       │
       ▼
07. Experiment Planning
       │
       ▼
08. Experiment Execution
       │
       ▼
09. Experiment Analysis
       │
       ▼
10. Final Research Report
```

The frontend exposes this workflow as a visible **10-stage agentic pipeline**.

---

# 5. Agentic Workflow

## Stage 1 — Research Planning

Gemini analyzes the research question and creates a structured plan containing:

- research goal
- research objective
- hypothesis
- required research steps
- suggested experiments
- evaluation metrics
- task type, such as regression or classification

The planning stage adapts to the question rather than assuming a fixed research domain.

## Stage 2 — Literature Research

ResearchPilot attempts literature discovery using:

1. **Semantic Scholar** as the primary provider
2. **OpenAlex** as a fallback when the primary search fails

The workflow records provider/tool state rather than fabricating research results.

```text
Semantic Scholar
      │
      ├── success ──► use literature results
      │
      └── failure
            │
            ▼
      record adaptation
            │
            ▼
         OpenAlex
            │
            ├── success ──► use fallback results
            │
            └── failure ──► report literature unavailable
```

## Stage 3 — Dataset Discovery

ResearchPilot searches **OpenML** for datasets related to the research question.

The discovery stage returns candidate metadata such as dataset ID, dataset name, number of instances, number of features, target metadata when available, URL, and description.

## Stage 4 — Dataset Evaluation & Selection

The agent compares candidate datasets against the original research objective using suitability dimensions such as:

- relevance
- size
- features
- target suitability
- machine-learning suitability
- overall fit

It then selects a dataset, explains the decision, and proposes the next action.

## Stage 5 — Dataset Inspection

The selected OpenML dataset is inspected for:

- row and column counts
- feature columns
- target column
- missing values
- duplicate rows
- task type
- data-quality concerns
- ML suitability

Target detection is performed from the inspected dataset rather than relying on one globally fixed target name.

## Stage 6 — Dataset Preparation

ResearchPilot prepares the selected dataset using a reproducible preprocessing pipeline supporting:

- numerical missing-value imputation
- numerical feature scaling
- categorical missing-value imputation
- categorical one-hot encoding
- unseen-category handling
- train/test splitting

## Stage 7 — Experiment Planning

The agent creates a task-aware experiment plan.

### Regression

- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

Metrics:

- MAE
- RMSE
- R²

### Classification

- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier

Metrics:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

The planned candidate is not automatically treated as the final winner.

## Stage 8 — Experiment Execution

The backend trains multiple models and evaluates them on a held-out test set.

### Current validation approach

**Regression**
- 80/20 train-test split

**Classification**
- 80/20 train-test split
- stratified when class distribution permits

The implementation also includes safeguards against identified target leakage patterns.

## Stage 9 — Experiment Analysis

ResearchPilot compares model results and selects the strongest model according to the task:

- regression → lower RMSE is preferred
- classification → higher F1-score is preferred

The analysis produces a summary, interpretation, key findings, recommendations, limitations, and a research takeaway.

## Stage 10 — Final Research Report

The final report includes:

- research title
- objective
- conclusion
- experimental evidence
- model evaluation
- evidence interpretation
- limitations
- future research direction

---

# 6. Example Workflows

## House Price Prediction

```text
Can machine learning predict house prices based on property characteristics?
```

Example successful run:

```text
Selected dataset: house_prices
Task: regression

Linear Regression
RMSE: 29448.4894
R²:   0.8869

Random Forest Regressor
RMSE: 29006.9736
R²:   0.8903

Gradient Boosting Regressor
RMSE: 26409.4065
R²:   0.9091
```

The system selected **Gradient Boosting Regressor** using RMSE.

## Diabetes Classification

```text
Can machine learning predict whether a patient has diabetes based on health measurements?
```

Example run:

```text
Selected dataset: Diabetes-Data-Set
Task: classification

Logistic Regression
F1: 0.7084

Random Forest Classifier
F1: 0.7555

Gradient Boosting Classifier
F1: 0.7496
```

The system selected **Random Forest Classifier** using F1-score.

---

# 7. Failure Handling

ResearchPilot distinguishes tool failure from a valid result.

```text
Literature search
      │
      ▼
Primary provider fails
      │
      ▼
Agent records failure/adaptation
      │
      ▼
Fallback provider attempted
      │
      ▼
If unavailable:
      │
      ▼
Literature marked unavailable
      │
      ▼
Remaining workflow continues
```

The UI explicitly communicates when literature retrieval is unavailable instead of inventing papers.

---

# 8. System Architecture

```text
                           ┌──────────────────────┐
                           │        User          │
                           │ Research Question    │
                           └──────────┬───────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │     React Frontend       │
                        │   ResearchPilot UI       │
                        └────────────┬─────────────┘
                                     │ HTTP / JSON
                                     ▼
                        ┌──────────────────────────┐
                        │      FastAPI Backend     │
                        │      API / Controller    │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                     ┌──────────────────────────────┐
                     │   Research Orchestrator      │
                     │      Agent / Controller      │
                     └──────────────┬───────────────┘
                                    │
            ┌───────────────────────┼────────────────────────┐
            │                       │                        │
            ▼                       ▼                        ▼
     ┌──────────────┐       ┌──────────────┐        ┌───────────────┐
     │ Literature   │       │   OpenML     │        │ Experiment    │
     │ Tools        │       │ Dataset Tool │        │ Runner        │
     └──────┬───────┘       └──────┬───────┘        └──────┬────────┘
            │                      │                       │
            ▼                      ▼                       ▼
     Semantic Scholar          OpenML                 scikit-learn
            │
       on failure
            │
            ▼
         OpenAlex
                                    │
                                    ▼
                         ┌────────────────────┐
                         │ Dataset Evaluation │
                         │ & Inspection       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Preparation        │
                         │ Experiments        │
                         │ Evaluation         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ AI Analysis        │
                         │ Final Report       │
                         └────────────────────┘
```

---

# 9. Architecture Components

| Component | Role |
|---|---|
| User | Supplies the research question and reviews results |
| React/Vite frontend | Presents the workflow and results |
| FastAPI backend | Exposes research APIs |
| Research Orchestrator | Coordinates the multi-step workflow |
| Gemini | Generates structured research plans and agent reasoning outputs |
| Semantic Scholar | Primary literature retrieval |
| OpenAlex | Literature fallback |
| OpenML | Dataset discovery and metadata |
| Dataset Evaluation Agent | Scores and selects candidate datasets |
| Dataset Inspector | Determines schema, target, task type, and data quality |
| Dataset Preparer | Builds preprocessing and train/test data |
| Experiment Runner | Trains and evaluates ML models |
| Analysis Agent | Interprets experiment results |
| Final Report Agent | Produces the final research report |

---

# 10. State, Retrieval, Evaluation & Adaptation

### State

The pipeline carries structured stage outputs between agents, including research goals, decisions, dataset selection, detected target, task type, experiment plan, model results, analysis, and final report.

### Retrieval

External information is retrieved from:

- Semantic Scholar
- OpenAlex
- OpenML

### Evaluation

The system evaluates literature retrieval outcomes, dataset suitability, dataset schema/quality, and model performance.

### Adaptation

Examples include:

- literature-provider fallback
- dynamic regression/classification workflow selection
- dataset choice based on research-question fit
- model selection based on observed experiment results

---

# 11. Technology Stack

### Frontend

- React
- Vite
- Tailwind CSS
- JavaScript

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### AI

- Google Gemini API
- `google-genai`

### Machine Learning

- scikit-learn
- NumPy
- Pandas

### External Sources

- Semantic Scholar Academic Graph API
- OpenAlex Works API
- OpenML API

---

# 12. Project Structure

```text
ResearchPilot/
│
├── backend/
│   ├── agents/
│   ├── models/
│   ├── routes/
│   ├── tools/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docs/
├── .env.example
├── .gitignore
├── README.md
└── package.json
```

---

# 13. Environment Configuration

Create a root `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Then add your own Gemini API key locally:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

**Never commit `.env` to GitHub.** Only the placeholder `.env.example` should be committed.

---

# 14. Backend Setup

From the project root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
uvicorn backend.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

# 15. Frontend Setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

The frontend uses the backend at:

```text
http://127.0.0.1:8000
```

unless `VITE_API_URL` is configured.

---

# 16. Main API

The FastAPI backend exposes workflow endpoints including:

```text
POST /api/research/plan
POST /api/research/literature
POST /api/research/datasets
POST /api/research/datasets/evaluate
POST /api/research/datasets/inspect
POST /api/research/datasets/analyze
POST /api/research/datasets/prepare
POST /api/research/experiments/plan
POST /api/research/experiments/run
POST /api/research/experiments/analyze
POST /api/research/report
POST /api/research/run
```

### End-to-end workflow endpoint

```text
POST /api/research/run
```

Example:

```json
{
  "research_question": "Can machine learning predict house prices based on property characteristics?"
}
```

---

# 17. Testing

Run backend tests from the project root:

```powershell
.ackend\.venv\Scripts\python.exe -m unittest discover -s backend	ests
```

For a final smoke test, verify:

1. a regression question
2. a classification question
3. literature-tool failure handling
4. full 10/10 workflow completion

---

# 18. Demo Workflow

Recommended primary demo question:

```text
Can machine learning predict house prices based on property characteristics?
```

The demonstration should visibly show:

**Goal → Decision → Action → Evaluation → Adaptation → Outcome**

A secondary diabetes example can demonstrate dynamic classification behavior.

---

# 19. Limitations

The current implementation has several limitations:

- literature retrieval depends on availability of external providers
- the current experiment runner uses a single held-out train/test evaluation rather than repeated cross-validation
- only a small set of baseline models is evaluated
- hyperparameter tuning is not part of the core execution path
- feature-importance analysis is not part of the current experiment output
- external API availability can affect literature retrieval
- predictive results should not be interpreted as causal evidence

---

# 20. Future Scope

Potential extensions include:

- stronger cross-validation and repeated evaluation
- automated hyperparameter tuning
- feature-importance and explainability modules
- richer literature synthesis and citation graphs
- persistent research memory
- experiment tracking and artifact storage
- larger model libraries
- human approval checkpoints
- hosted deployment
- downloadable research reports

---

# 21. Responsible AI

ResearchPilot is a research-assistance and experimentation system.

For sensitive domains such as healthcare:

- model outputs are experimental predictions, not medical diagnoses
- dataset limitations should be considered before deployment
- results should not be interpreted as causal evidence
- responsible human oversight is required for real-world decisions

---

# 22. Hackathon Context

**Event:** Agentic AI Hackathon  
**Fest:** Tech Zephyr 4.0  
**Institute:** Indian Institute of Technology Bhubaneswar

ResearchPilot demonstrates genuine agentic behavior through:

- planning
- tool interaction
- multi-step execution
- dataset and model decision-making
- evaluation
- failure handling
- adaptation
- final outcome generation

---

## ResearchPilot

**From research question to research-ready intelligence.**
