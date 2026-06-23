from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # must be first — loads .env before any service reads os.environ

import os
from database import init_db, get_stats
from scheduler import start_scheduler
from routers import issues, confirmations, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield

app = FastAPI(
    title="CivicPulse API",
    description="3-agent autonomous civic intelligence platform. Discovery → Confirmation → Resolution.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the configured frontend URL + localhost for dev
_frontend_url = os.environ.get("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
if _frontend_url:
    _allowed_origins.append(_frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(issues.router)
app.include_router(confirmations.router)
app.include_router(admin.router)

stats_router = APIRouter()

@stats_router.get("/api/stats")
def stats():
    return get_stats()

app.include_router(stats_router)

@app.get("/")
def root():
    return {
        "app": "CivicPulse",
        "status": "running",
        "docs": "/docs",
        "agents": ["discovery", "confirmation", "resolution"],
    }
