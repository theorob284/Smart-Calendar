import os

from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document, ExtractedEventCandidate
from .serializers import DocumentSerializer, ExtractedEventCandidateSerializer, SmartPlanSerializer
from .parsers import parse_ics, extractPDF, ExtractedTextToEvent, extractOCR
from calendarapp.serializers import EventSerializer
from calendarapp.models import Event
from calendarapp.utils import CreateConflictRecord

class FileUploadAPIView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):

        files = request.FILES.getlist("files")
        if not files:
            OneFile =  request.FILES.get("file")
            if OneFile:
                files = [OneFile]
        
        if not files:
            return Response({"detail": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        FilesTitle = request.data.get("title") or f"Upload ({len(files)} files)"
        FilesDoc = Document.objects.create(title=FilesTitle)

        def parseFiles(file_path,name):
            candidates = []
            ext = os.path.splitext(name.lower())[1]
            if ext == ".ics":
                candidates = parse_ics(file_path)

            elif ext == ".pdf":
                text = extractPDF(file_path)
                # One candidate for now, later split
                candidates = ExtractedTextToEvent(text)
                if not candidates:
                    candidates = [{
                        "title": f"Imported from {name}",
                        "start_time": None,
                        "end_time": None,
                        "location": "",
                        "confidence": 0.2,
                        "raw_text": text[:5000],  # avoid huge DB entry
                    }]
            elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
                text = extractOCR(file_path)
                candidates = ExtractedTextToEvent(text)
                if not candidates:
                    candidates = [{
                        "title": f"OCR pending for image: {name}",
                        "raw_text": "Image uploaded. OCR not implemented yet.",
                        "confidence": 0.0,
                        "start_time": None,
                        "end_time": None,
                        "location": "",
                    }]
            else:
                candidates = [{
                    "title": "Unsupported file type (stored only)",
                    "confidence": 0.0,
                    "raw_text": name,
                    "start_time": None,
                    "end_time": None,
                    "location": "",
                }]
            return candidates

        created = []
        for f in files:
            childDoc = Document.objects.create(title=f.name, file=f)
            file_path = childDoc.file.path
            candidates = parseFiles(file_path, childDoc.file.name)
            for c in candidates:
                obj = ExtractedEventCandidate.objects.create(
                    document=FilesDoc,
                    title=c.get("title", ""),
                    start_time=c.get("start_time"),
                    end_time=c.get("end_time"),
                    location=c.get("location", ""),
                    raw_text=c.get("raw_text", ""),
                    confidence=c.get("confidence"),
                )
                created.append({
                    "id": obj.id,
                    "title": obj.title,
                    "start_time": obj.start_time,
                    "end_time": obj.end_time,
                    "location": obj.location,
                    "confidence": obj.confidence,
                })
            if childDoc.file:
                childDoc.file.delete(save=True)
            childDoc.delete()
        
        docData = self.get_serializer(FilesDoc).data
        # Return normal upload response + candidates
        return Response(
            {
                "document": docData,
                "candidates_created": created,
                "files_received": len(files),
            },
            status=status.HTTP_201_CREATED,
        )

class CandidateView(viewsets.ModelViewSet):
    serializer_class = ExtractedEventCandidateSerializer
    queryset = ExtractedEventCandidate.objects.all().order_by("id")

    def get_queryset(self):

        qs = super().get_queryset()

        document_id = self.request.query_params.get("document")
        if document_id:
            qs = qs.filter(document_id=document_id)

        GetStatus = self.request.query_params.get("status")
        if GetStatus:
            qs = qs.filter(status=GetStatus)
        
        return qs
    
    def update(self, request, *args, **kwargs):
        
        cand = self.get_object()

        if cand.status != ExtractedEventCandidate.Status.pending:
            return Response({"error": "only candidates in the pending state can be edited"}, status=409)
        
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])

    def reject(self, request, pk=None):
        cand = self.get_object()

        cand.status = ExtractedEventCandidate.Status.rejected
        cand.reviewed_at = timezone.now()
        cand.save()

        return Response(self.get_serializer(cand).data)
    @action(detail=True, methods=["post"])

    def accept(self, request, pk=None):
        cand = self.get_object()

        if cand.status != ExtractedEventCandidate.Status.pending:
            return Response({"error": "only candidates in the pending state can be edited"}, status=409)
        
        OverrideStart = request.data.get("start_time")
        OverrideEnd = request.data.get("end_time")

        if (OverrideStart and not OverrideEnd) or (not OverrideStart and OverrideEnd):
            return Response({"error": "Start time and End time must be provided"}, status=400)

        if OverrideStart and OverrideEnd:
            ParsedStart = parse_datetime(OverrideStart)
            ParsedEnd = parse_datetime(OverrideEnd)

            if not ParsedStart or not ParsedEnd:
                return Response({"error": "invalid date format"}, status=400)
            
            if ParsedEnd <= ParsedStart:
                return Response({"error": "end time must be after start time"},status=400)

            cand.start_time = ParsedStart
            cand.end_time = ParsedEnd
        
        if not cand.start_time or not cand.end_time:
            return Response({"error": "Missing start or end time"}, status=400)
        
        ConvertToEvent = {
            "title": cand.title,
            "start_time": cand.start_time,
            "end_time": cand.end_time,
            "location": cand.location,
            "confidence": cand.confidence
        }

        serializer = EventSerializer(data=ConvertToEvent)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        CreateConflictRecord(event)

        cand.status = ExtractedEventCandidate.Status.approved
        cand.reviewed_at = timezone.now()
        cand.approveEvent = event
        cand.save()

        return Response({"candidate": self.get_serializer(cand).data,"event": serializer.data}, status=201)
    
