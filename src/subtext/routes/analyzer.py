"""
AI Analysis API routes - Scenario Analyzer & Tone Checker
Uses LLM to provide strategic guidance
"""

from fastapi import APIRouter
from subtext.models import (
    AnalyzeScenarioRequest,
    ScenarioAnalysis,
    AnalyzeToneRequest,
    ToneAnalysis,
)
from subtext.llm_service import llm_service
from subtext.security import sanitize_input

router = APIRouter(tags=["analyzer"])


@router.post("/analyze-scenario", response_model=ScenarioAnalysis)
async def analyze_scenario(request: AnalyzeScenarioRequest) -> ScenarioAnalysis:
    """
    Analyze an office politics scenario
    Returns power dynamics, risk assessment, and 3 strategic options
    """

    # Sanitize input
    scenario_clean = sanitize_input(request.scenario_description)
    goal_clean = sanitize_input(request.user_goal)

    # Call LLM service
    analysis = llm_service.analyze_scenario(
        scenario_description=scenario_clean,
        stakeholders_involved=request.stakeholders_involved,
        user_goal=goal_clean
    )

    return analysis


@router.post("/analyze-tone", response_model=ToneAnalysis)
async def analyze_tone(request: AnalyzeToneRequest) -> ToneAnalysis:
    """
    Analyze the tone of an email or message
    Returns aggression/passivity scores and a rewritten version
    """

    # Sanitize input
    email_clean = sanitize_input(request.email_draft)

    # Call LLM service
    analysis = llm_service.analyze_tone(email_draft=email_clean)

    return analysis


@router.get("/analyzer/test")
async def test_analyzer() -> dict:
    """Test endpoint to verify analyzer is working"""
    return {
        "status": "ok",
        "message": "Analyzer API is working!",
        "llm_configured": llm_service.client is not None
    }
