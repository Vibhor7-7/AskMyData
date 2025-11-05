from icalendar import Calendar
import pandas as pd
from datetime import datetime

with open("backend/parsers/sch.ics", "rb") as f:
    cal = Calendar.from_ical(f.read())

events = []
for component in cal.walk():
    if component.name == "VEVENT":
        events.append({
            "summary": str(component.get("summary")),
            "start": component.get("dtstart").dt,
            "end": component.get("dtend").dt,
            "duration": (component.get("dtend").dt - component.get("dtstart").dt).total_seconds() / 3600
        })

df = pd.DataFrame(events)
print(df)