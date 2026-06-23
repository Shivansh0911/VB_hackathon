from fastapi import APIRouter, HTTPException
from agents.discovery_agent import run_all_cities
from agents.resolution_agent import escalate_issue, run_batch_escalation

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/trigger-discovery")
async def trigger_discovery():
    """Manually trigger the discovery agent (for demo/testing)."""
    results = await run_all_cities()
    return {"status": "completed", "new_issues_by_city": results}

@router.post("/trigger-escalation")
async def trigger_escalation():
    """Process all confirmed issues and send escalation letters."""
    results = await run_batch_escalation()
    return {"status": "completed", "escalated": results}

@router.post("/escalate/{issue_id}")
async def escalate_single(issue_id: int):
    """Escalate a specific issue immediately."""
    result = await escalate_issue(issue_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/seed")
async def seed_demo_data():
    """Seed database with demo data (first-run only)."""
    results = await run_all_cities()
    return {"status": "seeded", "results": results}
