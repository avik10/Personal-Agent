"""Google Calendar API Tools for MCP."""

import datetime
from typing import Any, Dict, List, Optional
import uuid

from ..auth import get_service


def _format_event_time(event: Dict[str, Any], key: str) -> str:
    """Helper to extract formatted start/end time string."""
    t = event.get(key, {})
    return t.get("dateTime") or t.get("date") or ""


def calendar_list_calendars() -> List[Dict[str, Any]]:
    """List all Google Calendars accessible by the authenticated user."""
    service = get_service("calendar", "v3")
    res = service.calendarList().list().execute()
    items = res.get("items", [])
    return [
        {
            "id": cal.get("id"),
            "summary": cal.get("summary"),
            "primary": cal.get("primary", False),
            "timeZone": cal.get("timeZone"),
            "accessRole": cal.get("accessRole"),
        }
        for cal in items
    ]


def calendar_list_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    query: Optional[str] = None,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """List events from a Google Calendar with optional date filtering and search query.

    Args:
        calendar_id: Calendar ID (default 'primary').
        time_min: Start time in ISO format (e.g., '2026-11-01T00:00:00Z'). Defaults to current time.
        time_max: End time in ISO format (e.g., '2026-11-08T23:59:59Z').
        query: Free text search term to filter events.
        max_results: Maximum events to return (default 20, max 100).
    """
    service = get_service("calendar", "v3")

    if not time_min:
        time_min = datetime.datetime.now(datetime.timezone.utc).isoformat()

    params: Dict[str, Any] = {
        "calendarId": calendar_id,
        "timeMin": time_min,
        "maxResults": max(1, min(max_results, 100)),
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if time_max:
        params["timeMax"] = time_max
    if query:
        params["q"] = query

    res = service.events().list(**params).execute()
    events = res.get("items", [])

    output = []
    for ev in events:
        output.append(
            {
                "id": ev.get("id"),
                "summary": ev.get("summary", "(Untitled)"),
                "start": _format_event_time(ev, "start"),
                "end": _format_event_time(ev, "end"),
                "location": ev.get("location", ""),
                "description": ev.get("description", ""),
                "htmlLink": ev.get("htmlLink", ""),
                "hangoutLink": ev.get("hangoutLink", ""),
                "attendees": [
                    a.get("email") for a in ev.get("attendees", []) if a.get("email")
                ],
            }
        )
    return output


def calendar_get_agenda(
    days_ahead: int = 7, calendar_id: str = "primary"
) -> List[Dict[str, Any]]:
    """Convenience tool to get scheduled events and meetings for the upcoming N days.

    Args:
        days_ahead: Number of days forward to inspect (default 7).
        calendar_id: Calendar identifier (default 'primary').
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    until = now + datetime.timedelta(days=max(1, days_ahead))
    return calendar_list_events(
        calendar_id=calendar_id,
        time_min=now.isoformat(),
        time_max=until.isoformat(),
        max_results=50,
    )


def calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    add_meet_link: bool = False,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """Create a new event or meeting on Google Calendar.

    Args:
        summary: Title or name of the event.
        start_time: ISO 8601 start datetime string (e.g., '2026-11-02T14:00:00' or with timezone '2026-11-02T14:00:00+05:30') or date '2026-11-02'.
        end_time: ISO 8601 end datetime string (e.g., '2026-11-02T15:00:00' or with timezone) or date.
        description: Optional notes, agenda, or description.
        location: Optional location or room name.
        attendees: Optional list of guest email addresses.
        add_meet_link: If True, automatically creates a Google Meet video conference link.
        calendar_id: Target calendar ID (default 'primary').
    """
    service = get_service("calendar", "v3")

    # Format start and end
    event_body: Dict[str, Any] = {"summary": summary}

    if "T" in start_time:
        event_body["start"] = {"dateTime": start_time}
        event_body["end"] = {"dateTime": end_time}
    else:
        event_body["start"] = {"date": start_time}
        event_body["end"] = {"date": end_time}

    if description:
        event_body["description"] = description
    if location:
        event_body["location"] = location
    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]

    conference_args: Dict[str, Any] = {}
    if add_meet_link:
        event_body["conferenceData"] = {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }
        conference_args["conferenceDataVersion"] = 1

    created = (
        service.events()
        .insert(calendarId=calendar_id, body=event_body, **conference_args)
        .execute()
    )

    return {
        "status": "created",
        "id": created.get("id"),
        "summary": created.get("summary"),
        "start": _format_event_time(created, "start"),
        "end": _format_event_time(created, "end"),
        "htmlLink": created.get("htmlLink"),
        "meetLink": created.get("hangoutLink", ""),
    }


def calendar_update_event(
    event_id: str,
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """Update details of an existing event on Google Calendar.

    Args:
        event_id: Event ID to modify.
        summary: Optional updated event summary/title.
        start_time: Optional updated start time (ISO 8601).
        end_time: Optional updated end time (ISO 8601).
        description: Optional updated description text.
        location: Optional updated location.
        calendar_id: Calendar ID (default 'primary').
    """
    service = get_service("calendar", "v3")

    existing = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    if summary is not None:
        existing["summary"] = summary
    if description is not None:
        existing["description"] = description
    if location is not None:
        existing["location"] = location

    if start_time is not None:
        if "T" in start_time:
            existing["start"] = {"dateTime": start_time}
        else:
            existing["start"] = {"date": start_time}

    if end_time is not None:
        if "T" in end_time:
            existing["end"] = {"dateTime": end_time}
        else:
            existing["end"] = {"date": end_time}

    updated = (
        service.events()
        .update(calendarId=calendar_id, eventId=event_id, body=existing)
        .execute()
    )

    return {
        "status": "updated",
        "id": updated.get("id"),
        "summary": updated.get("summary"),
        "start": _format_event_time(updated, "start"),
        "end": _format_event_time(updated, "end"),
        "htmlLink": updated.get("htmlLink"),
    }


def calendar_delete_event(
    event_id: str, calendar_id: str = "primary"
) -> Dict[str, Any]:
    """Delete an event from Google Calendar.

    Args:
        event_id: Event ID to remove.
        calendar_id: Calendar identifier (default 'primary').
    """
    service = get_service("calendar", "v3")
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return {"status": "deleted", "id": event_id, "calendarId": calendar_id}
