"""
Log Book API routes - Feature C (Context Memory / Interaction Timeline)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, Player, Interaction
from ..schemas import InteractionCreate, InteractionUpdate, InteractionResponse
from ..auth import get_current_user
from ..encryption import encrypt_if_key_exists, decrypt_if_key_exists

router = APIRouter(prefix="/logbook", tags=["Log Book"])


@router.post("/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a new interaction (meeting, email, incident, etc.).

    This creates a timestamped record that will be used as context
    for future Tone Decoder analyses.
    """
    # Verify player exists if player_id provided
    if interaction_data.player_id:
        player = db.query(Player).filter(
            Player.id == interaction_data.player_id,
            Player.user_id == current_user.id
        ).first()

        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )

    # Encrypt description
    encrypted_description = encrypt_if_key_exists(
        interaction_data.description,
        current_user.encryption_key
    )

    new_interaction = Interaction(
        user_id=current_user.id,
        player_id=interaction_data.player_id,
        title=interaction_data.title,
        description=encrypted_description,
        interaction_type=interaction_data.interaction_type,
        sentiment=interaction_data.sentiment,
        risk_level=interaction_data.risk_level,
        tags=interaction_data.tags,
        interaction_date=interaction_data.interaction_date
    )

    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    # Decrypt for response
    interaction_dict = new_interaction.__dict__.copy()
    interaction_dict["description"] = decrypt_if_key_exists(
        new_interaction.description,
        current_user.encryption_key
    )

    return InteractionResponse(**interaction_dict)


@router.get("/interactions", response_model=List[InteractionResponse])
async def list_interactions(
    player_id: Optional[UUID] = Query(None, description="Filter by player ID"),
    interaction_type: Optional[str] = Query(None, description="Filter by type (email, meeting, slack, other)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (low, medium, high)"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get interaction log entries with optional filters.

    Returns most recent interactions first.
    """
    query = db.query(Interaction).filter(Interaction.user_id == current_user.id)

    # Apply filters
    if player_id:
        query = query.filter(Interaction.player_id == player_id)
    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)
    if risk_level:
        query = query.filter(Interaction.risk_level == risk_level)

    interactions = query.order_by(Interaction.interaction_date.desc()).limit(limit).all()

    # Decrypt descriptions
    results = []
    for interaction in interactions:
        interaction_dict = interaction.__dict__.copy()
        interaction_dict["description"] = decrypt_if_key_exists(
            interaction.description,
            current_user.encryption_key
        )
        results.append(InteractionResponse(**interaction_dict))

    return results


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific interaction by ID.
    """
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id,
        Interaction.user_id == current_user.id
    ).first()

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )

    # Decrypt description
    interaction_dict = interaction.__dict__.copy()
    interaction_dict["description"] = decrypt_if_key_exists(
        interaction.description,
        current_user.encryption_key
    )

    return InteractionResponse(**interaction_dict)


@router.patch("/interactions/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: UUID,
    interaction_data: InteractionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing interaction log entry.
    """
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id,
        Interaction.user_id == current_user.id
    ).first()

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )

    # Update fields
    update_data = interaction_data.model_dump(exclude_unset=True)

    # Encrypt description if being updated
    if "description" in update_data and update_data["description"] is not None:
        update_data["description"] = encrypt_if_key_exists(
            update_data["description"],
            current_user.encryption_key
        )

    for field, value in update_data.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)

    # Decrypt for response
    interaction_dict = interaction.__dict__.copy()
    interaction_dict["description"] = decrypt_if_key_exists(
        interaction.description,
        current_user.encryption_key
    )

    return InteractionResponse(**interaction_dict)


@router.delete("/interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an interaction from the log book.
    """
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id,
        Interaction.user_id == current_user.id
    ).first()

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )

    db.delete(interaction)
    db.commit()

    return None


@router.get("/players/{player_id}/timeline", response_model=List[InteractionResponse])
async def get_player_timeline(
    player_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get interaction timeline for a specific player.

    Returns chronological history of all logged interactions with this person.
    """
    # Verify player exists and belongs to user
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.user_id == current_user.id
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    # Get interactions
    interactions = db.query(Interaction).filter(
        Interaction.user_id == current_user.id,
        Interaction.player_id == player_id
    ).order_by(Interaction.interaction_date.desc()).limit(limit).all()

    # Decrypt descriptions
    results = []
    for interaction in interactions:
        interaction_dict = interaction.__dict__.copy()
        interaction_dict["description"] = decrypt_if_key_exists(
            interaction.description,
            current_user.encryption_key
        )
        results.append(InteractionResponse(**interaction_dict))

    return results
