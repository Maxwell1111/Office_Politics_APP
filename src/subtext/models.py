"""
Database models for Office Politics app
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


def utc_now():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


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
