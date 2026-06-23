from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class IssueStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    CONFIRMED = "CONFIRMED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"

class IssueCategory(str, Enum):
    POTHOLE = "POTHOLE"
    STREETLIGHT = "STREETLIGHT"
    WATER_LEAKAGE = "WATER_LEAKAGE"
    GARBAGE = "GARBAGE"
    BROKEN_FOOTPATH = "BROKEN_FOOTPATH"
    DRAINAGE = "DRAINAGE"
    TREE_FALLEN = "TREE_FALLEN"
    ROAD_DAMAGE = "ROAD_DAMAGE"
    OTHER = "OTHER"

class IssueBase(BaseModel):
    title: str
    category: IssueCategory
    description: str
    latitude: float
    longitude: float
    location_name: Optional[str] = ""

class IssueCreate(IssueBase):
    source_signals: Optional[List[str]] = []
    confidence_score: Optional[int] = 10

class IssueResponse(IssueBase):
    id: int
    source_signals: str
    confidence_score: int
    confirmation_count: int
    status: IssueStatus
    authority_name: Optional[str] = None
    authority_email: Optional[str] = None
    escalation_letter: Optional[str] = None
    escalation_sent_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
