import os
from datetime import datetime, timedelta, timezone

import requests
import icalendar
import recurring_ical_events


SOURCE_URL = os.environ["OUTLOOK_ICS_URL"]

now = datetime.now(timezone.utc)
window_start = now - timedelta(days=60)
window_end = now + timedelta(days=120)

response = requests.get(SOURCE_URL, timeout=60)
response.raise_for_status()

source_calendar = icalendar.Calendar.from_ical(response.content)

output_calendar = icalendar.Calendar()
output_calendar.add("prodid", "-//WhiteLab Professional Calendar//")
output_calendar.add("version", "2.0")
output_calendar.add("calscale", "GREGORIAN")
output_calendar.add("method", "PUBLISH")

# Expand recurring events and retrieve occurrences in our rolling window.
occurrences = recurring_ical_events.of(source_calendar).between(
    window_start,
    window_end,
    inc=True,
)

for event in occurrences:
    # Only process calendar events.
    if event.name != "VEVENT":
        continue

    new_event = icalendar.Event()

    # Copy the event properties while excluding recurrence rules.
    # Recurring events have already been expanded into individual occurrences.
    excluded = {
        "RRULE",
        "RDATE",
        "EXDATE",
        "RECURRENCE-ID",
    }

    for key, value in event.items():
        if key not in excluded:
            new_event.add(key, value)

    # Give each generated occurrence a unique UID.
    original_uid = str(event.get("UID", ""))
    recurrence_id = event.get("RECURRENCE-ID")

    if recurrence_id:
        new_event["UID"] = (
            f"{original_uid}-{str(recurrence_id).replace(':', '-')}"
        )
    else:
        new_event["UID"] = original_uid

    output_calendar.add_component(new_event)


os.makedirs("public", exist_ok=True)

with open("public/professional.ics", "wb") as f:
    f.write(output_calendar.to_ical())

print(
    f"Calendar generated: "
    f"{window_start.isoformat()} to {window_end.isoformat()}"
)
