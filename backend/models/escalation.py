from pydantic import BaseModel
from typing import Optional

class AuthorityInfo(BaseModel):
    authority_name: str
    authority_type: str
    department: str
    email: str
    reasoning: str

class EscalationResponse(BaseModel):
    success: bool
    issue_id: Optional[int] = None
    authority: Optional[AuthorityInfo] = None
    letter_preview: Optional[str] = None
    email_sent: Optional[bool] = None
    error: Optional[str] = None

class StatsResponse(BaseModel):
    total_issues: int
    discovered: int
    confirmed: int
    escalated: int
    resolved: int
    total_citizen_confirmations: int
