from datetime import timedelta
from icalendar import Calendar
import pdfplumber
from PIL import Image
import re
from datetime import datetime, timedelta
from dateutil import parser as dparse

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

# PDF Extraction logic
#-------------------------------------------
datePattern = [
        # these date regex's have been found and inspired from: https://regexbox.com/regex-templates/date, https://www.freecodecamp.org/news/regex-for-date-formats-what-is-the-regular-expression-for-matching-dates/
        # https://regex101.com/r/rAmexa/1 and most USEFULLY: https://thelinuxcode.com/mastering-regular-expressions-for-matching-date-formats/
        # e.g. March 3, 2026 / March 12th 2026 / March 5th, 2026
        r"\b(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+\d{2,4}\b",
        # 4 March 2026 / 09 March 2026 / 4th March 2026
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)(?:,)?\s+\d{2,4}\b",
        # weekday prefix (Monday, March 3, 2026 / Tue 4 March 2026)
        r"\b(?:Mon|Monday|Tue|Tuesday|Wed|Wednesday|Thu|Thursday|Fri|Friday|Sat|Saturday|Sun|Sunday),?\s+(?:\d{1,2}(?:st|nd|rd|th)?\s+)?(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+\d{2,4}\b",
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", # e.g. 03/03/2026 / 3/8/26 / 06-03-2026 (slash or dash)
        r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", # Dot format (e.g. 06.03.2026 / 6.3.26)
        r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b", # ISO format (e.g. 2026-03-05)
    ]
# Times like 9:00 AM or 10:30 PM https://stackoverflow.com/questions/33906033/regex-for-time-in-hhmm-am-pm-format
timeRegex = r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b"

# 24-hour times: 14:30, 09:00, optional seconds
Hour24Regex = r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\:[0-5]\d)?\b"

# Ranges like "from 1:30 PM to 4:00 PM" or "1:30 PM - 4:00 PM"
timeRangeRegex = rf"(?:from\s+)?({timeRegex}|{Hour24Regex})\s*(?:to|-|–)\s*({timeRegex}|{Hour24Regex})"

# Locations
locationRegex = r"\b(?:in|at|inside)\s+([A-Z][A-Za-z0-9\s&\-]+?)(?:\.|,|$)"

def extractPDF(path):

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(layout=True)
            if page_text:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    
def _SplitSenteces(text):
    splitted = re.split(r"(?<=[\.\!\?])\s+", text.strip())
    return [s.strip() for s in splitted if s.strip()]

def _FindDate(sentence):
    for pattern in datePattern:
        find = re.search(pattern, sentence)
        if find:
            return find.group(0)
    return None

def _GetSingleTime(sentence):
    find = re.search(timeRegex, sentence)
    return find.group(0)

def _FindTimeRange(sentence):
    find = re.search(timeRangeRegex, sentence)
    if find:
        return find.group(1).find.group(2)
    return None, None

def _FindLocation(sentence):
    find = re.search(locationRegex, sentence)
    return find.group(1).strip() if find else ""

def _GuessTitle(sentence, date, start):
    if date:
        sentence = sentence.replace(date, "")
    if start:
        sentence = sentence.replace(start, "")

    sentence = re.sub(r"\b(on|at|we will|will|is scheduled|begins|starts|starting)\b", "", sentence, flags=re.I)
    sentence = re.sub(r"\s+", " ", sentence).strip(" ,.-")

    return (sentence[:60] or "Imported event").strip()

def pdfTextToEvent(text, defaultDuration: int = 60):

    candidates = []
    sentences = _SplitSenteces(text)

    for sent in sentences:
        date = _FindDate(sent)
        if not date:
            continue

        StartTime, EndTime = _FindTimeRange(sent)

        if StartTime and EndTime:
            start = dparse.parse(f"{date} {StartTime}", dayfirst=True, fuzzy=True)
            end = dparse.parse(f"{date} {EndTime}", dayfirst=True, fuzzy=True)
            confidence = 0.85
        else:
            SingleTime = _GetSingleTime(sent)
            if not SingleTime:
                continue

            StartTime = dparse.parse(f"{date} {SingleTime}", dayfirst=True, fuzzy=True)
            EndTime = StartTime + timedelta(minutes=defaultDuration)
            confidence = 0.70
        
        location = _FindLocation(sent)
        if location:
            confidence += 0.05
        
        title = _GuessTitle(sent, date, StartTime or _GetSingleTime)

        candidates.append({
            "title": title,
            "start_time": StartTime,
            "end_time": EndTime,
            "location": location,
            "confidence": min(confidence, 0.95),
            "raw_text": sent[:5000]
        })
    return candidates
