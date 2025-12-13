"""
Stakeholder tracking API routes
Track people in your organization with encrypted notes
"""

from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from subtext.models import (
    Stakeholder,
    InteractionLog,
    CreateStakeholderRequest,
    CreateInteractionRequest,
)
from subtext.security import encrypt_text, decrypt_text, sanitize_input

router = APIRouter(tags=["stakeholders"])

# In-memory storage (will be database later)
stakeholders: dict[str, Stakeholder] = {}
interactions: dict[str, InteractionLog] = {}


@router.post("/stakeholders", response_model=Stakeholder)
async def create_stakeholder(request: CreateStakeholderRequest) -> Stakeholder:
    """Create a new stakeholder with encrypted notes"""

    # Sanitize and encrypt sensitive data
    notes_encrypted = None
    if request.notes:
        sanitized_notes = sanitize_input(request.notes)
        notes_encrypted = encrypt_text(sanitized_notes)

    stakeholder = Stakeholder(
        id=str(uuid.uuid4()),
        name=request.name,
        role=request.role,
        relationship_status=request.relationship_status,
        influence_level=request.influence_level,
        core_motivations=request.core_motivations,
        notes_encrypted=notes_encrypted,
    )

    stakeholders[stakeholder.id] = stakeholder
    return stakeholder


@router.get("/stakeholders", response_model=List[Stakeholder])
async def list_stakeholders() -> List[Stakeholder]:
    """List all stakeholders (notes remain encrypted)"""
    return list(stakeholders.values())


@router.get("/stakeholders/{stakeholder_id}", response_model=Stakeholder)
async def get_stakeholder(stakeholder_id: str) -> Stakeholder:
    """Get a specific stakeholder"""
    if stakeholder_id not in stakeholders:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    return stakeholders[stakeholder_id]


@router.get("/stakeholders/{stakeholder_id}/notes-decrypted")
async def get_decrypted_notes(stakeholder_id: str) -> dict:
    """Get decrypted notes for a stakeholder (separate endpoint for security)"""
    if stakeholder_id not in stakeholders:
        raise HTTPException(status_code=404, detail="Stakeholder not found")

    stakeholder = stakeholders[stakeholder_id]
    decrypted = decrypt_text(stakeholder.notes_encrypted) if stakeholder.notes_encrypted else ""

    return {"notes": decrypted}


@router.delete("/stakeholders/{stakeholder_id}")
async def delete_stakeholder(stakeholder_id: str) -> dict:
    """Delete a stakeholder"""
    if stakeholder_id not in stakeholders:
        raise HTTPException(status_code=404, detail="Stakeholder not found")

    del stakeholders[stakeholder_id]
    return {"message": "Stakeholder deleted"}


@router.post("/stakeholders/{stakeholder_id}/interactions", response_model=InteractionLog)
async def log_interaction(stakeholder_id: str, request: CreateInteractionRequest) -> InteractionLog:
    """Log an interaction with a stakeholder"""
    if stakeholder_id not in stakeholders:
        raise HTTPException(status_code=404, detail="Stakeholder not found")

    # Encrypt description
    sanitized = sanitize_input(request.description)
    encrypted_desc = encrypt_text(sanitized)

    interaction = InteractionLog(
        id=str(uuid.uuid4()),
        stakeholder_id=stakeholder_id,
        interaction_type=request.interaction_type,
        description_encrypted=encrypted_desc,
        sentiment=request.sentiment,
    )

    interactions[interaction.id] = interaction
    return interaction


@router.get("/stakeholders/{stakeholder_id}/interactions", response_model=List[InteractionLog])
async def list_interactions(stakeholder_id: str) -> List[InteractionLog]:
    """List all interactions for a stakeholder"""
    return [i for i in interactions.values() if i.stakeholder_id == stakeholder_id]
