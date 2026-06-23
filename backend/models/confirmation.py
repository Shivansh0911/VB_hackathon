from pydantic import BaseModel
from typing import Optional

class ConfirmationCreate(BaseModel):
    citizen_note: Optional[str] = ""

class ValidationResult(BaseModel):
    valid: bool
    confidence: int
    reasoning: str
    detected_issue: str

class ConfirmationResponse(BaseModel):
    success: bool
    validation: Optional[ValidationResult] = None
    new_confirmation_count: int
    new_confidence_score: int
    new_status: str
    ready_for_escalation: bool
    error: Optional[str] = None
