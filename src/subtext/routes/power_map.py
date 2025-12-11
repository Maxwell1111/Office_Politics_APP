"""
Power Map API routes - Feature B (Relationship Database)
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, Player, PowerRelationship
from ..schemas import (
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PowerRelationshipCreate,
    PowerRelationshipUpdate,
    PowerRelationshipResponse,
    PowerMapResponse,
    PowerMapNode,
    PowerMapEdge
)
from ..auth import get_current_user
from ..encryption import encrypt_if_key_exists, decrypt_if_key_exists

router = APIRouter(prefix="/power-map", tags=["Power Map"])


# ============================================================================
# Player CRUD Operations
# ============================================================================

@router.post("/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player_data: PlayerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new player (colleague/stakeholder) in the user's power map.
    """
    # Check for duplicate name
    existing = db.query(Player).filter(
        Player.user_id == current_user.id,
        Player.name == player_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player with name '{player_data.name}' already exists"
        )

    # Encrypt notes if provided
    encrypted_notes = encrypt_if_key_exists(player_data.notes, current_user.encryption_key)

    new_player = Player(
        user_id=current_user.id,
        name=player_data.name,
        role=player_data.role,
        department=player_data.department,
        influence_level=player_data.influence_level,
        relationship_status=player_data.relationship_status,
        reports_to_player_id=player_data.reports_to_player_id,
        notes=encrypted_notes
    )

    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    return PlayerResponse.model_validate(new_player)


@router.get("/players", response_model=List[PlayerResponse])
async def list_players(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all players in the user's power map.
    """
    players = db.query(Player).filter(Player.user_id == current_user.id).all()

    # Decrypt notes before returning
    results = []
    for player in players:
        player_dict = player.__dict__.copy()
        if player.notes:
            player_dict["notes"] = decrypt_if_key_exists(player.notes, current_user.encryption_key)
        results.append(PlayerResponse(**player_dict))

    return results


@router.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific player by ID.
    """
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.user_id == current_user.id
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    # Decrypt notes
    player_dict = player.__dict__.copy()
    if player.notes:
        player_dict["notes"] = decrypt_if_key_exists(player.notes, current_user.encryption_key)

    return PlayerResponse(**player_dict)


@router.patch("/players/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: UUID,
    player_data: PlayerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a player's information.
    """
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.user_id == current_user.id
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    # Update fields
    update_data = player_data.model_dump(exclude_unset=True)

    # Encrypt notes if being updated
    if "notes" in update_data and update_data["notes"] is not None:
        update_data["notes"] = encrypt_if_key_exists(update_data["notes"], current_user.encryption_key)

    for field, value in update_data.items():
        setattr(player, field, value)

    db.commit()
    db.refresh(player)

    # Decrypt notes for response
    player_dict = player.__dict__.copy()
    if player.notes:
        player_dict["notes"] = decrypt_if_key_exists(player.notes, current_user.encryption_key)

    return PlayerResponse(**player_dict)


@router.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a player from the power map.
    """
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.user_id == current_user.id
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    db.delete(player)
    db.commit()

    return None


# ============================================================================
# Power Relationship Operations
# ============================================================================

@router.post("/relationships", response_model=PowerRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_power_relationship(
    relationship_data: PowerRelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new power relationship (informal influence) between two players.
    """
    # Verify both players belong to current user
    from_player = db.query(Player).filter(
        Player.id == relationship_data.from_player_id,
        Player.user_id == current_user.id
    ).first()

    to_player = db.query(Player).filter(
        Player.id == relationship_data.to_player_id,
        Player.user_id == current_user.id
    ).first()

    if not from_player or not to_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both players not found"
        )

    # Check for existing relationship
    existing = db.query(PowerRelationship).filter(
        PowerRelationship.user_id == current_user.id,
        PowerRelationship.from_player_id == relationship_data.from_player_id,
        PowerRelationship.to_player_id == relationship_data.to_player_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relationship already exists between these players"
        )

    new_relationship = PowerRelationship(
        user_id=current_user.id,
        from_player_id=relationship_data.from_player_id,
        to_player_id=relationship_data.to_player_id,
        influence_type=relationship_data.influence_type,
        strength=relationship_data.strength,
        notes=relationship_data.notes
    )

    db.add(new_relationship)
    db.commit()
    db.refresh(new_relationship)

    return PowerRelationshipResponse.model_validate(new_relationship)


@router.get("/relationships", response_model=List[PowerRelationshipResponse])
async def list_power_relationships(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all power relationships in the user's map.
    """
    relationships = db.query(PowerRelationship).filter(
        PowerRelationship.user_id == current_user.id
    ).all()

    return [PowerRelationshipResponse.model_validate(r) for r in relationships]


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_power_relationship(
    relationship_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a power relationship.
    """
    relationship = db.query(PowerRelationship).filter(
        PowerRelationship.id == relationship_id,
        PowerRelationship.user_id == current_user.id
    ).first()

    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found"
        )

    db.delete(relationship)
    db.commit()

    return None


# ============================================================================
# Power Map Visualization
# ============================================================================

@router.get("/visualization", response_model=PowerMapResponse)
async def get_power_map_visualization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete power map data for visualization (nodes and edges).

    Nodes: All players with their attributes
    Edges: Both formal (org chart) and informal (power relationships)
    """
    # Get all players (nodes)
    players = db.query(Player).filter(Player.user_id == current_user.id).all()
    nodes = [
        PowerMapNode(
            id=p.id,
            name=p.name,
            role=p.role,
            influence_level=p.influence_level,
            relationship_status=p.relationship_status,
            reports_to_player_id=p.reports_to_player_id
        )
        for p in players
    ]

    # Get edges
    edges = []

    # 1. Formal org chart relationships
    for player in players:
        if player.reports_to_player_id:
            edges.append(PowerMapEdge(
                from_player_id=player.id,
                to_player_id=player.reports_to_player_id,
                influence_type="reports_to",
                strength=5,  # Default strength for formal relationships
                is_formal=True
            ))

    # 2. Informal power relationships
    relationships = db.query(PowerRelationship).filter(
        PowerRelationship.user_id == current_user.id
    ).all()

    for rel in relationships:
        edges.append(PowerMapEdge(
            from_player_id=rel.from_player_id,
            to_player_id=rel.to_player_id,
            influence_type=rel.influence_type,
            strength=rel.strength,
            is_formal=False
        ))

    return PowerMapResponse(nodes=nodes, edges=edges)
