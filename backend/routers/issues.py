from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_all_issues, get_issue, get_stats

router = APIRouter(prefix="/api/issues", tags=["issues"])

@router.get("")
def list_issues(status: Optional[str] = Query(None)):
    issues = get_all_issues(status)
    return {"issues": issues, "total": len(issues)}

@router.get("/stats")
def issue_stats():
    return get_stats()

@router.get("/{issue_id}")
def get_issue_detail(issue_id: int):
    issue = get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue
