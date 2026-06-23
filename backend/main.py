from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # must be first — loads .env before any service reads os.environ

from database import init_db, get_all_issues, get_stats
from agents.discovery_agent import run_all_cities
from scheduler import start_scheduler
from routers import issues, confirmations, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB init
    init_db()
    # Background scheduler (discovery every 6h, escalation every 30min)
    start_scheduler()
    # Auto-seed demo data on first run
    if not get_all_issues():
        print("[Startup] Empty DB — seeding demo data via discovery agent...")
        await run_all_cities()
    yield

app = FastAPI(
    title="CivicPulse API",
    description="3-agent autonomous civic intelligence platform. Discovery → Confirmation → Resolution.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
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
