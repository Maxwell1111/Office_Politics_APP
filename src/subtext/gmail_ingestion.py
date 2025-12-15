"""
Gmail Ingestion Service - Analyze email metadata only
NO EMAIL BODY CONTENT IS READ - only From/To/CC/timestamps
"""

import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from collections import defaultdict

from subtext.models import EmailInteraction

# Optional import
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available for Gmail API")


class GmailIngestionService:
    """
    Ingest email metadata from Gmail API
    PRIVACY-FIRST: Only reads metadata (From/To/CC/timestamps), never body content
    """

    def __init__(self):
        """Initialize Gmail ingestion service"""
        self.base_url = "https://gmail.googleapis.com/gmail/v1/users/me"

    def fetch_email_metadata(
        self,
        access_token: str,
        days_back: int = 30,
        max_results: int = 500
    ) -> List[EmailInteraction]:
        """
        Fetch email metadata (From/To/CC only, NO body content)

        Args:
            access_token: Google OAuth access token
            days_back: How many days back to analyze
            max_results: Maximum number of emails to fetch

        Returns:
            List of EmailInteraction objects with metadata only
        """

        if not REQUESTS_AVAILABLE:
            print("⚠️ Requests library not available - using mock email data")
            return self._mock_email_interactions(days_back)

        try:
            # Calculate date range
            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            query = f"after:{since_date.strftime('%Y/%m/%d')}"

            # Get list of message IDs
            messages = self._fetch_message_ids(access_token, query, max_results)

            if not messages:
                return []

            # Fetch metadata for each message
            interactions = []
            for msg_id in messages[:max_results]:  # Limit to max_results
                interaction = self._fetch_message_metadata(access_token, msg_id)
                if interaction:
                    interactions.append(interaction)

            return interactions

        except Exception as e:
            print(f"Error fetching Gmail metadata: {e}")
            return self._mock_email_interactions(days_back)

    def _fetch_message_ids(
        self,
        access_token: str,
        query: str,
        max_results: int
    ) -> List[str]:
        """Fetch list of message IDs matching query"""

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "q": query,
            "maxResults": max_results
        }

        url = f"{self.base_url}/messages"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        messages = data.get("messages", [])

        return [msg["id"] for msg in messages]

    def _fetch_message_metadata(
        self,
        access_token: str,
        message_id: str
    ) -> Optional[EmailInteraction]:
        """
        Fetch metadata for a single message
        PRIVACY: Only reads headers, never body
        """

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"format": "metadata"}  # Only fetch metadata, not body

        url = f"{self.base_url}/messages/{message_id}"

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract headers
            headers_dict = {}
            for header in data.get("payload", {}).get("headers", []):
                headers_dict[header["name"].lower()] = header["value"]

            # Parse From/To/CC
            from_email = self._extract_email(headers_dict.get("from", ""))
            to_emails = self._extract_emails(headers_dict.get("to", ""))
            cc_emails = self._extract_emails(headers_dict.get("cc", ""))

            if not from_email or not to_emails:
                return None

            # Parse timestamp
            timestamp_ms = int(data.get("internalDate", 0))
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

            # Determine if it's a reply
            in_reply_to = headers_dict.get("in-reply-to")
            is_reply = bool(in_reply_to)

            return EmailInteraction(
                from_email=from_email,
                to_emails=to_emails,
                cc_emails=cc_emails,
                timestamp=timestamp,
                thread_id=data.get("threadId"),
                is_reply=is_reply,
                response_time_hours=None  # Calculate separately
            )

        except Exception as e:
            print(f"Error fetching message {message_id}: {e}")
            return None

    def _extract_email(self, email_str: str) -> str:
        """Extract email address from 'Name <email>' format"""
        if not email_str:
            return ""

        # Match email in angle brackets or standalone
        match = re.search(r'<([^>]+)>|([^\s]+@[^\s]+)', email_str)
        if match:
            return (match.group(1) or match.group(2)).strip().lower()

        return ""

    def _extract_emails(self, emails_str: str) -> List[str]:
        """Extract multiple email addresses from comma-separated string"""
        if not emails_str:
            return []

        # Split by comma and extract each email
        parts = emails_str.split(',')
        emails = []

        for part in parts:
            email = self._extract_email(part)
            if email:
                emails.append(email)

        return emails

    def calculate_response_times(
        self,
        interactions: List[EmailInteraction]
    ) -> List[EmailInteraction]:
        """
        Calculate response times for email threads

        For each reply, find the previous email in the thread and
        calculate how long it took to respond
        """

        # Group by thread ID
        threads = defaultdict(list)
        for interaction in interactions:
            if interaction.thread_id:
                threads[interaction.thread_id].append(interaction)

        # Calculate response times
        updated_interactions = []
        for interaction in interactions:
            if interaction.is_reply and interaction.thread_id:
                thread_emails = threads[interaction.thread_id]
                # Sort by timestamp
                thread_emails.sort(key=lambda x: x.timestamp)

                # Find previous email in thread
                idx = thread_emails.index(interaction)
                if idx > 0:
                    previous = thread_emails[idx - 1]
                    time_diff = interaction.timestamp - previous.timestamp
                    interaction.response_time_hours = time_diff.total_seconds() / 3600

            updated_interactions.append(interaction)

        return updated_interactions

    def _mock_email_interactions(self, days_back: int) -> List[EmailInteraction]:
        """Generate mock email interactions for testing"""
        print("⚠️ Using mock email data - provide Gmail OAuth token for real data")

        now = datetime.now(timezone.utc)
        interactions = []

        # Mock email patterns
        people = [
            "alice@company.com",
            "bob@company.com",
            "manager@company.com",
            "director@company.com",
            "teammate1@company.com",
            "teammate2@company.com"
        ]

        for day in range(days_back):
            date = now - timedelta(days=day)

            # Morning check-in with manager
            interactions.append(EmailInteraction(
                from_email="user@company.com",
                to_emails=["manager@company.com"],
                cc_emails=[],
                timestamp=date.replace(hour=9),
                is_reply=False
            ))

            # Team discussions
            interactions.append(EmailInteraction(
                from_email=people[day % len(people)],
                to_emails=["user@company.com", people[(day + 1) % len(people)]],
                cc_emails=["manager@company.com"],
                timestamp=date.replace(hour=11),
                is_reply=False
            ))

            # Reply to someone
            interactions.append(EmailInteraction(
                from_email="user@company.com",
                to_emails=[people[day % len(people)]],
                cc_emails=[],
                timestamp=date.replace(hour=14),
                is_reply=True,
                response_time_hours=2.5
            ))

        return interactions


# Global instance
gmail_service = GmailIngestionService()
