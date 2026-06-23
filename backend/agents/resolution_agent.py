"""
Agent 3 — Resolution Agent
Triggered when an issue reaches CONFIRMED status (5+ citizen confirmations).
Pipeline: identify authority → draft formal letter → send email → update DB.
"""
from services.gemini_service import identify_authority as gemini_identify_authority
from services.gemini_service import draft_escalation_letter
from services.authority_service import lookup_authority
from services.email_service import send_escalation_email
from database import get_issue, update_issue_escalated, get_issues_ready_for_escalation
import asyncio


def _get_authority(issue: dict) -> dict:
    """Lookup table first (instant, zero quota), Gemini as fallback for unknowns."""
    loc = issue.get("location_name", "")
    for city in ["Bengaluru", "Mumbai", "Hyderabad"]:
        if city in loc:
            return lookup_authority(city, issue["category"])
    # Unknown city — use Gemini
    return gemini_identify_authority(issue)


async def escalate_issue(issue_id: int) -> dict:
    issue = get_issue(issue_id)
    if not issue:
        return {"success": False, "error": "Issue not found"}
    if issue["status"] != "CONFIRMED":
        return {"success": False, "error": f"Status is '{issue['status']}', expected CONFIRMED"}

    print(f"[Resolution] Escalating #{issue_id}: {issue['title']}")

    # Step 1: identify authority (lookup table → Gemini fallback)
    authority = _get_authority(issue)
    print(f"[Resolution] Authority → {authority['authority_name']} <{authority['email']}>")

    # Step 2: draft formal letter with Gemini Pro
    letter = draft_escalation_letter(issue, authority, issue["confirmation_count"])

    # Step 3: dispatch email
    email_sent = send_escalation_email(
        authority["email"],
        authority["authority_name"],
        letter,
        issue["title"],
    )

    # Step 4: persist escalation state
    update_issue_escalated(issue_id, authority["authority_name"], authority["email"], letter)

    return {
        "success": True,
        "issue_id": issue_id,
        "authority": authority,
        "letter_preview": letter[:400] + ("..." if len(letter) > 400 else ""),
        "email_sent": email_sent,
    }

async def run_batch_escalation() -> list:
    """Process all confirmed issues that haven't been escalated yet."""
    ready = get_issues_ready_for_escalation()
    print(f"[Resolution] {len(ready)} issue(s) ready for escalation")
    results = []
    for i, issue in enumerate(ready):
        if i > 0:
            await asyncio.sleep(20)  # avoid Gemini rate limit between escalations
        result = await escalate_issue(issue["id"])
        results.append(result)
    return results
