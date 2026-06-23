from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # must be first — loads .env before any service reads os.environ

import os
from database import init_db, get_stats
from scheduler import start_scheduler
from routers import issues, confirmations, admin

async def _background_discovery():
    """Run real discovery in background after seed data is shown. Adds real issues on top."""
    import asyncio
    from agents.discovery_agent import run_discovery, MONITOR_CITIES
    await asyncio.sleep(3)  # let server fully start first
    print("[Startup] Running background discovery to supplement seed data...")
    try:
        await run_discovery(MONITOR_CITIES[0])  # Bengaluru — 1 Gemini call
    except Exception as e:
        print(f"[Startup] Background discovery failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from database import get_all_issues
    init_db()
    start_scheduler()

    # Always show seed data instantly (milliseconds, no API)
    if not get_all_issues():
        from seed_data import seed_database
        seed_database()
        asyncio.create_task(_background_discovery())

    # Start Telegram bot if token is set
    _bot_app = None
    _telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if _telegram_token:
        try:
            from services.telegram_bot import build_application
            _bot_app = build_application(_telegram_token)
            await _bot_app.initialize()
            await _bot_app.start()
            await _bot_app.updater.start_polling(drop_pending_updates=True)
            print("[Telegram] Bot started and polling")
        except Exception as e:
            print(f"[Telegram] Failed to start bot: {e}")
    else:
        print("[Telegram] No token set — bot disabled")

    yield

    if _bot_app:
        await _bot_app.updater.stop()
        await _bot_app.stop()
        await _bot_app.shutdown()

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