class SmartPlanView(APIView):
    def post(self, request):
        SmartSerializer = SmartPlanSerializer(data=request.data)
        SmartSerializer.is_valid(raise_exception=True)
        data = SmartSerializer.validated_data

        CandidateSet = ExtractedEventCandidate.objects.filter(
            status=ExtractedEventCandidate.Status.pending,
            document_id__in=data["GetDocumentIds"]
        )

        if data["ExistingEvents"]:
            existing = list(Event.objects.all())
        else:
            existing = []
        
        selected = []
        skipped = []

        def candConfidence(c):
            if c.confidence is not None:
                return float(c.confidence)
            else:
                return 0.5
            
        def getOverlappingMinutes (Astart, Aend, Bstart, Bend):
            Latest = max(Astart, Bstart)
            Earliest = min(Aend, Bend)
            if Latest >= Earliest:
                return 0.0
            return (Earliest - Latest).total_seconds() / 60.0
            

        def SortCandidates(Sortkey):
            if Sortkey.start_time and Sortkey.end_time and Sortkey.end_time > Sortkey.start_time:
                duration = (Sortkey.end_time - Sortkey.start_time).total_seconds()
            else:
                duration = -1
            return (-duration, -candConfidence(Sortkey), Sortkey.start_time or timezone.now())
        
        def GroupKey(c):
            title = (c.title or "").strip().lower()
            if not c.start_time or not c.end_time:
                return ("title only", title)
            
            day = c.start_time.date()
            grouped = (c.start_time.hour * 60 + c.start_time.minute) // 30
            return ("timed", title, day, grouped)
        
        def MergeIntervals(intervals):
            intervals = sorted(intervals, key=lambda x: x[0])
            merged = []
            for start, end in intervals:
                if not merged or start > merged[-1][1]:
                    merged.append([start,end])
                else:
                    merged[-1][1] = max(merged[-1][1], end)
            return [(start, end) for start, end in merged]

        def GetGapOptions(Target, Duration, Busy, GapStart, GapEnd, MaxGapOptions = 10):
            GetGapStart = []
            for start, end in Busy:
                if end <= GapStart or start >= GapEnd:
                    continue
                GetGapStart.append((max(start, GapStart), min(end, GapEnd)))
            busy = MergeIntervals(GetGapStart)

            timeline = [(GapStart, GapStart)] + busy + [(GapEnd, GapEnd)]
            candidates = []
            DurationSeconds = Duration.total_seconds()

            for i in range(len(timeline) - 1):
                GapStart = timeline[i][1]
                GapEnd = timeline[i + 1][0]

                if GapEnd <= GapStart:
                    continue

                if (GapEnd - GapStart).total_seconds() < DurationSeconds:
                    continue

                start1 = GapStart
                event1 = start1 + Duration

                Start2 = GapEnd - Duration
                event2 = GapEnd

                Start3 = Target
                if Start3 < GapStart:
                    Start3 = GapStart
                if (Start3 + Duration) > GapEnd:
                    Start3 = GapEnd - Duration
                event3 = Start3 + Duration

                for start, end in {(start1, event1), (Start2, event2), (Start3, event3)}:
                    moved = abs((start - Target).total_seconds()) / 60.0
                    candidates.append((start, end, moved))
            
            best = {}
            for start, end, moved in candidates:
                key = (start, end)
                if key not in best or moved < best[key]:
                    best[key] = moved
            
            options = [(start, end, best[(start, end)]) for (start, end) in best.keys()]
            options.sort(key=lambda x: x[2]) 
            return options[:MaxGapOptions]


        candidates = list(CandidateSet)
        candidates.sort(key=SortCandidates)
        
        selected_ranges = []
        selectedGroups = set()

        for cand in candidates:
            if not cand.title:
                skipped.append({"candidate_id": cand.id, "reason": "no_title"})
                continue
    
            if not cand.start_time or not cand.end_time:
                skipped.append({"candidate_id": cand.id,"reason": "missing_time"})
                continue

            if cand.end_time <= cand.start_time:
                skipped.append({"candidate_id": cand.id,"reason": "invalid_timerange"})
                continue

            confidece = candConfidence(cand)
            duration = cand.end_time - cand.start_time

            options = [(cand.start_time, cand.end_time, 0)]
            if data["AllowReschedule"] and data["MaxTimeShift"] > 0:
                StartWindow = cand.start_time - timedelta(minutes=data["MaxTimeShift"])
                EndWindow = cand.start_time + timedelta(minutes=data["MaxTimeShift"])

                BusyIntervals = []
                if data["ExistingEvents"]:
                    BusyIntervals.extend((event.start_time, event.end_time) for event in existing)
                BusyIntervals.extend(selected_ranges)

                GapOptions = GetGapOptions(Target=cand.start_time, Duration=duration, Busy=BusyIntervals, GapStart = StartWindow, GapEnd=EndWindow, MaxGapOptions=10)

                options.extend(GapOptions)
            
            BestOption = None
            BestScore = None
            BestExistingOverlap = 0.0
            BestSelectedOverlap = 0.0
            SkipScore = -(data["SkipPenalty"] * confidece)
            ScoredOptions = []
            BestBufferRule = 0.0

            for OptionalStart, OptionalEnd, moved in options:
                ExistingOverlapMinutes = 0.0
                for event in existing:
                    ExistingOverlapMinutes += getOverlappingMinutes(OptionalStart, OptionalEnd, event.start_time, event.end_time)

                SelectedOverlapMinutes = 0.0
                for start, end in selected_ranges:
                    SelectedOverlapMinutes += getOverlappingMinutes(OptionalStart, OptionalEnd, start, end)

                ExistingOverlap = ExistingOverlapMinutes / 60.0
                SelectedOverlap = SelectedOverlapMinutes / 60.0
                    
                Benefit = data["ConfidenceWeight"] * confidece
                penalties = 0.0
                penalties += data["MovePenalty"] * moved
                penalties += data["ConflictPenalty"] * (data["ExistingConflictMulti"] * ExistingOverlap + SelectedOverlap)
                BufferMinutes = data["BufferTime"]
                BufferPenalty = data["BufferPenalty"]
                BufferRule = 0.0

                for start, end in selected_ranges:
                    GapBefore = (start - OptionalEnd).total_seconds() / 60.0
                    GapAfter = (OptionalStart - end).total_seconds() / 60.0

                    if 0 < GapBefore < BufferMinutes:
                        BufferRule += (BufferMinutes - GapBefore)
                    
                    if 0 < GapAfter < BufferMinutes:
                        BufferRule += (BufferMinutes - GapAfter)
    
                if BufferRule > 0:
                    penalties += BufferPenalty

                if data["WorkHours"]:
                    WorkStart = data["WorkStart"]
                    WorkEnd = data["WorkEnd"]

                    if OptionalStart.hour < WorkStart or OptionalEnd.hour >= WorkEnd:
                        penalties += data["OutsideWorkPenalty"]
                    if data["AvoidWeekends"] and OptionalStart.weekday() >= 5:
                        penalties += data["WeekendPenalty"]

                score = Benefit - penalties

                if BestScore is None or score > BestScore:
                    BestScore = score
                    BestOption = (OptionalStart, OptionalEnd, moved)
                    BestExistingOverlap = ExistingOverlap
                    BestSelectedOverlap = SelectedOverlap
                    BestBufferRule = BufferRule
                
                ScoredOptions.append({
                    "start": OptionalStart,
                    "end": OptionalEnd,
                    "moved": moved,
                    "score": score,
                })

            ScoredOptions.sort(key=lambda x: x["score"], reverse=True)
            
            if BestScore is None or BestScore <= SkipScore:
                skipped.append({
                    "candidate_id": cand.id,
                    "reason": "No option to schedule",
                    "bestOptionScore": BestScore,
                    "skip_threshold": SkipScore,
                })
                continue
            
            ChosenStart, ChosenEnd, moved = BestOption

            AlternativeRule = 2

            AlternativesExist = any(opt["score"] >= BestScore - AlternativeRule and not (opt["start"] == ChosenStart and opt["end"] == ChosenEnd) for opt in ScoredOptions)
            NeedsAlternatives = (
                moved > 0 or BestExistingOverlap > 0 or BestSelectedOverlap > 0 or BestBufferRule >= 5 or AlternativesExist
            )

            TopScore = ScoredOptions[0]["score"]
            FilterAlternatives = [
                option for option in ScoredOptions
                if option["score"] >= TopScore - AlternativeRule
                and not (option["start"] == ChosenStart and option["end"] == ChosenEnd)
            ]
            Alternatives = FilterAlternatives[:3] if NeedsAlternatives else []

            Gkey = GroupKey(cand)
            if Gkey in selectedGroups:
                skipped.append({"candidate_id": cand.id, "reason": "Already in alternative group"})
                continue

            selected.append({
                "candidate_id": cand.id,
                "title": cand.title,
                "start_time": ChosenStart,
                "end_time": ChosenEnd,
                "confidence": confidece,
                "moved_minutes": moved,
                "explanation": {
                    "existing_overlap_minutes": BestExistingOverlap,
                    "selected_overlap_minutes": BestSelectedOverlap,
                    "score": BestScore,
                },
                "alternatives": Alternatives
            })
            selected_ranges.append((ChosenStart, ChosenEnd))
            selectedGroups.add(Gkey)
        
        plan = {
            "selected": selected,
            "skipped": skipped,
            "stats": {
                "total_candidates": CandidateSet.count(),
                "selected_count": len(selected),
                "skipped_count": len(skipped)
            }
        }

        return Response(plan, status=status.HTTP_200_OK)