"""
Agent 2 — Confirmation Agent
Validates citizen photo uploads with Gemini Vision, updates confidence scores.
"""
from services.gemini_service import validate_photo_for_issue
from database import get_issue, add_confirmation

async def process_confirmation(issue_id: int, photo_base64: str, citizen_note: str = "") -> dict:
    issue = get_issue(issue_id)
    if not issue:
        return {"success": False, "error": "Issue not found"}

    if issue["status"] in ("ESCALATED", "RESOLVED"):
        return {"success": False, "error": "Issue already escalated or resolved"}

    validation = {"valid": True, "confidence": 75, "reasoning": "No photo provided", "detected_issue": ""}
    if photo_base64:
        validation = validate_photo_for_issue(photo_base64, issue["category"], issue["title"])

    confirmation_data = {
        "photo_url": "",
        "gemini_validation": validation.get("reasoning", ""),
        "validation_passed": validation.get("valid", True) and validation.get("confidence", 0) >= 60,
        "citizen_note": citizen_note,
    }
    add_confirmation(issue_id, confirmation_data)

    updated = get_issue(issue_id)
    return {
        "success": True,
        "validation": validation,
        "new_confirmation_count": updated["confirmation_count"],
        "new_confidence_score": updated["confidence_score"],
        "new_status": updated["status"],
        "ready_for_escalation": updated["status"] == "CONFIRMED",
    }
