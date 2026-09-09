from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load the .env file from the ResearchPilot root folder
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from backend.routes.research import router as research_router


app = FastAPI(
    title="ResearchPilot API",
    description="API for creating structured research plans.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    research_router,
    prefix="/api/research",
    tags=["research"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}