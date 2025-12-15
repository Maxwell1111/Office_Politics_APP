"""
Database models for Politico - Office Politics Navigator
Designed with security, privacy, and strategic analysis in mind
"""

from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


def utc_now():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


# Enums for structured data
class RelationshipStatus(str, Enum):
    """Relationship status with a stakeholder"""
    ALLY = "ally"
    NEUTRAL = "neutral"
    ADVERSARY = "adversary"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Risk level for scenarios"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StrategyType(str, Enum):
    """Strategy approach types"""
    PASSIVE = "passive"
    ASSERTIVE = "assertive"
    STRATEGIC = "strategic"


class Person(BaseModel):
    """A person in the organization"""
    id: str
    name: str
    title: str
    department: str
    influence_level: int = Field(ge=1, le=10, description="Influence level from 1-10")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Relationship(BaseModel):
    """A relationship between two people"""
    id: str
    from_person_id: str
    to_person_id: str
    relationship_type: str = Field(description="e.g., 'reports_to', 'allies', 'rivals', 'mentor'")
    strength: int = Field(ge=1, le=10, description="Relationship strength from 1-10")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PowerMap(BaseModel):
    """A complete power map"""
    id: str
    name: str
    description: Optional[str] = None
    people: list[Person] = []
    relationships: list[Relationship] = []
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# Request/Response models
class CreatePersonRequest(BaseModel):
    """Request to create a new person"""
    name: str
    title: str
    department: str
    influence_level: int = Field(ge=1, le=10)
    notes: Optional[str] = None


class CreateRelationshipRequest(BaseModel):
    """Request to create a new relationship"""
    from_person_id: str
    to_person_id: str
    relationship_type: str
    strength: int = Field(ge=1, le=10)
    notes: Optional[str] = None


class CreatePowerMapRequest(BaseModel):
    """Request to create a new power map"""
    name: str
    description: Optional[str] = None


# ========================================
# NEW: Stakeholder Tracking Models
# ========================================

class Stakeholder(BaseModel):
    """A stakeholder in the organization - someone to track politically"""
    id: str
    name: str
    role: str
    relationship_status: RelationshipStatus = RelationshipStatus.UNKNOWN
    influence_level: int = Field(ge=1, le=10, description="Political influence 1-10")
    core_motivations: List[str] = Field(default_factory=list, description="What drives them")
    notes_encrypted: Optional[str] = Field(None, description="Encrypted private notes")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class InteractionLog(BaseModel):
    """Log of interactions with a stakeholder"""
    id: str
    stakeholder_id: str
    interaction_type: str  # conflict, favor, meeting, email, etc.
    description_encrypted: Optional[str] = Field(None, description="Encrypted description")
    sentiment: str  # positive, neutral, negative
    created_at: datetime = Field(default_factory=utc_now)


class CreateStakeholderRequest(BaseModel):
    """Request to create a stakeholder"""
    name: str
    role: str
    relationship_status: RelationshipStatus = RelationshipStatus.UNKNOWN
    influence_level: int = Field(ge=1, le=10)
    core_motivations: List[str] = []
    notes: Optional[str] = None  # Will be encrypted server-side


class CreateInteractionRequest(BaseModel):
    """Request to log an interaction"""
    stakeholder_id: str
    interaction_type: str
    description: str  # Will be encrypted server-side
    sentiment: str


# ========================================
# NEW: Scenario Analysis Models
# ========================================

class StrategyOption(BaseModel):
    """A strategic option for handling a scenario"""
    strategy_type: StrategyType
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    recommended_actions: List[str]


class ScenarioAnalysis(BaseModel):
    """Analysis result from the LLM for a scenario"""
    id: str
    scenario_description: str
    power_dynamic: str  # Who holds power in this scenario
    risk_level: RiskLevel
    political_implications: str
    strategy_options: List[StrategyOption]
    created_at: datetime = Field(default_factory=utc_now)


class AnalyzeScenarioRequest(BaseModel):
    """Request to analyze a political scenario"""
    scenario_description: str = Field(..., min_length=10)
    stakeholders_involved: List[str] = []
    user_goal: str


# ========================================
# NEW: Tone Analysis Models
# ========================================

class ToneAnalysis(BaseModel):
    """Analysis of email/message tone"""
    id: str
    original_text: str
    aggression_score: int = Field(ge=0, le=100)
    passivity_score: int = Field(ge=0, le=100)
    political_implications: str
    suggested_rewrite: str
    created_at: datetime = Field(default_factory=utc_now)


class AnalyzeToneRequest(BaseModel):
    """Request to analyze tone of a message"""
    email_draft: str = Field(..., min_length=10)


# ========================================
# NEW: Strategic Calendar Models
# ========================================

class PoliticalStakesLevel(str, Enum):
    """Political stakes level for meetings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CalendarEvent(BaseModel):
    """A calendar event from user's schedule"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str] = Field(default_factory=list, description="List of attendee names/emails")
    location: Optional[str] = None
    description: Optional[str] = None
    is_recurring: bool = False


class MeetingWarning(BaseModel):
    """A warning/flag about a meeting"""
    type: str  # "adversary_present", "power_imbalance", "opportunity", "risk"
    message: str
    severity: PoliticalStakesLevel


class MeetingInsight(BaseModel):
    """Strategic insight for a specific meeting"""
    event_id: str
    event_title: str
    start_time: datetime
    political_stakes: PoliticalStakesLevel
    matched_stakeholders: List[str] = Field(default_factory=list, description="Stakeholder IDs found in attendees")
    total_influence_score: int = Field(ge=0, description="Sum of influence levels of all matched stakeholders")
    warnings: List[MeetingWarning] = Field(default_factory=list)
    manager_tips: Optional[str] = Field(None, description="Specific tips if manager is present")
    preparation_advice: str = Field(description="AI-generated advice for this meeting")
    talking_points: List[str] = Field(default_factory=list, description="Suggested talking points")


class CalendarAnalysis(BaseModel):
    """Complete calendar analysis for a time period"""
    id: str
    analysis_period: str = Field(description="e.g., 'Next 7 days'")
    total_meetings: int
    high_stakes_count: int
    meeting_insights: List[MeetingInsight]
    weekly_summary: str = Field(description="AI-generated strategic summary")
    created_at: datetime = Field(default_factory=utc_now)


class ConnectCalendarRequest(BaseModel):
    """Request to connect calendar"""
    calendar_type: str = Field(description="'google' or 'ical'")
    ical_url: Optional[str] = Field(None, description="iCal feed URL if using iCal")
    google_access_token: Optional[str] = Field(None, description="Google OAuth token if using Google Calendar")


class AnalyzeCalendarRequest(BaseModel):
    """Request to analyze calendar for strategic insights"""
    days_ahead: int = Field(default=7, ge=1, le=30, description="Number of days to analyze")
    user_manager_name: Optional[str] = Field(None, description="User's manager name for specific tips")
