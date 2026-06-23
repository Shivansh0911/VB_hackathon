from fastapi import APIRouter, HTTPException
from agents.discovery_agent import run_all_cities
from agents.resolution_agent import escalate_issue, run_batch_escalation
from database import get_all_issues

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/trigger-discovery")
async def trigger_discovery():
    """Trigger the discovery agent. Falls back to example issues if no real data found."""
    results = await run_all_cities()
    total_new = sum(results.values())

    # If Gemini quota exhausted or all sources empty and DB is still empty, load examples
    if total_new == 0 and not get_all_issues():
        from seed_data import seed_database
        seed_database()
        return {"status": "completed", "new_issues_by_city": results, "fallback": "example_issues_loaded"}

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
