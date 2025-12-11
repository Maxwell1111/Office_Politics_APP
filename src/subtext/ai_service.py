"""
AI Service for Tone Decoder using Anthropic Claude API
"""

import os
from typing import List, Optional, Dict, Any
import anthropic
from sqlalchemy.orm import Session

from .models import Interaction, Player
from .encryption import decrypt_if_key_exists

# System prompt for the AI Chief of Staff persona
CHIEF_OF_STAFF_SYSTEM_PROMPT = """You are the Chief of Staff to a mid-level professional navigating corporate politics. Your role is to provide strategic, objective advice that maximizes their career longevity and leverage.

Core Directives:
1. ANALYZE POWER DYNAMICS: Identify who has formal authority vs. informal influence. Surface hidden agendas.
2. DECODE SUBTEXT: Read between the lines. What is ACTUALLY being communicated beyond the literal words?
3. ASSESS RISK: Evaluate career threats (Low/Medium/High). Flag situations where the user's reputation, autonomy, or position is at stake.
4. PROVIDE STRATEGIC RESPONSES: Draft replies that protect the user's status, document accountability, and avoid unnecessary conflict.
5. LEVERAGE CONTEXT: Reference past interactions and relationship history to inform advice. Patterns matter.

Personality Guidelines:
- Be direct and candid. No corporate platitudes or "positive vibes only" nonsense.
- Assume everyone has mixed motives. Trust is earned through repeated aligned behavior.
- When someone takes credit, sabotages, or undermines: name it clearly and suggest countermeasures.
- Prioritize survival and advancement over being "nice." Professionalism ≠ passivity.
- Use a tone that is calm, strategic, slightly cynical but constructive. Think: seasoned political operative, not HR.

Output Format (when decoding messages):
1. THE SUBTEXT: [What they're actually saying/wanting]
2. RISK ASSESSMENT: [Low/Medium/High + explanation]
3. STRATEGIC RESPONSE: [Suggested reply with rationale]
4. FOLLOW-UP ACTIONS: [Optional: what to document, who to loop in, etc.]

Remember: Your loyalty is to the user's career objectives, not to organizational harmony. Be Machiavellian when necessary."""


