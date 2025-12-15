"""
Automated Power Map API routes
Ingest Google Workspace data and build network graph
"""

from fastapi import APIRouter, HTTPException

from subtext.models import AutomatedPowerMap, IngestGoogleWorkspaceRequest
from subtext.gmail_ingestion import gmail_service
from subtext.calendar_service import calendar_service
from subtext.network_analyzer import network_analyzer
from subtext.google_oauth import google_oauth_service

router = APIRouter(tags=["automated-power-map"])


@router.post("/automated-power-map/ingest", response_model=AutomatedPowerMap)
async def ingest_workspace_data(request: IngestGoogleWorkspaceRequest) -> AutomatedPowerMap:
    """
    Ingest Google Workspace data and build automated power map

    **What this does:**
    1. Fetches Gmail metadata (From/To/CC only, NO body content)
    2. Fetches Calendar meeting attendance data
    3. Builds network graph with nodes (people) and edges (connections)
    4. Calculates centrality scores (who's most influential)
    5. Identifies structural holes (valuable missing connections)
    6. Analyzes manager relationship (over/under communicating)
    7. Analyzes direct reports (isolation risk)
    8. Generates AI-powered strategic insights

    **Privacy:** Only email headers are read, never body content
    **Game Theory:** Uses graph centrality and betweenness analysis
    **Actionable:** Provides specific next steps for each insight
    """

    try:
        # Step 1: Fetch Gmail metadata
        print(f"Fetching email metadata for past {request.days_back} days...")
        email_interactions = gmail_service.fetch_email_metadata(
            access_token=request.gmail_access_token,
            days_back=request.days_back,
            max_results=500
        )

        # Calculate response times
        email_interactions = gmail_service.calculate_response_times(email_interactions)

        print(f"Fetched {len(email_interactions)} email interactions")

        # Step 2: Fetch Calendar data
        print("Fetching calendar events...")
        calendar_token = request.calendar_access_token or request.gmail_access_token

        calendar_events = calendar_service.fetch_google_calendar_events(
            access_token=calendar_token,
            days_ahead=request.days_back  # Look back same period
        )

        print(f"Fetched {len(calendar_events)} calendar events")

        # Step 3: Build network graph and analyze
        print("Building network graph...")
        power_map = network_analyzer.build_power_map(
            email_interactions=email_interactions,
            calendar_events=calendar_events,
            user_email=request.user_email,
            manager_email=request.manager_email,
            direct_report_emails=request.direct_report_emails,
            days_analyzed=request.days_back
        )

        print(f"Generated power map with {len(power_map.nodes)} nodes and {len(power_map.edges)} edges")
        print(f"Identified {len(power_map.structural_holes)} structural holes")
        print(f"Generated {len(power_map.insights)} insights")

        return power_map

    except Exception as e:
        print(f"Error ingesting workspace data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest workspace data: {str(e)}"
        )


@router.get("/automated-power-map/test")
async def test_automated_power_map() -> dict:
    """Test endpoint to verify automated power map API is working"""
    return {
        "status": "ok",
        "message": "Automated Power Map API is working!",
        "features": [
            "Gmail metadata ingestion (no body content)",
            "Calendar meeting analysis",
            "Network graph construction",
            "Centrality and betweenness calculation",
            "Structural hole identification",
            "Manager relationship analysis",
            "Direct report isolation detection",
            "AI-powered strategic insights"
        ],
        "privacy": "Only email headers (From/To/CC/timestamps) are read, never body content",
        "algorithms": [
            "Graph centrality (degree-based)",
            "Betweenness centrality (bridge detection)",
            "Edge reciprocity scoring",
            "Community detection (structural holes)"
        ]
    }


@router.post("/automated-power-map/generate-from-oauth")
async def generate_from_oauth(
    user_id: str = "default_user",
    days_back: int = 30,
    manager_email: str = None,
    direct_report_emails: list[str] = None
) -> AutomatedPowerMap:
    """
    Generate power map using stored OAuth tokens

    Requires user to have connected Google account via /api/oauth/google/authorize

    Args:
        user_id: User identifier (defaults to "default_user")
        days_back: How many days of data to analyze (7-90)
        manager_email: Optional manager email for managing-up analysis
        direct_report_emails: Optional list of direct report emails
    """

    # Get valid access token
    access_token = google_oauth_service.get_valid_access_token(user_id)

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No connected Google account. Please authorize access first at /api/oauth/google/authorize"
        )

    try:
        # Get user's email
        user_email = google_oauth_service.get_user_email(access_token)

        # Fetch real data using OAuth token
        print(f"Fetching email metadata for {user_email}...")
        email_interactions = gmail_service.fetch_email_metadata(
            access_token=access_token,
            days_back=days_back,
            max_results=500
        )

        email_interactions = gmail_service.calculate_response_times(email_interactions)
        print(f"Fetched {len(email_interactions)} email interactions")

        print("Fetching calendar events...")
        calendar_events = calendar_service.fetch_google_calendar_events(
            access_token=access_token,
            days_ahead=days_back
        )
        print(f"Fetched {len(calendar_events)} calendar events")

        # Build power map
        power_map = network_analyzer.build_power_map(
            email_interactions=email_interactions,
            calendar_events=calendar_events,
            user_email=user_email,
            manager_email=manager_email,
            direct_report_emails=direct_report_emails or [],
            days_analyzed=days_back
        )

        print(f"Generated power map with {len(power_map.nodes)} nodes")
        return power_map

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate power map: {str(e)}"
        )


@router.post("/automated-power-map/demo", response_model=AutomatedPowerMap)
async def generate_demo_power_map() -> AutomatedPowerMap:
    """
    Generate a demo power map with mock data

    Useful for testing the UI and understanding the output format
    without needing real Google Workspace access
    """

    # Use mock data
    email_interactions = gmail_service._mock_email_interactions(days_back=30)
    calendar_events = calendar_service._mock_calendar_events(days_ahead=30)

    power_map = network_analyzer.build_power_map(
        email_interactions=email_interactions,
        calendar_events=calendar_events,
        user_email="user@company.com",
        manager_email="manager@company.com",
        direct_report_emails=["teammate1@company.com", "teammate2@company.com"],
        days_analyzed=30
    )

    return power_map
