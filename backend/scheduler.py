from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

scheduler = AsyncIOScheduler()

def start_scheduler():
    from agents.discovery_agent import run_all_cities
    from agents.resolution_agent import run_batch_escalation

    scheduler.add_job(
        lambda: asyncio.create_task(run_all_cities()),
        trigger=IntervalTrigger(hours=6),
        id="discovery",
        replace_existing=True,
    )
    scheduler.add_job(
        lambda: asyncio.create_task(run_batch_escalation()),
        trigger=IntervalTrigger(minutes=30),
        id="escalation",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] Started — discovery every 6h, escalation every 30min")
