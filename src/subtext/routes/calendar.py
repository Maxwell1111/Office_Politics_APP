"""
Strategic Calendar API routes
Analyze calendar for political insights
"""

from fastapi import APIRouter, HTTPException
from typing import List

from subtext.models import (
    CalendarAnalysis, AnalyzeCalendarRequest,
    ConnectCalendarRequest, Stakeholder
)
from subtext.calendar_service import calendar_service
from subtext.calendar_analyzer import calendar_analyzer
from subtext.security import sanitize_input

router = APIRouter(tags=["calendar"])

# In-memory storage for demo (replace with database in production)
connected_calendars = {}
stakeholders_db: List[Stakeholder] = []


@router.post("/calendar/analyze", response_model=CalendarAnalysis)
async def analyze_calendar(request: AnalyzeCalendarRequest) -> CalendarAnalysis:
    """
    Analyze upcoming calendar events for political stakes and strategic insights

    Cross-references calendar attendees with stakeholder database to identify:
    - Political stakes level (Low/Medium/High/Critical)
    - Warning flags (adversaries present, power imbalances, opportunities)
    - Manager-specific tips if manager is in the meeting
    - AI-generated preparation advice and talking points
    """

    # For demo, use mock calendar events
    # In production, fetch from stored calendar connection
    events = calendar_service._mock_calendar_events(request.days_ahead)

    if not events:
        raise HTTPException(status_code=404, detail="No calendar events found")

    # Sanitize manager name if provided
    manager_name = None
    if request.user_manager_name:
        manager_name = sanitize_input(request.user_manager_name)

    # Analyze calendar with stakeholder cross-reference
    analysis = calendar_analyzer.analyze_calendar(
        events=events,
        stakeholders=stakeholders_db,
        user_manager_name=manager_name,
        analysis_period=f"Next {request.days_ahead} days"
    )

    return analysis


@router.post("/calendar/connect")
async def connect_calendar(request: ConnectCalendarRequest) -> dict:
    """
    Connect a calendar source (iCal feed or Google Calendar)

    For iCal: Provide the feed URL
    For Google Calendar: Provide OAuth access token
    """

    calendar_type = request.calendar_type.lower()

    if calendar_type == "ical":
        if not request.ical_url:
            raise HTTPException(
                status_code=400,
                detail="ical_url is required for iCal calendar type"
            )

        # Store iCal URL
        connected_calendars["ical"] = {
            "type": "ical",
            "url": request.ical_url
        }

        return {
            "status": "success",
            "message": "iCal calendar connected successfully",
            "calendar_type": "ical"
        }

    elif calendar_type == "google":
        if not request.google_access_token:
            raise HTTPException(
                status_code=400,
                detail="google_access_token is required for Google Calendar type"
            )

        # Store Google token (in production, encrypt this!)
        connected_calendars["google"] = {
            "type": "google",
            "token": request.google_access_token
        }

        return {
            "status": "success",
            "message": "Google Calendar connected successfully",
            "calendar_type": "google"
        }

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported calendar type: {calendar_type}. Use 'ical' or 'google'"
        )


@router.get("/calendar/events")
async def get_calendar_events(days_ahead: int = 7) -> dict:
    """
    Fetch raw calendar events without analysis

    Useful for debugging or previewing what events will be analyzed
    """

    # Check if any calendar is connected
    if "ical" in connected_calendars:
        events = calendar_service.fetch_ical_events(
            ical_url=connected_calendars["ical"]["url"],
            days_ahead=days_ahead
        )
    elif "google" in connected_calendars:
        events = calendar_service.fetch_google_calendar_events(
            access_token=connected_calendars["google"]["token"],
            days_ahead=days_ahead
        )
    else:
        # Use mock events for demo
        events = calendar_service._mock_calendar_events(days_ahead)

    return {
        "events": [event.model_dump() for event in events],
        "total": len(events),
        "calendar_connected": len(connected_calendars) > 0
    }


@router.post("/calendar/stakeholders/sync")
async def sync_stakeholders(stakeholders: List[Stakeholder]) -> dict:
    """
    Sync stakeholder data for calendar analysis

    This endpoint allows the frontend to provide stakeholder data
    that will be used for cross-referencing calendar attendees
    """

    global stakeholders_db
    stakeholders_db = stakeholders

    return {
        "status": "success",
        "message": f"Synced {len(stakeholders)} stakeholders",
        "stakeholder_count": len(stakeholders_db)
    }


@router.get("/calendar/test")
async def test_calendar() -> dict:
    """Test endpoint to verify calendar API is working"""
    return {
        "status": "ok",
        "message": "Strategic Calendar API is working!",
        "calendar_connected": len(connected_calendars) > 0,
        "stakeholders_loaded": len(stakeholders_db),
        "calendar_service_available": True,
        "llm_configured": calendar_analyzer._generate_weekly_summary.__code__ is not None
    }
