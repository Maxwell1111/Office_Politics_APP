"""
Network Graph Analyzer - Build and analyze organizational network
Uses graph theory to calculate centrality, betweenness, and identify structural holes
"""

import uuid
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from subtext.models import (
    EmailInteraction, CalendarEvent,
    NetworkNode, NetworkEdge, StructuralHole,
    NetworkInsight, ManagerAnalysis, DirectReportAnalysis,
    AutomatedPowerMap
)
from subtext.llm_service import llm_service


class NetworkAnalyzer:
    """
    Analyze organizational network from email and calendar data
    Calculate graph metrics and identify strategic opportunities
    """

    def build_power_map(
        self,
        email_interactions: List[EmailInteraction],
        calendar_events: List[CalendarEvent],
        user_email: str,
        manager_email: Optional[str] = None,
        direct_report_emails: List[str] = None,
        days_analyzed: int = 30
    ) -> AutomatedPowerMap:
        """
        Build complete automated power map from interaction data

        Args:
            email_interactions: Email metadata
            calendar_events: Calendar meetings
            user_email: The user's email address
            manager_email: User's manager (if known)
            direct_report_emails: User's direct reports (if any)
            days_analyzed: Number of days of data

        Returns:
            AutomatedPowerMap with nodes, edges, and insights
        """

        direct_report_emails = direct_report_emails or []

        # Build graph
        nodes, edges = self._build_graph(
            email_interactions,
            calendar_events,
            user_email,
            manager_email,
            direct_report_emails
        )

        # Calculate centrality scores
        self._calculate_centrality(nodes, edges)

        # Identify structural holes
        structural_holes = self._identify_structural_holes(
            user_email, nodes, edges
        )

        # Generate insights
        insights = self._generate_insights(
            user_email, nodes, edges, structural_holes
        )

        # Analyze manager relationship
        manager_analysis = None
        if manager_email:
            manager_analysis = self._analyze_manager_relationship(
                user_email, manager_email, edges, email_interactions, calendar_events
            )

        # Analyze direct reports
        direct_report_analyses = []
        for report_email in direct_report_emails:
            analysis = self._analyze_direct_report(
                report_email, nodes, edges, email_interactions
            )
            if analysis:
                direct_report_analyses.append(analysis)

        return AutomatedPowerMap(
            id=str(uuid.uuid4()),
            nodes=nodes,
            edges=edges,
            structural_holes=structural_holes,
            insights=insights,
            manager_analysis=manager_analysis,
            direct_report_analyses=direct_report_analyses,
            data_period_days=days_analyzed,
            total_emails_analyzed=len(email_interactions),
            total_meetings_analyzed=len(calendar_events)
        )

    def _build_graph(
        self,
        emails: List[EmailInteraction],
        meetings: List[CalendarEvent],
        user_email: str,
        manager_email: Optional[str],
        direct_report_emails: List[str]
    ) -> Tuple[List[NetworkNode], List[NetworkEdge]]:
        """Build network graph from interactions"""

        # Track all people and their interactions
        people: Set[str] = set()
        edge_data: Dict[Tuple[str, str], Dict] = defaultdict(lambda: {
            "email_count": 0,
            "meeting_count": 0,
            "response_times": []
        })

        # Process emails
        for email in emails:
            # Add people
            people.add(email.from_email)
            people.update(email.to_emails)
            people.update(email.cc_emails)

            # Track email edges
            for to_email in email.to_emails:
                key = (email.from_email, to_email)
                edge_data[key]["email_count"] += 1

                if email.response_time_hours is not None:
                    edge_data[key]["response_times"].append(email.response_time_hours)

            # CC counts as weaker connection
            for cc_email in email.cc_emails:
                key = (email.from_email, cc_email)
                edge_data[key]["email_count"] += 0.5  # Half weight for CC

        # Process meetings
        for meeting in meetings:
            attendees = meeting.attendees
            people.update(attendees)

            # Create edges between all pairs in meeting
            for i, attendee1 in enumerate(attendees):
                for attendee2 in attendees[i+1:]:
                    # Bidirectional edges for meetings
                    edge_data[(attendee1, attendee2)]["meeting_count"] += 1
                    edge_data[(attendee2, attendee1)]["meeting_count"] += 1

        # Build nodes
        nodes = []
        for email in people:
            # Count total interactions
            total_interactions = sum(
                data["email_count"] + data["meeting_count"]
                for key, data in edge_data.items()
                if email in key
            )

            node = NetworkNode(
                email=email,
                interaction_count=int(total_interactions),
                is_user=(email == user_email),
                is_manager=(email == manager_email),
                is_direct_report=(email in direct_report_emails)
            )
            nodes.append(node)

        # Build edges
        edges = []
        for (from_email, to_email), data in edge_data.items():
            if data["email_count"] == 0 and data["meeting_count"] == 0:
                continue

            # Calculate reciprocity
            reverse_data = edge_data.get((to_email, from_email), {})
            forward_count = data["email_count"] + data["meeting_count"]
            reverse_count = reverse_data.get("email_count", 0) + reverse_data.get("meeting_count", 0)

            if forward_count + reverse_count > 0:
                reciprocity = min(forward_count, reverse_count) / max(forward_count, reverse_count)
            else:
                reciprocity = 0.0

            # Calculate average response time
            avg_response_time = None
            if data["response_times"]:
                avg_response_time = sum(data["response_times"]) / len(data["response_times"])

            # Calculate edge strength (weighted combination)
            strength = (
                data["email_count"] * 1.0 +
                data["meeting_count"] * 2.0 +  # Meetings weigh more
                reciprocity * 5.0  # Reciprocity is valuable
            )

            edge = NetworkEdge(
                from_email=from_email,
                to_email=to_email,
                interaction_count=int(data["email_count"] + data["meeting_count"]),
                email_frequency=int(data["email_count"]),
                meeting_frequency=data["meeting_count"],
                reciprocity_score=reciprocity,
                avg_response_time_hours=avg_response_time,
                strength=strength
            )
            edges.append(edge)

        return nodes, edges

    def _calculate_centrality(
        self,
        nodes: List[NetworkNode],
        edges: List[NetworkEdge]
    ) -> None:
        """
        Calculate centrality and betweenness scores for all nodes
        Uses simplified graph algorithms
        """

        # Build adjacency structure
        email_to_node = {node.email: node for node in nodes}
        connections: Dict[str, List[str]] = defaultdict(list)
        edge_weights: Dict[Tuple[str, str], float] = {}

        for edge in edges:
            connections[edge.from_email].append(edge.to_email)
            connections[edge.to_email].append(edge.from_email)  # Treat as undirected for centrality
            edge_weights[(edge.from_email, edge.to_email)] = edge.strength
            edge_weights[(edge.to_email, edge.from_email)] = edge.strength

        # Calculate degree centrality (simple: number of connections)
        for node in nodes:
            unique_connections = set(connections[node.email])
            node.centrality_score = len(unique_connections)

        # Normalize centrality to 0-1 range
        max_centrality = max(node.centrality_score for node in nodes) if nodes else 1
        if max_centrality > 0:
            for node in nodes:
                node.centrality_score = node.centrality_score / max_centrality

        # Calculate betweenness (simplified: count how many shortest paths go through each node)
        # For simplicity, we'll approximate by counting bridges between communities
        for node in nodes:
            # Count how many distinct communities this person connects
            neighbors = set(connections[node.email])
            if len(neighbors) < 2:
                node.betweenness_score = 0.0
                continue

            # Check if removing this person would disconnect parts of the network
            bridge_score = 0.0
            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    if neighbor1 != neighbor2:
                        # If neighbor1 and neighbor2 aren't directly connected
                        if neighbor2 not in connections[neighbor1]:
                            bridge_score += 1.0

            node.betweenness_score = min(bridge_score / 100.0, 1.0)  # Normalize

    def _identify_structural_holes(
        self,
        user_email: str,
        nodes: List[NetworkNode],
        edges: List[NetworkEdge]
    ) -> List[StructuralHole]:
        """
        Identify structural holes - high-value connections the user is missing

        A structural hole is a valuable person the user doesn't directly connect to
        but could access through mutual connections
        """

        # Get user's direct connections
        user_connections = set()
        for edge in edges:
            if edge.from_email == user_email:
                user_connections.add(edge.to_email)
            elif edge.to_email == user_email:
                user_connections.add(edge.from_email)

        # Find high-centrality people user isn't connected to
        structural_holes = []

        for node in nodes:
            if node.email == user_email or node.email in user_connections:
                continue

            # Only consider high-centrality nodes (top influencers)
            if node.centrality_score < 0.5:
                continue

            # Find mutual connections
            mutual_connections = []
            for edge in edges:
                # People connected to this high-value node
                if edge.from_email == node.email and edge.to_email in user_connections:
                    mutual_connections.append(edge.to_email)
                elif edge.to_email == node.email and edge.from_email in user_connections:
                    mutual_connections.append(edge.from_email)

            if not mutual_connections:
                continue  # No path to this person

            # Generate AI-powered strategic value and approach
            strategic_value, approach = self._generate_structural_hole_advice(
                node, mutual_connections
            )

            hole = StructuralHole(
                person_email=node.email,
                person_name=node.name,
                centrality_score=node.centrality_score,
                mutual_connections=mutual_connections[:3],  # Top 3
                strategic_value=strategic_value,
                recommended_approach=approach
            )
            structural_holes.append(hole)

        # Sort by centrality (most influential first)
        structural_holes.sort(key=lambda x: x.centrality_score, reverse=True)

        return structural_holes[:5]  # Top 5 structural holes

    def _generate_structural_hole_advice(
        self,
        node: NetworkNode,
        mutual_connections: List[str]
    ) -> Tuple[str, str]:
        """Generate strategic advice for bridging a structural hole"""

        # Default advice if no LLM
        if not llm_service.client:
            return (
                f"High-centrality connection (score: {node.centrality_score:.2f}) - could expand your influence",
                f"Route communication through {mutual_connections[0]} who can introduce you"
            )

        # Use LLM for nuanced advice
        prompt = f"""You are an executive coach advising on network building.

**Target Person:** {node.email}
**Their Network Centrality:** {node.centrality_score:.2f} (0-1 scale, higher = more influential)
**Mutual Connections:** {', '.join(mutual_connections[:3])}

Provide 2 concise responses:
1. **Strategic Value** (1 sentence): Why connecting with this person would increase influence
2. **Recommended Approach** (1 sentence): Concrete way to build this connection using mutual contacts

Keep it professional and actionable."""

        try:
            message = llm_service.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()
            lines = [line.strip() for line in response.split('\n') if line.strip()]

            if len(lines) >= 2:
                return lines[0], lines[1]
            else:
                return response, f"Connect through {mutual_connections[0]}"

        except Exception as e:
            print(f"Error generating structural hole advice: {e}")
            return (
                f"High-centrality node - connecting could expand your influence by {int(node.centrality_score * 100)}%",
                f"Ask {mutual_connections[0]} for an introduction or invite both to a casual meeting"
            )

    def _generate_insights(
        self,
        user_email: str,
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        structural_holes: List[StructuralHole]
    ) -> List[NetworkInsight]:
        """Generate actionable network insights"""

        insights = []

        # Structural hole insights
        for hole in structural_holes[:3]:  # Top 3
            insights.append(NetworkInsight(
                insight_type="structural_hole",
                priority="high",
                title=f"Missing Connection: {hole.person_email}",
                description=hole.strategic_value,
                actionable_step=hole.recommended_approach,
                related_people=[hole.person_email] + hole.mutual_connections
            ))

        # Find your strongest connections
        user_edges = [e for e in edges if e.from_email == user_email or e.to_email == user_email]
        user_edges.sort(key=lambda e: e.strength, reverse=True)

        if user_edges:
            strongest = user_edges[0]
            other_person = strongest.to_email if strongest.from_email == user_email else strongest.from_email

            insights.append(NetworkInsight(
                insight_type="game_theory",
                priority="medium",
                title=f"Leverage Your Strongest Connection: {other_person}",
                description=f"This is your highest-strength relationship (interaction count: {strongest.interaction_count})",
                actionable_step=f"To influence others, route proposals through {other_person} who has strong network connections",
                related_people=[other_person]
            ))

        return insights

    def _analyze_manager_relationship(
        self,
        user_email: str,
        manager_email: str,
        edges: List[NetworkEdge],
        emails: List[EmailInteraction],
        meetings: List[CalendarEvent]
    ) -> ManagerAnalysis:
        """Analyze relationship with manager"""

        # Count your interactions with manager (per week)
        user_manager_emails = sum(
            1 for e in emails
            if (e.from_email == user_email and manager_email in e.to_emails) or
               (e.from_email == manager_email and user_email in e.to_emails)
        )

        user_manager_meetings = sum(
            1 for m in meetings
            if user_email in m.attendees and manager_email in m.attendees
        )

        weeks = len(emails) / 7 if emails else 1  # Approximate weeks
        your_frequency = int((user_manager_emails + user_manager_meetings) / weeks)

        # Estimate peer average (simplified)
        peer_avg = your_frequency * 0.8  # Assume slightly less than you

        # Determine communication balance
        if your_frequency > peer_avg * 1.5:
            balance = "over_communicating"
            recs = ["Consider spacing out less urgent updates", "Let manager come to you occasionally"]
        elif your_frequency < peer_avg * 0.7:
            balance = "under_communicating"
            recs = ["Increase check-in frequency", "Proactively share progress updates"]
        else:
            balance = "balanced"
            recs = ["Maintain current communication cadence", "Continue regular 1:1 meetings"]

        return ManagerAnalysis(
            manager_email=manager_email,
            your_interaction_frequency=your_frequency,
            peer_avg_frequency=peer_avg,
            communication_balance=balance,
            response_time_trend="stable",  # Would need historical data
            recommendations=recs
        )

    def _analyze_direct_report(
        self,
        report_email: str,
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        emails: List[EmailInteraction]
    ) -> Optional[DirectReportAnalysis]:
        """Analyze direct report for isolation risk"""

        # Find the report's node
        report_node = next((n for n in nodes if n.email == report_email), None)
        if not report_node:
            return None

        # Count their connections
        connection_count = len([
            e for e in edges
            if e.from_email == report_email or e.to_email == report_email
        ])

        # Calculate isolation risk
        if connection_count < 3:
            isolation = "high"
            recs = [
                "Schedule team introduction meetings",
                "Include them in more group discussions"
            ]
        elif connection_count < 6:
            isolation = "medium"
            recs = ["Encourage cross-team collaboration"]
        else:
            isolation = "low"
            recs = ["Network connectivity looks healthy"]

        return DirectReportAnalysis(
            report_email=report_email,
            interaction_frequency=report_node.interaction_count,
            isolation_risk=isolation,
            network_connectivity=report_node.centrality_score,
            recommendations=recs
        )


# Global instance
network_analyzer = NetworkAnalyzer()
