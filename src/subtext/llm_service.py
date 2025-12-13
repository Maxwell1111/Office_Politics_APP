"""
LLM Service for Politico - Corporate Zen AI Analysis
Provides scenario analysis and tone checking using Claude or OpenAI
"""

import os
import json
from typing import List, Dict, Any
from anthropic import Anthropic
from subtext.models import (
    StrategyOption, StrategyType, RiskLevel,
    ScenarioAnalysis, ToneAnalysis
)
import uuid
from datetime import datetime, timezone


class PoliticoLLMService:
    """
    LLM service for political scenario analysis and communication guidance
    Tone: Corporate Zen - calm, strategic, objective, supportive
    """

    def __init__(self):
        """Initialize with API key from environment"""
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None

    def analyze_scenario(
        self,
        scenario_description: str,
        stakeholders_involved: List[str],
        user_goal: str
    ) -> ScenarioAnalysis:
        """
        Analyze a political scenario and provide strategic options
        Returns 3 approaches: Passive, Assertive, Strategic
        """

        if not self.client:
            return self._mock_scenario_analysis(scenario_description, user_goal)

        prompt = f"""You are an expert in organizational psychology and workplace dynamics.
Analyze this office politics scenario with a "Corporate Zen" approach - calm, strategic, objective, and supportive.

**Scenario:**
{scenario_description}

**Stakeholders Involved:**
{', '.join(stakeholders_involved) if stakeholders_involved else 'Not specified'}

**User's Goal:**
{user_goal}

**Provide a JSON response with this exact structure:**
{{
  "power_dynamic": "Who holds the power in this scenario and why",
  "risk_level": "low|medium|high|critical",
  "political_implications": "How this situation could affect the user's career/reputation",
  "strategy_options": [
    {{
      "strategy_type": "passive",
      "title": "Low-Confrontation Approach",
      "description": "A diplomatic, low-risk option",
      "pros": ["Benefit 1", "Benefit 2"],
      "cons": ["Drawback 1", "Drawback 2"],
      "recommended_actions": ["Step 1", "Step 2"]
    }},
    {{
      "strategy_type": "assertive",
      "title": "Professional Boundary-Setting",
      "description": "Clear, professional communication",
      "pros": ["Benefit 1", "Benefit 2"],
      "cons": ["Drawback 1", "Drawback 2"],
      "recommended_actions": ["Step 1", "Step 2"]
    }},
    {{
      "strategy_type": "strategic",
      "title": "Long-Term Alliance Building",
      "description": "Strategic positioning and relationship building",
      "pros": ["Benefit 1", "Benefit 2"],
      "cons": ["Drawback 1", "Drawback 2"],
      "recommended_actions": ["Step 1", "Step 2"]
    }}
  ]
}}

Focus on ethical, professional approaches. Do not encourage toxic behavior."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response
            response_text = message.content[0].text
            # Extract JSON from response (it might have markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text

            data = json.loads(json_str)

            # Convert to our model
            return ScenarioAnalysis(
                id=str(uuid.uuid4()),
                scenario_description=scenario_description,
                power_dynamic=data["power_dynamic"],
                risk_level=RiskLevel(data["risk_level"]),
                political_implications=data["political_implications"],
                strategy_options=[
                    StrategyOption(
                        strategy_type=StrategyType(opt["strategy_type"]),
                        title=opt["title"],
                        description=opt["description"],
                        pros=opt["pros"],
                        cons=opt["cons"],
                        recommended_actions=opt["recommended_actions"]
                    )
                    for opt in data["strategy_options"]
                ]
            )

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_scenario_analysis(scenario_description, user_goal)

    def analyze_tone(self, email_draft: str) -> ToneAnalysis:
        """
        Analyze the tone of an email/message
        Returns aggression/passivity scores and a suggested rewrite
        """

        if not self.client:
            return self._mock_tone_analysis(email_draft)

        prompt = f"""You are an expert in workplace communication and Non-Violent Communication (NVC) techniques.

Analyze this email draft for tone and political implications:

**Email Draft:**
{email_draft}

**Provide a JSON response with this exact structure:**
{{
  "aggression_score": 0-100 (how aggressive/confrontational the tone is),
  "passivity_score": 0-100 (how passive/weak the tone is),
  "political_implications": "One sentence about how this might be perceived",
  "suggested_rewrite": "A rewritten version using NVC principles that maintains the core message"
}}

The rewrite should be professional, clear, and assertive without being aggressive."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text

            data = json.loads(json_str)

            return ToneAnalysis(
                id=str(uuid.uuid4()),
                original_text=email_draft,
                aggression_score=data["aggression_score"],
                passivity_score=data["passivity_score"],
                political_implications=data["political_implications"],
                suggested_rewrite=data["suggested_rewrite"]
            )

        except Exception as e:
            print(f"Error analyzing tone: {e}")
            return self._mock_tone_analysis(email_draft)

    def _mock_scenario_analysis(self, scenario: str, goal: str) -> ScenarioAnalysis:
        """Mock response when LLM is not available"""
        return ScenarioAnalysis(
            id=str(uuid.uuid4()),
            scenario_description=scenario,
            power_dynamic="⚠️ LLM not configured. Set ANTHROPIC_API_KEY environment variable.",
            risk_level=RiskLevel.MEDIUM,
            political_implications="Unable to analyze without LLM API access.",
            strategy_options=[
                StrategyOption(
                    strategy_type=StrategyType.PASSIVE,
                    title="Document and Wait",
                    description="Document the situation and monitor",
                    pros=["Low risk", "Gather information"],
                    cons=["Slow", "May miss opportunities"],
                    recommended_actions=["Document everything", "Observe patterns"]
                ),
                StrategyOption(
                    strategy_type=StrategyType.ASSERTIVE,
                    title="Direct Communication",
                    description="Address the issue directly but professionally",
                    pros=["Clear boundaries", "Faster resolution"],
                    cons=["Potential confrontation", "Requires courage"],
                    recommended_actions=["Schedule private meeting", "Use 'I' statements"]
                ),
                StrategyOption(
                    strategy_type=StrategyType.STRATEGIC,
                    title="Build Support Network",
                    description="Strengthen alliances before acting",
                    pros=["Better positioning", "More support"],
                    cons=["Takes time", "Requires patience"],
                    recommended_actions=["Identify allies", "Build credibility"]
                )
            ]
        )

    def _mock_tone_analysis(self, email: str) -> ToneAnalysis:
        """Mock tone analysis when LLM is not available"""
        return ToneAnalysis(
            id=str(uuid.uuid4()),
            original_text=email,
            aggression_score=50,
            passivity_score=50,
            political_implications="⚠️ LLM not configured. Set ANTHROPIC_API_KEY for real analysis.",
            suggested_rewrite=email
        )


# Global instance
llm_service = PoliticoLLMService()
