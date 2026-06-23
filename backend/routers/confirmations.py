from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import base64
from agents.confirmation_agent import process_confirmation
from agents.resolution_agent import escalate_issue

router = APIRouter(prefix="/api/confirm", tags=["confirmations"])

@router.post("/{issue_id}")
async def confirm_issue(
    issue_id: int,
    citizen_note: str = Form(default=""),
    photo: Optional[UploadFile] = File(default=None),
):
    photo_base64 = ""
    if photo:
        content = await photo.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Photo too large (max 5MB)")
        photo_base64 = base64.b64encode(content).decode("utf-8")

    result = await process_confirmation(issue_id, photo_base64, citizen_note)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    if result.get("ready_for_escalation"):
        await escalate_issue(issue_id)

    return result
