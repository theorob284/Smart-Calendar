from datetime import timedelta
from icalendar import Calendar
import pdfplumber
from PIL import Image
import pytesseract
import re
from datetime import timedelta
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

# these date regex's have been found and inspired from: https://regexbox.com/regex-templates/date, https://www.freecodecamp.org/news/regex-for-date-formats-what-is-the-regular-expression-for-matching-dates/
# https://regex101.com/r/rAmexa/1 and most USEFULLY: https://thelinuxcode.com/mastering-regular-expressions-for-matching-date-formats/

# PDF and OCR Extraction logic
#------------------------------------------

monthRegex = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)? |Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
weekdayRegex = r"(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)"
dayRegex = r"\d{1,2}(?:st|nd|rd|th)?"
yearRegex = r"(?:\d{2}|\d{4})"

datePattern = [
    rf"\b{monthRegex}\s+{dayRegex},?\s+{yearRegex}\b", # e.g. March 3, 2026 / March 12th 2026 / March 5th, 2026
    rf"\b{dayRegex}\s+{monthRegex},?\s+{yearRegex}\b", # 4 March 2026 / 09 March 2026 / 4th March 2026
    rf"\b{weekdayRegex},?\s+(?:{monthRegex}\s+{dayRegex},?\s+{yearRegex}|{dayRegex}\s+{monthRegex},?\s+{yearRegex})\b", # weekday prefix (Monday, March 3, 2026 / Tue 4 March 2026)
    rf"\b\d{{1,2}}[-/]\d{{1,2}}[-/]{yearRegex}\b", # e.g. 03/03/2026 / 3/8/26 / 06-03-2026 (slash or dash)
    rf"\b\d{{1,2}}\.\d{{1,2}}\.{yearRegex}\b", # Dot format (e.g. 06.03.2026 / 6.3.26)
    rf"\b\d{{4}}[-/.]\d{{1,2}}[-/.]\d{{1,2}}\b",# ISO format (e.g. 2026-03-05)
    rf"\b\d{{1,2}}-{monthRegex}-{yearRegex}\b",# e.g. 4-Mar-2026 / 04-March-26
] 

timeRegex = r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b"
Hour24Regex = r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\:[0-5]\d)?\b"
timeRangeRegex = rf"(?:from\s+)?({timeRegex}|{Hour24Regex})\s*(?:to|-|–)\s*({timeRegex}|{Hour24Regex})"

# Locations
CommonLocations = ["Main Office","Office","Front Office","Training Lab","IT Training Lab","Hall","Library",]
CommonLocationsRegex = r"(?:{})".format("|".join(sorted((re.escape(x) for x in CommonLocations), key=len, reverse=True)))
CheckRoom = r"(?:Room\s*\d+[A-Za-z]?)"
campusOutlierCheck = r"(?:entire\s+campus|campus)"
locationLabelledRegex = rf"""\b(?:location|venue|address)\s*:\s*(?P<labelled>.+?)(?=[\.,;\n]|$)"""
locationPrepositionRegex = rf"""\b(?:in|at|inside|to|across)\s+(?:the\s+)?(?P<place>{CommonLocationsRegex} | {CheckRoom} | {campusOutlierCheck} | (?:[A-Z][\w&'\-\.]*\s*){{1,8}}) (?=[\.,;\n]|$)"""
locationRegex = re.compile(locationLabelledRegex + "|" + locationPrepositionRegex, re.I | re.VERBOSE)

def extractPDF(path):
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(layout=True)
            if page_text:
                text_parts.append(page_text)
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
    find = re.search(rf"({timeRegex}|{Hour24Regex})", sentence)
    return find.group(0) if find else None

def _FindTimeRange(sentence):
    find = re.search(timeRangeRegex, sentence)
    if find:
        return find.group(1), find.group(2)
    return None, None

