"""
Tone Decoder API routes - Feature A
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, Player, Interaction, DecodedMessage
from ..schemas import ToneDecoderRequest, ToneDecoderResponse, DecodedMessageResponse
from ..auth import get_current_user
from ..ai_service import ai_service
from ..encryption import encrypt_if_key_exists

router = APIRouter(prefix="/tone-decoder", tags=["Tone Decoder"])


@router.post("/analyze", response_model=ToneDecoderResponse)
async def analyze_message(
    request: ToneDecoderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decode a message to extract subtext, assess risk, and suggest a strategic response.

    This is the core "Tone Decoder" feature - analyzes communications with
    Machiavellian strategic advice.
    """
    player_info = None
    context_interactions = []

    # If player_id provided, get player info and interaction history
    if request.player_id:
        player_info = db.query(Player).filter(
            Player.id == request.player_id,
            Player.user_id == current_user.id
        ).first()

        if not player_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )

        # Get recent interactions with this player for context
        if request.include_context:
            context_interactions = db.query(Interaction).filter(
                Interaction.user_id == current_user.id,
                Interaction.player_id == request.player_id
            ).order_by(Interaction.interaction_date.desc()).limit(10).all()

    # Call AI service
    try:
        analysis = ai_service.decode_message(
            message_text=request.original_text,
            sender_name=request.sender_name,
            sender_role=request.sender_role,
            context_interactions=context_interactions,
            player_info=player_info,
            encryption_key=current_user.encryption_key
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )

    # Save decoded message to database
    encrypted_text = encrypt_if_key_exists(request.original_text, current_user.encryption_key)
    decoded_msg = DecodedMessage(
        user_id=current_user.id,
        player_id=request.player_id,
        original_text=encrypted_text,
        subtext_analysis=analysis["subtext"],
        risk_level=analysis["risk_level"],
        suggested_reply=analysis["suggested_reply"],
        context_used=analysis["context_used"]
    )
    db.add(decoded_msg)
    db.commit()

    return ToneDecoderResponse(
        subtext=analysis["subtext"],
        risk_level=analysis["risk_level"],
        suggested_reply=analysis["suggested_reply"],
        follow_up_actions=analysis.get("follow_up_actions"),
        context_used=analysis.get("context_used")
    )


@router.get("/history", response_model=List[DecodedMessageResponse])
async def get_decoded_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get history of decoded messages for the current user.
    """
    decoded_messages = db.query(DecodedMessage).filter(
        DecodedMessage.user_id == current_user.id
    ).order_by(DecodedMessage.created_at.desc()).limit(limit).all()

    # Decrypt original text before returning
    results = []
    for msg in decoded_messages:
        msg_dict = msg.__dict__.copy()
        # Decrypt if needed
        if current_user.encryption_key and msg.original_text:
            from ..encryption import decrypt_if_key_exists
            msg_dict["original_text"] = decrypt_if_key_exists(msg.original_text, current_user.encryption_key)
        results.append(DecodedMessageResponse(**msg_dict))

    return results


@router.get("/history/{message_id}", response_model=DecodedMessageResponse)
async def get_decoded_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific decoded message by ID.
    """
    decoded_msg = db.query(DecodedMessage).filter(
        DecodedMessage.id == message_id,
        DecodedMessage.user_id == current_user.id
    ).first()

    if not decoded_msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decoded message not found"
        )

    # Decrypt original text
    msg_dict = decoded_msg.__dict__.copy()
    if current_user.encryption_key and decoded_msg.original_text:
        from ..encryption import decrypt_if_key_exists
        msg_dict["original_text"] = decrypt_if_key_exists(decoded_msg.original_text, current_user.encryption_key)

    return DecodedMessageResponse(**msg_dict)
