"""
Calendar Analyzer - AI-powered strategic calendar analysis
Cross-references calendar events with stakeholder database
"""

import uuid
import json
from typing import List, Optional
from datetime import datetime

from subtext.models import (
    CalendarEvent, CalendarAnalysis, MeetingInsight,
    MeetingWarning, PoliticalStakesLevel, Stakeholder,
    RelationshipStatus
)
from subtext.llm_service import llm_service


class CalendarAnalyzer:
    """
    Analyzes calendar events for political stakes and strategic insights
    Cross-references attendees with stakeholder database
    """

    def analyze_calendar(
        self,
        events: List[CalendarEvent],
        stakeholders: List[Stakeholder],
        user_manager_name: Optional[str] = None,
        analysis_period: str = "Next 7 days"
    ) -> CalendarAnalysis:
        """
        Analyze calendar events and generate strategic insights

        Args:
            events: List of calendar events
            stakeholders: List of known stakeholders
            user_manager_name: Name of user's manager for personalized tips
            analysis_period: Description of time period being analyzed

        Returns:
            CalendarAnalysis with meeting insights and warnings
        """

        # Analyze each meeting
        meeting_insights = []
        for event in events:
            insight = self._analyze_meeting(
                event=event,
                stakeholders=stakeholders,
                user_manager_name=user_manager_name
            )
            meeting_insights.append(insight)

        # Calculate summary stats
        total_meetings = len(meeting_insights)
        high_stakes_count = sum(
            1 for m in meeting_insights
            if m.political_stakes in [PoliticalStakesLevel.HIGH, PoliticalStakesLevel.CRITICAL]
        )

        # Generate weekly summary using LLM
        weekly_summary = self._generate_weekly_summary(
            meeting_insights=meeting_insights,
            stakeholders=stakeholders
        )

        return CalendarAnalysis(
            id=str(uuid.uuid4()),
            analysis_period=analysis_period,
            total_meetings=total_meetings,
            high_stakes_count=high_stakes_count,
            meeting_insights=meeting_insights,
            weekly_summary=weekly_summary
        )

    def _analyze_meeting(
        self,
        event: CalendarEvent,
        stakeholders: List[Stakeholder],
        user_manager_name: Optional[str] = None
    ) -> MeetingInsight:
        """Analyze a single meeting for political implications"""

        # Cross-reference attendees with stakeholders
        matched_stakeholders = []
        total_influence = 0
        adversary_count = 0
        ally_count = 0
        manager_present = False

        for attendee in event.attendees:
            # Try to match by name or email
            matched = self._find_stakeholder_match(attendee, stakeholders)
            if matched:
                matched_stakeholders.append(matched.id)
                total_influence += matched.influence_level

                if matched.relationship_status == RelationshipStatus.ADVERSARY:
                    adversary_count += 1
                elif matched.relationship_status == RelationshipStatus.ALLY:
                    ally_count += 1

                if user_manager_name and matched.name.lower() == user_manager_name.lower():
                    manager_present = True

        # Calculate political stakes
        political_stakes = self._calculate_political_stakes(
            total_influence=total_influence,
            stakeholder_count=len(matched_stakeholders),
            adversary_count=adversary_count
        )

        # Generate warnings
        warnings = self._generate_warnings(
            event=event,
            matched_stakeholders=matched_stakeholders,
            stakeholders=stakeholders,
            adversary_count=adversary_count,
            ally_count=ally_count,
            political_stakes=political_stakes
        )

        # Get manager tips if manager is present
        manager_tips = None
        if manager_present and user_manager_name:
            manager_stakeholder = next(
                (s for s in stakeholders if s.name.lower() == user_manager_name.lower()),
                None
            )
            if manager_stakeholder:
                manager_tips = self._generate_manager_tips(manager_stakeholder, event)

        # Generate preparation advice using LLM
        preparation_advice = self._generate_preparation_advice(
            event=event,
            matched_stakeholders=[s for s in stakeholders if s.id in matched_stakeholders],
            political_stakes=political_stakes,
            adversary_count=adversary_count,
            ally_count=ally_count
        )

        # Generate talking points
        talking_points = self._generate_talking_points(
            event=event,
            matched_stakeholders=[s for s in stakeholders if s.id in matched_stakeholders],
            political_stakes=political_stakes
        )

        return MeetingInsight(
            event_id=event.id,
            event_title=event.title,
            start_time=event.start_time,
            political_stakes=political_stakes,
            matched_stakeholders=matched_stakeholders,
            total_influence_score=total_influence,
            warnings=warnings,
            manager_tips=manager_tips,
            preparation_advice=preparation_advice,
            talking_points=talking_points
        )

    def _find_stakeholder_match(
        self,
        attendee: str,
        stakeholders: List[Stakeholder]
    ) -> Optional[Stakeholder]:
        """Match an attendee email/name to a stakeholder"""
        attendee_lower = attendee.lower()

        for stakeholder in stakeholders:
            # Match by exact name
            if stakeholder.name.lower() in attendee_lower:
                return stakeholder

            # Match by name parts (first/last name)
            name_parts = stakeholder.name.lower().split()
            if all(part in attendee_lower for part in name_parts):
                return stakeholder

        return None

    def _calculate_political_stakes(
        self,
        total_influence: int,
        stakeholder_count: int,
        adversary_count: int
    ) -> PoliticalStakesLevel:
        """Calculate the political stakes level for a meeting"""

        # Critical if multiple adversaries
        if adversary_count >= 3:
            return PoliticalStakesLevel.CRITICAL

        # High if high total influence or multiple adversaries
        if total_influence >= 25 or adversary_count >= 2:
            return PoliticalStakesLevel.HIGH

        # Medium if moderate influence or one adversary
        if total_influence >= 15 or adversary_count == 1 or stakeholder_count >= 3:
            return PoliticalStakesLevel.MEDIUM

        # Low otherwise
        return PoliticalStakesLevel.LOW

    def _generate_warnings(
        self,
        event: CalendarEvent,
        matched_stakeholders: List[str],
        stakeholders: List[Stakeholder],
        adversary_count: int,
        ally_count: int,
        political_stakes: PoliticalStakesLevel
    ) -> List[MeetingWarning]:
        """Generate warning flags for a meeting"""
        warnings = []

        # Multiple adversaries warning
        if adversary_count >= 3:
            warnings.append(MeetingWarning(
                type="adversary_present",
                message=f"⚠️ {adversary_count} adversaries in this meeting - prepare for potential pile-on. Have allies speak first if possible.",
                severity=PoliticalStakesLevel.CRITICAL
            ))
        elif adversary_count >= 2:
            warnings.append(MeetingWarning(
                type="adversary_present",
                message=f"⚠️ {adversary_count} adversaries present - they may coordinate. Stay factual and document everything.",
                severity=PoliticalStakesLevel.HIGH
            ))
        elif adversary_count == 1:
            warnings.append(MeetingWarning(
                type="adversary_present",
                message="⚠️ One adversary in attendance - be prepared for pushback on your proposals.",
                severity=PoliticalStakesLevel.MEDIUM
            ))

        # Outnumbered warning
        if adversary_count > ally_count and adversary_count > 0:
            warnings.append(MeetingWarning(
                type="power_imbalance",
                message=f"⚠️ Outnumbered: {adversary_count} adversaries vs {ally_count} allies. Consider deferring controversial topics.",
                severity=PoliticalStakesLevel.HIGH
            ))

        # Opportunity warnings
        if ally_count >= 2 and adversary_count == 0:
            warnings.append(MeetingWarning(
                type="opportunity",
                message=f"✅ Opportunity: {ally_count} allies present, no adversaries. Good time to advance your initiatives.",
                severity=PoliticalStakesLevel.LOW
            ))

        # Unstructured meeting opportunity
        if "brainstorm" in event.title.lower() or "ideation" in event.title.lower():
            warnings.append(MeetingWarning(
                type="opportunity",
                message="💡 Brainstorming session - opportunity to gain credit by contributing valuable ideas. Prepare 2-3 concrete suggestions.",
                severity=PoliticalStakesLevel.MEDIUM
            ))

        # High-stakes warning
        if political_stakes == PoliticalStakesLevel.CRITICAL:
            warnings.append(MeetingWarning(
                type="risk",
                message="🔴 Critical stakes - this meeting could significantly impact your standing. Prepare thoroughly.",
                severity=PoliticalStakesLevel.CRITICAL
            ))

        return warnings

    def _generate_manager_tips(
        self,
        manager: Stakeholder,
        event: CalendarEvent
    ) -> str:
        """Generate specific tips based on manager profile"""

        tips = []

        # Use manager's motivations if available
        if manager.core_motivations:
            motivations_str = ", ".join(manager.core_motivations[:2])
            tips.append(f"Your manager values: {motivations_str}")

        # Generic tips based on role
        tips.append("Have specific data/examples ready - managers appreciate concrete information")

        if "review" in event.title.lower() or "update" in event.title.lower():
            tips.append("Prepare a concise update on your progress and any blockers")

        if "planning" in event.title.lower() or "strategy" in event.title.lower():
            tips.append("Come with 1-2 strategic suggestions to demonstrate initiative")

        return " | ".join(tips)

    def _generate_preparation_advice(
        self,
        event: CalendarEvent,
        matched_stakeholders: List[Stakeholder],
        political_stakes: PoliticalStakesLevel,
        adversary_count: int,
        ally_count: int
    ) -> str:
        """Generate AI-powered preparation advice using LLM"""

        # If no LLM available, return generic advice
        if not llm_service.client:
            return self._generic_preparation_advice(event, political_stakes, adversary_count, ally_count)

        # Build stakeholder context
        stakeholder_context = []
        for s in matched_stakeholders[:5]:  # Limit to top 5
            stakeholder_context.append(
                f"- {s.name} ({s.role}): {s.relationship_status.value}, influence {s.influence_level}/10"
            )

        prompt = f"""You are an expert executive coach helping someone prepare for a meeting.

**Meeting:** {event.title}
**When:** {event.start_time.strftime('%A, %B %d at %I:%M %p')}
**Duration:** {(event.end_time - event.start_time).seconds // 60} minutes
**Political Stakes:** {political_stakes.value.upper()}

**Attendees ({len(matched_stakeholders)} stakeholders identified):**
{chr(10).join(stakeholder_context) if stakeholder_context else "No stakeholders identified"}

**Power Dynamic:**
- Allies: {ally_count}
- Adversaries: {adversary_count}
- Unknown/Neutral: {len(matched_stakeholders) - ally_count - adversary_count}

Provide concise, actionable preparation advice (2-3 sentences). Focus on:
1. How to position yourself given the power dynamic
2. What to prepare/bring
3. Key behaviors to adopt

Keep it practical and corporate-appropriate."""

        try:
            message = llm_service.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Error generating LLM advice: {e}")
            return self._generic_preparation_advice(event, political_stakes, adversary_count, ally_count)

    def _generate_talking_points(
        self,
        event: CalendarEvent,
        matched_stakeholders: List[Stakeholder],
        political_stakes: PoliticalStakesLevel
    ) -> List[str]:
        """Generate suggested talking points"""

        points = []

        if political_stakes in [PoliticalStakesLevel.HIGH, PoliticalStakesLevel.CRITICAL]:
            points.append("Lead with data and facts to establish credibility")
            points.append("Acknowledge others' concerns before presenting your view")

        if "review" in event.title.lower():
            points.append("Highlight measurable achievements and outcomes")
            points.append("Frame challenges as learning opportunities")

        if "planning" in event.title.lower() or "strategy" in event.title.lower():
            points.append("Connect proposals to team/company goals")
            points.append("Address potential risks proactively")

        # Default points
        if not points:
            points.append("Listen actively and take notes")
            points.append("Ask clarifying questions to show engagement")
            points.append("Summarize action items at the end")

        return points[:3]  # Max 3 points

    def _generate_weekly_summary(
        self,
        meeting_insights: List[MeetingInsight],
        stakeholders: List[Stakeholder]
    ) -> str:
        """Generate a strategic summary of the week using LLM"""

        if not llm_service.client or not meeting_insights:
            return self._generic_weekly_summary(meeting_insights)

        # Build summary of meetings
        meetings_summary = []
        for insight in meeting_insights[:10]:  # Limit to 10
            meetings_summary.append(
                f"- {insight.event_title} ({insight.political_stakes.value} stakes, {len(insight.warnings)} warnings)"
            )

        prompt = f"""You are an executive coach providing a strategic weekly briefing.

**Upcoming Meetings:** {len(meeting_insights)}
**High-Stakes Meetings:** {sum(1 for m in meeting_insights if m.political_stakes in [PoliticalStakesLevel.HIGH, PoliticalStakesLevel.CRITICAL])}

**Schedule:**
{chr(10).join(meetings_summary)}

Provide a 2-3 sentence strategic summary for the week ahead. Focus on:
1. Overall political temperature (calm, challenging, opportunity-rich)
2. Top strategic priority or theme
3. One key recommendation for navigating the week

Keep it executive-level and actionable."""

        try:
            message = llm_service.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Error generating weekly summary: {e}")
            return self._generic_weekly_summary(meeting_insights)

    def _generic_preparation_advice(
        self,
        event: CalendarEvent,
        political_stakes: PoliticalStakesLevel,
        adversary_count: int,
        ally_count: int
    ) -> str:
        """Generic preparation advice when LLM is unavailable"""

        if political_stakes == PoliticalStakesLevel.CRITICAL:
            return "High-stakes meeting with complex dynamics. Prepare thoroughly, have supporting data ready, and consider pre-aligning with allies."

        if adversary_count > ally_count:
            return "You're outnumbered. Stay factual, document everything, and defer controversial decisions if possible."

        if ally_count >= 2:
            return "Supportive audience. Good opportunity to advance your initiatives and gain visibility."

        return "Standard meeting preparation: review agenda, prepare talking points, and be ready to contribute constructively."

    def _generic_weekly_summary(self, meeting_insights: List[MeetingInsight]) -> str:
        """Generic weekly summary when LLM is unavailable"""

        high_stakes = sum(
            1 for m in meeting_insights
            if m.political_stakes in [PoliticalStakesLevel.HIGH, PoliticalStakesLevel.CRITICAL]
        )

        if high_stakes >= 3:
            return f"Challenging week ahead with {high_stakes} high-stakes meetings. Prioritize preparation for critical meetings and maintain strong documentation."

        if high_stakes >= 1:
            return f"Moderate week with {high_stakes} key meeting(s) requiring focused preparation. Good opportunities to build relationships in other meetings."

        return "Relatively calm week. Use this time to build relationships, gather information, and advance long-term initiatives."


# Global instance
calendar_analyzer = CalendarAnalyzer()
