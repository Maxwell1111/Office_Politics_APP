"""
Calendar Service - Fetch events from iCal or Google Calendar
Supports both iCal feed URLs and Google Calendar API
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import re

from subtext.models import CalendarEvent

# Optional imports for calendar parsing
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests package not installed. Calendar fetching disabled.")

try:
    from icalendar import Calendar
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False
    print("Warning: icalendar package not installed. iCal parsing disabled.")


class CalendarService:
    """
    Service for fetching calendar events from various sources
    Supports: iCal feeds, Google Calendar API
    """

    def __init__(self):
        """Initialize calendar service"""
        self.google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    def fetch_ical_events(
        self,
        ical_url: str,
        days_ahead: int = 7
    ) -> List[CalendarEvent]:
        """
        Fetch events from an iCal feed URL

        Args:
            ical_url: URL to the iCal feed
            days_ahead: Number of days ahead to fetch

        Returns:
            List of CalendarEvent objects
        """
        if not REQUESTS_AVAILABLE or not ICALENDAR_AVAILABLE:
            print("⚠️ Calendar libraries not available")
            return self._mock_calendar_events(days_ahead)

        try:
            # Fetch the iCal feed
            response = requests.get(ical_url, timeout=10)
            response.raise_for_status()

            # Parse the iCal data
            cal = Calendar.from_ical(response.content)

            # Filter events within the time range
            now = datetime.now(timezone.utc)
            end_date = now + timedelta(days=days_ahead)

            events = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    event = self._parse_ical_event(component)
                    if event and now <= event.start_time <= end_date:
                        events.append(event)

            # Sort by start time
            events.sort(key=lambda x: x.start_time)
            return events

        except Exception as e:
            print(f"Error fetching iCal events: {e}")
            return self._mock_calendar_events(days_ahead)

    def fetch_google_calendar_events(
        self,
        access_token: str,
        days_ahead: int = 7
    ) -> List[CalendarEvent]:
        """
        Fetch events from Google Calendar API

        Args:
            access_token: Google OAuth access token
            days_ahead: Number of days ahead to fetch

        Returns:
            List of CalendarEvent objects
        """
        if not REQUESTS_AVAILABLE:
            print("⚠️ Requests library not available")
            return self._mock_calendar_events(days_ahead)

        try:
            # Calculate time range
            now = datetime.now(timezone.utc)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=days_ahead)).isoformat()

            # Call Google Calendar API
            url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": True,
                "orderBy": "startTime",
                "maxResults": 100
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse events
            events = []
            for item in data.get("items", []):
                event = self._parse_google_event(item)
                if event:
                    events.append(event)

            return events

        except Exception as e:
            print(f"Error fetching Google Calendar events: {e}")
            return self._mock_calendar_events(days_ahead)

    def _parse_ical_event(self, component) -> Optional[CalendarEvent]:
        """Parse an iCal VEVENT component into a CalendarEvent"""
        try:
            # Extract basic info
            summary = str(component.get('SUMMARY', 'Untitled Event'))
            dtstart = component.get('DTSTART').dt
            dtend = component.get('DTEND').dt if component.get('DTEND') else dtstart

            # Convert to datetime if date only
            if not isinstance(dtstart, datetime):
                dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=timezone.utc)
            if not isinstance(dtend, datetime):
                dtend = datetime.combine(dtend, datetime.min.time()).replace(tzinfo=timezone.utc)

            # Ensure timezone aware
            if dtstart.tzinfo is None:
                dtstart = dtstart.replace(tzinfo=timezone.utc)
            if dtend.tzinfo is None:
                dtend = dtend.replace(tzinfo=timezone.utc)

            # Extract attendees
            attendees = []
            if component.get('ATTENDEE'):
                attendee_list = component.get('ATTENDEE')
                if not isinstance(attendee_list, list):
                    attendee_list = [attendee_list]

                for attendee in attendee_list:
                    # Extract email from mailto: URI
                    attendee_str = str(attendee)
                    email_match = re.search(r'mailto:([^\s]+)', attendee_str)
                    if email_match:
                        attendees.append(email_match.group(1))

            return CalendarEvent(
                id=str(component.get('UID', str(uuid.uuid4()))),
                title=summary,
                start_time=dtstart,
                end_time=dtend,
                attendees=attendees,
                location=str(component.get('LOCATION', '')) if component.get('LOCATION') else None,
                description=str(component.get('DESCRIPTION', '')) if component.get('DESCRIPTION') else None,
                is_recurring=bool(component.get('RRULE'))
            )

        except Exception as e:
            print(f"Error parsing iCal event: {e}")
            return None

    def _parse_google_event(self, item: dict) -> Optional[CalendarEvent]:
        """Parse a Google Calendar API event into a CalendarEvent"""
        try:
            # Extract start/end times
            start = item.get('start', {})
            end = item.get('end', {})

            # Handle both dateTime and date (all-day events)
            start_str = start.get('dateTime') or start.get('date')
            end_str = end.get('dateTime') or end.get('date')

            if not start_str or not end_str:
                return None

            # Parse to datetime
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))

            # Extract attendees
            attendees = []
            for attendee in item.get('attendees', []):
                email = attendee.get('email')
                if email:
                    attendees.append(email)

            return CalendarEvent(
                id=item.get('id', str(uuid.uuid4())),
                title=item.get('summary', 'Untitled Event'),
                start_time=start_dt,
                end_time=end_dt,
                attendees=attendees,
                location=item.get('location'),
                description=item.get('description'),
                is_recurring='recurringEventId' in item
            )

        except Exception as e:
            print(f"Error parsing Google event: {e}")
            return None

    def _mock_calendar_events(self, days_ahead: int) -> List[CalendarEvent]:
        """Generate mock calendar events for testing"""
        print("⚠️ Using mock calendar events - install requests and icalendar packages for real calendar support")

        now = datetime.now(timezone.utc)
        events = [
            CalendarEvent(
                id=str(uuid.uuid4()),
                title="Weekly Team Sync",
                start_time=now + timedelta(days=1, hours=10),
                end_time=now + timedelta(days=1, hours=11),
                attendees=["alice@company.com", "bob@company.com", "manager@company.com"],
                location="Conference Room A"
            ),
            CalendarEvent(
                id=str(uuid.uuid4()),
                title="Q4 Strategy Review",
                start_time=now + timedelta(days=2, hours=14),
                end_time=now + timedelta(days=2, hours=15, minutes=30),
                attendees=["vp@company.com", "director@company.com", "manager@company.com"],
                location="Board Room"
            ),
            CalendarEvent(
                id=str(uuid.uuid4()),
                title="1:1 with Manager",
                start_time=now + timedelta(days=3, hours=9),
                end_time=now + timedelta(days=3, hours=9, minutes=30),
                attendees=["manager@company.com"],
                location="Virtual"
            ),
        ]

        return events


# Global instance
calendar_service = CalendarService()