def _FindLocation(sentence):
    sentence = re.sub(r"\s+", " ", sentence).strip()

    find = locationRegex.search(sentence)
    loc = ""
    if find:
        gd = find.groupdict()
        loc = (gd.get("labelled") or gd.get("place") or "").strip()

    if not loc:
        return ""

    loc = re.sub(r"\s+", " ", loc).strip(" ,.-")
    loc = loc.rstrip(" ?!.")
    loc = re.sub(r"(?i)^(?:at|in|inside|near|by|to|across)\s+(?:the\s+)?", "", loc).strip()
    loc = re.sub(r"(?ix)^\d{1,2}[:\.]\d{2}\s*(?:am|pm|a\.?m\.?|p\.?m\.?)?\s*", "", loc).strip()
    if re.fullmatch(r"(?ix)\d{1,2}[:\.]\d{2}\s*(?:am|pm|a\.?m\.?|p\.?m\.?)?", loc):
        return ""
    loc = re.split(r"(?ix)\s+\b(?:at|from|to|by|starting|start)\b\s+", loc, maxsplit=1)[0].strip(" ,.-")
    return loc

def _GuessTitle(sentence, date, start, loc):
    original_sentence = sentence
    sentence = re.sub(r"\s+", " ", sentence).strip()

    def applySubs(rules):
        nonlocal sentence
        for patterns, replace in rules:
            sentence = re.sub(patterns, replace, sentence, flags=re.I)
        return sentence

    def Getgroup(pattern):
        find = re.search(pattern, sentence, flags=re.I)
        return find.group(1) if find else None

    applySubs([(r"^\s*[–\-•]+\s*", ""),(r"^\s*on\s*[,:\-–—]*\s*", ""),(r"^\s*on\s+the\s+", ""),])

    timeRange = re.search(timeRangeRegex, sentence, flags=re.I)
    if timeRange and timeRange.start() <= 3:
        after = sentence[timeRange.end():].strip(" :-–—,")
        if after:
            sentence = after
    elif start:
        starting = re.search(re.escape(start), sentence, flags=re.I)
        if starting and starting.start() <= 3:
            after = sentence[starting.end():].strip(" :-–—,")
            if after:
                sentence = after

    find = Getgroup(r"\bwith\s+(?:the|a|an)?\s*(.+?)(?=\s+\b(?:at|in|from|to|by|starting)\b|[.,;]|$)")
    if find: 
        sentence = find

    find = Getgroup(r"\b(?:present|presenting|conducting|hosting|running)\s+(?:the\s+)?(.+?)(?=\s+\b(?:at|in|from|to|by|starting)\b|[.,;]|$)")
    if find: 
        sentence = find

    sentence = re.split(r"(?i)\s+\b(?:at|in|from|to|by|starting)\b\s+", sentence, 1)[0]
    sentence = re.split(r"(?i)\s+\b(?:is|are|was|were)\s+(?:at|in)\b\s+", sentence, 1)[0]
    sentence = re.sub(r"(?i)\s+\bon\b\s*$", "", sentence).strip()

    find = re.search(r"(?i)^\s*(?:the\s+)?(.+?)\s+\b(?:is|will)\s+(?:scheduled|occur|take\s+place|be\s+held|follow|begin|start)\b", sentence)
    if find: 
        sentence = find.group(1).strip()

    sentence = re.split(r"(?i)\s+(?:how|i['’]m|there['’]s|we['’]ll|we will)\b", sentence, 1)[0]
    find = re.search(r"(?i)\b(?:local\s+)?(.+?\b(?:exhibition|game|dinner|meeting|assembly|workshop|run|night))\b", sentence)
    if find: 
        sentence = find.group(1)
    sentence = re.sub(r"(?i)^\s*(?:there['’]s|there is)\s+(?:a\s+)?", "", sentence).strip()

    if date:
        sentence = sentence.replace(date, "")
    if loc:
        sentence = re.sub(re.escape(loc).replace(r"\ ", r"\s+"), "", sentence, flags=re.I)

    applySubs([
        (r"^\s*[–\-•]+\s*", ""),
        (r"^\s*(?:here(?:'s| is)\s+an?\s+overview.*?:\s*)", ""),
        (r"^\s*(?:good\s+(?:morning|afternoon|evening).*?:?\s*)", ""),
        (r"^\s*(?:on\s+)?(?:mon|monday|tue|tuesday|wed|wednesday|thu|thursday|fri|friday|sat|saturday|sun|sunday)\b[:,\-]?\s*", ""),
        (r"^\s*(?:later\s+that\s+same\s+day|later\s+on|additionally|finally|please\s+remember\s+that)\b[:,\-]?\s*", ""),
        (r"^\s*on\s*[,:\-–—]*\s*", ""),
        (r"^(?:on\s+)?(?:the\s+week\s+begins\s+with|we\s+will|the\s+team\s+will|it\s+will|is\s+scheduled|there\s+is|there\s+will\s+be|this\s+will\s+be)\s+", ""),
        (r"\b(at|in|from|to|on)\s*$", ""),
        (r"\b(?:will\s+(?:be\s+)?)?(?:occur|take\s+place|be\s+held|be\s+conducted|be\s+hosted|begin|begins|start|starts|scheduled|present|presents|marks)\b", ""),
    ])
    sentence = re.sub(r"\s+", " ", sentence).strip(" ,.-")
    sentence = re.sub(r"^(?:the|a|an)\s+", "", sentence, flags=re.I)
    sentence = re.sub(r"(?i)\b(in|at)\s+(?:t|th)$", "", sentence).strip()
    sentence = re.sub(r"^[\s\ufeff\u200b\u200c\u200d]*[–—−\-•]+\s*", "", sentence).strip()

    find = re.search(r"(?i)\b(art exhibition|exhibition|game night|game|workshop|meeting|assembly|training)\b", sentence)
    if find and len(sentence) < 3:
        sentence = find.group(1)

    if len(sentence.strip()) < 3:
        find = re.search(r"(?i)\b(?:local\s+)?(.+?\b(?:exhibition|game night|game|dinner|meeting|assembly|workshop|run|training|fire drill))\b", original_sentence)
        if find:
            sentence = find.group(1).strip()

    return (sentence[:60] or "Imported event").strip()

