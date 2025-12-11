"""
Pydantic schemas for API request/response validation
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    current_role: Optional[str] = None
    company: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================================
# Player Schemas
# ============================================================================

class PlayerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: Optional[str] = None
    department: Optional[str] = None
    influence_level: Optional[int] = Field(None, ge=1, le=10)
    relationship_status: Optional[str] = Field(None, pattern="^(ally|neutral|rival|enemy|unknown)$")
    reports_to_player_id: Optional[UUID] = None
    notes: Optional[str] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = None
    department: Optional[str] = None
    influence_level: Optional[int] = Field(None, ge=1, le=10)
    relationship_status: Optional[str] = Field(None, pattern="^(ally|neutral|rival|enemy|unknown)$")
    reports_to_player_id: Optional[UUID] = None
    notes: Optional[str] = None


class PlayerResponse(PlayerBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Interaction (Log Book) Schemas
# ============================================================================

class InteractionBase(BaseModel):
    player_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    interaction_type: Optional[str] = Field(None, pattern="^(email|meeting|slack|other)$")
    sentiment: Optional[str] = Field(None, pattern="^(positive|neutral|negative|hostile)$")
    risk_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = None
    interaction_date: Optional[datetime] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    player_id: Optional[UUID] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    interaction_type: Optional[str] = Field(None, pattern="^(email|meeting|slack|other)$")
    sentiment: Optional[str] = Field(None, pattern="^(positive|neutral|negative|hostile)$")
    risk_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = None
    interaction_date: Optional[datetime] = None


class InteractionResponse(InteractionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Power Relationship Schemas
# ============================================================================

class PowerRelationshipBase(BaseModel):
    from_player_id: UUID
    to_player_id: UUID
    influence_type: Optional[str] = Field(None, max_length=100)
    strength: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class PowerRelationshipCreate(PowerRelationshipBase):
    pass


class PowerRelationshipUpdate(BaseModel):
    influence_type: Optional[str] = Field(None, max_length=100)
    strength: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class PowerRelationshipResponse(PowerRelationshipBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Tone Decoder Schemas
# ============================================================================

class ToneDecoderRequest(BaseModel):
    original_text: str = Field(..., min_length=1)
    sender_name: Optional[str] = None
    sender_role: Optional[str] = None
    player_id: Optional[UUID] = None  # If sender is a known player
    include_context: bool = True  # Whether to pull interaction history


class ToneDecoderResponse(BaseModel):
    subtext: str
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    suggested_reply: str
    follow_up_actions: Optional[List[str]] = None
    context_used: Optional[List[str]] = None  # List of interaction titles used


class DecodedMessageResponse(BaseModel):
    id: UUID
    player_id: Optional[UUID]
    original_text: str
    subtext_analysis: str
    risk_level: str
    suggested_reply: Optional[str]
    context_used: Optional[List[str]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Power Map Schemas
# ============================================================================

class PowerMapNode(BaseModel):
    """Node in the power map visualization"""
    id: UUID
    name: str
    role: Optional[str]
    influence_level: Optional[int]
    relationship_status: Optional[str]
    reports_to_player_id: Optional[UUID]


class PowerMapEdge(BaseModel):
    """Edge in the power map visualization"""
    from_player_id: UUID
    to_player_id: UUID
    influence_type: Optional[str]
    strength: Optional[int]
    is_formal: bool  # True if org chart relationship, False if informal


class PowerMapResponse(BaseModel):
    """Complete power map for visualization"""
    nodes: List[PowerMapNode]
    edges: List[PowerMapEdge]
