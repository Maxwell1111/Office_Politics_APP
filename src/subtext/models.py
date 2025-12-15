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


# ========================================
# NEW: Automated Power Map Models (Google Workspace Integration)
# ========================================

class EmailInteraction(BaseModel):
    """Metadata from an email interaction (no body content)"""
    from_email: str
    to_emails: List[str]
    cc_emails: List[str] = Field(default_factory=list)
    timestamp: datetime
    thread_id: Optional[str] = None
    is_reply: bool = False
    response_time_hours: Optional[float] = None


class MeetingCluster(BaseModel):
    """Group of people who meet together frequently"""
    participants: List[str]
    meeting_count: int
    avg_duration_minutes: float
    meeting_titles: List[str] = Field(default_factory=list)


class NetworkNode(BaseModel):
    """A person in the organizational network graph"""
    email: str
    name: Optional[str] = None
    interaction_count: int = 0
    centrality_score: float = Field(0.0, description="How central/influential this person is in the network")
    betweenness_score: float = Field(0.0, description="How much this person bridges different groups")
    is_manager: bool = False
    is_direct_report: bool = False
    is_user: bool = False


class NetworkEdge(BaseModel):
    """Connection between two people in the network"""
    from_email: str
    to_email: str
    interaction_count: int
    email_frequency: int = 0  # How many emails
    meeting_frequency: int = 0  # How many meetings together
    reciprocity_score: float = Field(0.0, ge=0.0, le=1.0, description="How mutual is this relationship (0-1)")
    avg_response_time_hours: Optional[float] = None
    strength: float = Field(0.0, description="Overall edge weight/strength")


class StructuralHole(BaseModel):
    """A missing connection that could increase influence"""
    person_email: str
    person_name: Optional[str] = None
    centrality_score: float
    mutual_connections: List[str] = Field(default_factory=list, description="People who connect you to this person")
    strategic_value: str = Field(description="Why this connection is valuable")
    recommended_approach: str = Field(description="How to build this connection")


class NetworkInsight(BaseModel):
    """Strategic insight about network position"""
    insight_type: str  # "structural_hole", "managing_up", "managing_down", "game_theory"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    actionable_step: str
    related_people: List[str] = Field(default_factory=list)


class ManagerAnalysis(BaseModel):
    """Analysis of relationship with manager"""
    manager_email: str
    manager_name: Optional[str] = None
    your_interaction_frequency: int = Field(description="Your emails/meetings with manager per week")
    peer_avg_frequency: float = Field(description="Average peer interaction with manager")
    communication_balance: str = Field(description="over_communicating, balanced, under_communicating")
    response_time_trend: str = Field(description="improving, stable, declining")
    recommendations: List[str] = Field(default_factory=list)


class DirectReportAnalysis(BaseModel):
    """Analysis of relationships with direct reports"""
    report_email: str
    report_name: Optional[str] = None
    interaction_frequency: int
    isolation_risk: str = Field(description="low, medium, high")
    network_connectivity: float = Field(description="How connected they are to the broader team")
    recommendations: List[str] = Field(default_factory=list)


class AutomatedPowerMap(BaseModel):
    """Complete automated power map from Google Workspace data"""
    id: str
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    structural_holes: List[StructuralHole]
    insights: List[NetworkInsight]
    manager_analysis: Optional[ManagerAnalysis] = None
    direct_report_analyses: List[DirectReportAnalysis] = Field(default_factory=list)
    data_period_days: int = Field(description="How many days of data analyzed")
    total_emails_analyzed: int
    total_meetings_analyzed: int
    created_at: datetime = Field(default_factory=utc_now)


class IngestGoogleWorkspaceRequest(BaseModel):
    """Request to ingest Google Workspace data"""
    gmail_access_token: str = Field(description="Google OAuth token with Gmail API access")
    calendar_access_token: Optional[str] = Field(None, description="Google OAuth token for Calendar (can be same as Gmail)")
    days_back: int = Field(default=30, ge=7, le=90, description="How many days of data to analyze")
    user_email: str = Field(description="User's email address")
    manager_email: Optional[str] = Field(None, description="Manager's email for managing-up analysis")
    direct_report_emails: List[str] = Field(default_factory=list, description="Direct reports for managing-down analysis")
