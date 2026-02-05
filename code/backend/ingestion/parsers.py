from datetime import timedelta
from icalendar import Calendar
from pypdf import PdfReader
from PIL import Image

def parse_ics(file_path):
    
    results = []

    with open(file_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        title = str(component.get("summary", ""))

        dtstart = component.get("dtstart")
        dtend = component.get("dtend")

        start_dt = dtstart.dt if dtstart else None
        end_dt = dtend.dt if dtend else None

        # Some ICS files omit dtend; assume 1 hour if missing
        if start_dt and not end_dt:
            end_dt = start_dt + timedelta(hours=1)

        location = str(component.get("location", ""))

        results.append({
            "title": title,
            "start_time": start_dt,
            "end_time": end_dt,
            "location": location,
            "confidence": 1.0,
            "raw_text": title,
        })

    return results

def extractPDF(file_path):

    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)