class AIService:
    """Service for AI-powered tone decoding and strategic advice"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

    def decode_message(
        self,
        message_text: str,
        sender_name: Optional[str] = None,
        sender_role: Optional[str] = None,
        context_interactions: Optional[List[Interaction]] = None,
        player_info: Optional[Player] = None,
        encryption_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decode a message using Claude AI to extract subtext and provide strategic advice.

        Args:
            message_text: The message to decode
            sender_name: Name of the sender
            sender_role: Role/title of the sender
            context_interactions: Previous interactions with this person for context
            player_info: Player object if sender is in the power map
            encryption_key: Key to decrypt interaction descriptions

        Returns:
            Dictionary with subtext, risk_level, suggested_reply, follow_up_actions, context_used
        """
        # Build context from past interactions
        context_summary = self._build_context_summary(
            context_interactions,
            player_info,
            encryption_key
        )

        # Build the user prompt
        user_prompt = self._build_user_prompt(
            message_text,
            sender_name,
            sender_role,
            context_summary
        )

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=CHIEF_OF_STAFF_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Parse the response
            analysis_text = response.content[0].text
            parsed_result = self._parse_ai_response(analysis_text)

            # Track which context was used
            context_used = []
            if context_interactions:
                context_used = [interaction.title for interaction in context_interactions[:5]]

            return {
                "subtext": parsed_result["subtext"],
                "risk_level": parsed_result["risk_level"],
                "suggested_reply": parsed_result["suggested_reply"],
                "follow_up_actions": parsed_result["follow_up_actions"],
                "context_used": context_used,
                "raw_analysis": analysis_text
            }

        except Exception as e:
            raise RuntimeError(f"AI analysis failed: {str(e)}")

    def _build_context_summary(
        self,
        interactions: Optional[List[Interaction]],
        player: Optional[Player],
        encryption_key: Optional[str]
    ) -> str:
        """Build a context summary from player info and past interactions"""
        context_parts = []

        if player:
            context_parts.append(f"**About {player.name}:**")
            if player.role:
                context_parts.append(f"- Role: {player.role}")
            if player.department:
                context_parts.append(f"- Department: {player.department}")
            if player.influence_level:
                context_parts.append(f"- Influence Level: {player.influence_level}/10")
            if player.relationship_status:
                context_parts.append(f"- Current Relationship: {player.relationship_status}")
            if player.notes:
                notes = decrypt_if_key_exists(player.notes, encryption_key)
                context_parts.append(f"- Notes: {notes}")

        if interactions:
            context_parts.append(f"\n**Past Interactions (most recent {len(interactions)}):**")
            for interaction in interactions[:5]:  # Limit to 5 most recent
                desc = decrypt_if_key_exists(interaction.description, encryption_key)
                context_parts.append(
                    f"- {interaction.interaction_date.strftime('%Y-%m-%d')}: "
                    f"{interaction.title} (Sentiment: {interaction.sentiment}, "
                    f"Risk: {interaction.risk_level}) - {desc[:150]}..."
                )

        return "\n".join(context_parts) if context_parts else "No prior context available."

    def _build_user_prompt(
        self,
        message_text: str,
        sender_name: Optional[str],
        sender_role: Optional[str],
        context_summary: str
    ) -> str:
        """Build the user prompt for Claude"""
        prompt_parts = [
            "Please analyze the following message and provide strategic advice.\n"
        ]

        if sender_name or sender_role:
            prompt_parts.append("**Sender Information:**")
            if sender_name:
                prompt_parts.append(f"- Name: {sender_name}")
            if sender_role:
                prompt_parts.append(f"- Role: {sender_role}")
            prompt_parts.append("")

        if context_summary != "No prior context available.":
            prompt_parts.append("**Historical Context:**")
            prompt_parts.append(context_summary)
            prompt_parts.append("")

        prompt_parts.append("**Message to Analyze:**")
        prompt_parts.append(f'"{message_text}"')
        prompt_parts.append("")
        prompt_parts.append("Provide your analysis in the specified format.")

        return "\n".join(prompt_parts)

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude's response into structured format.
        Looks for sections: THE SUBTEXT, RISK ASSESSMENT, STRATEGIC RESPONSE, FOLLOW-UP ACTIONS
        """
        result = {
            "subtext": "",
            "risk_level": "medium",  # default
            "suggested_reply": "",
            "follow_up_actions": []
        }

        # Split into sections
        lines = response_text.split('\n')
        current_section = None

        for line in lines:
            line_upper = line.upper().strip()

            if "THE SUBTEXT" in line_upper or "SUBTEXT:" in line_upper:
                current_section = "subtext"
                continue
            elif "RISK ASSESSMENT" in line_upper or "RISK:" in line_upper:
                current_section = "risk"
                continue
            elif "STRATEGIC RESPONSE" in line_upper or "SUGGESTED REPLY" in line_upper:
                current_section = "reply"
                continue
            elif "FOLLOW-UP" in line_upper or "FOLLOW UP" in line_upper:
                current_section = "followup"
                continue

            # Append content to current section
            if current_section and line.strip():
                if current_section == "subtext":
                    result["subtext"] += line.strip() + " "
                elif current_section == "risk":
                    result["risk_level"] = self._extract_risk_level(line)
                    # Also save the full explanation
                    if "risk_explanation" not in result:
                        result["risk_explanation"] = ""
                    result["risk_explanation"] += line.strip() + " "
                elif current_section == "reply":
                    result["suggested_reply"] += line.strip() + " "
                elif current_section == "followup":
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        result["follow_up_actions"].append(line.strip()[1:].strip())
                    elif line.strip():
                        result["follow_up_actions"].append(line.strip())

        # Clean up whitespace
        result["subtext"] = result["subtext"].strip()
        result["suggested_reply"] = result["suggested_reply"].strip()

        # If parsing failed, use entire response as subtext
        if not result["subtext"]:
            result["subtext"] = response_text[:500]
        if not result["suggested_reply"]:
            result["suggested_reply"] = "Draft a professional response that protects your position."

        return result

    def _extract_risk_level(self, text: str) -> str:
        """Extract risk level from text (low/medium/high)"""
        text_lower = text.lower()
        if "high" in text_lower:
            return "high"
        elif "low" in text_lower:
            return "low"
        else:
            return "medium"


# Singleton instance
ai_service = AIService()
