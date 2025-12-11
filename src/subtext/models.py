"""
SQLAlchemy ORM models for Subtext app
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User account"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    current_role = Column(String(255))
    company = Column(String(255))
    encryption_key = Column(Text)  # For encrypting sensitive data at rest
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    players = relationship("Player", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    power_relationships = relationship("PowerRelationship", back_populates="user", cascade="all, delete-orphan")
    decoded_messages = relationship("DecodedMessage", back_populates="user", cascade="all, delete-orphan")


class Player(Base):
    """Colleague/Stakeholder in user's organization"""

    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255))
    department = Column(String(255))
    influence_level = Column(Integer, CheckConstraint("influence_level BETWEEN 1 AND 10"))
    relationship_status = Column(
        String(50),
        CheckConstraint("relationship_status IN ('ally', 'neutral', 'rival', 'enemy', 'unknown')")
    )
    reports_to_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="SET NULL"))
    notes = Column(Text)  # Encrypted general notes
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_player_name'),
    )

    # Relationships
    user = relationship("User", back_populates="players")
    reports_to = relationship("Player", remote_side=[id], backref="direct_reports")
    interactions = relationship("Interaction", back_populates="player", cascade="all, delete-orphan")
    outgoing_relationships = relationship(
        "PowerRelationship",
        foreign_keys="PowerRelationship.from_player_id",
        back_populates="from_player",
        cascade="all, delete-orphan"
    )
    incoming_relationships = relationship(
        "PowerRelationship",
        foreign_keys="PowerRelationship.to_player_id",
        back_populates="to_player",
        cascade="all, delete-orphan"
    )


class Interaction(Base):
    """Log Book entry for user interactions with players"""

    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), index=True)
    interaction_date = Column(TIMESTAMP, server_default=func.now())
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)  # Encrypted
    interaction_type = Column(
        String(50),
        CheckConstraint("interaction_type IN ('email', 'meeting', 'slack', 'other')")
    )
    sentiment = Column(
        String(50),
        CheckConstraint("sentiment IN ('positive', 'neutral', 'negative', 'hostile')")
    )
    risk_level = Column(
        String(50),
        CheckConstraint("risk_level IN ('low', 'medium', 'high')")
    )
    tags = Column(ARRAY(String))  # Array of tags like ['credit-stealing', 'promotion-related']
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="interactions")
    player = relationship("Player", back_populates="interactions")


class PowerRelationship(Base):
    """Informal influence relationships beyond org chart"""

    __tablename__ = "power_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    from_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    to_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    influence_type = Column(String(100))  # e.g., 'mentorship', 'personal-friendship', 'political-alliance'
    strength = Column(Integer, CheckConstraint("strength BETWEEN 1 AND 10"))
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'from_player_id', 'to_player_id', name='uq_user_power_relationship'),
    )

    # Relationships
    user = relationship("User", back_populates="power_relationships")
    from_player = relationship("Player", foreign_keys=[from_player_id], back_populates="outgoing_relationships")
    to_player = relationship("Player", foreign_keys=[to_player_id], back_populates="incoming_relationships")


class DecodedMessage(Base):
    """Cache of tone decoder analyses"""

    __tablename__ = "decoded_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="SET NULL"))
    original_text = Column(Text, nullable=False)  # Encrypted
    subtext_analysis = Column(Text, nullable=False)
    risk_level = Column(
        String(50),
        CheckConstraint("risk_level IN ('low', 'medium', 'high')")
    )
    suggested_reply = Column(Text)
    context_used = Column(ARRAY(String))  # Array of interaction IDs used for context
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="decoded_messages")