def ExtractedTextToEvent(text, defaultDuration: int = 60):
    
    candidates = []
    sentences = _SplitSenteces(text)
    #sentences = _SplitLines(text)
    currentDate = None

    for sent in sentences:
        sent = re.sub(r"\s+", " ", sent).strip()
        date = _FindDate(sent)
        if date:
            currentDate = date

        StartTime, EndTime = _FindTimeRange(sent)

        if StartTime and EndTime:
            useDate = date or currentDate
            if not useDate:
                continue
            start = dparse.parse(f"{useDate} {StartTime}", dayfirst=True, fuzzy=True)
            end = dparse.parse(f"{useDate} {EndTime}", dayfirst=True, fuzzy=True)
            confidence = 0.85
        else:
            SingleTime = _GetSingleTime(sent)
            if not SingleTime:
                continue

            useDate = date or currentDate
            start = dparse.parse(f"{useDate} {SingleTime}", dayfirst=True, fuzzy=True)
            end = start + timedelta(minutes=defaultDuration)
            confidence = 0.70
        
        location = _FindLocation(sent)
        if location:
            confidence += 0.05
        
        title = _GuessTitle(sent, date or currentDate, StartTime or _GetSingleTime(sent), location)

        candidates.append({
            "title": title,
            "start_time": start,
            "end_time": end,
            "location": location,
            "confidence": min(confidence, 0.95),
            #"raw_text": sent[:5000]
        })

    return candidates

def extractOCR(image):
    # Tesseract docs: https://tesseract-ocr.github.io/tessdoc/
    text_parts = []
    img = Image.open(image)

    img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
    text = pytesseract.image_to_string(img, config="--psm 6")
    if text:
        text_parts.append(text)
        return "\n".join(text_parts)
    return ""

