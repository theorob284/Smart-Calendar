import os

from datetime import timedelta
from django.utils import timezone
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
            
        candidates = list(CandidateSet)

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
                for skipStep in [15, 30, 60, 90, 120, 180]:
                    if skipStep <= data["MaxTimeShift"]:
                        earlier = cand.start_time - timedelta(minutes=skipStep)
                        later = cand.start_time + timedelta(minutes=skipStep)
                        options.append((earlier, earlier + duration, skipStep))
                        options.append((later, later + duration, skipStep))
            
            BestOption = None
            BestScore = None
            BestExistingOverlap = 0.0
            BestSelectedOverlap = 0.0
            SkipScore = -(data["SkipPenalty"] * confidece)
            ScoredOptions = []

            for OptionalStart, OptionalEnd, moved in options:
                ExistingOverlap = 0.0
                for event in existing:
                    ExistingOverlap += getOverlappingMinutes(OptionalStart, OptionalEnd, event.start_time, event.end_time)

                SelectedOverlap = 0.0
                for start, end in selected_ranges:
                    SelectedOverlap += getOverlappingMinutes(OptionalStart, OptionalEnd, start, end)
                    
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
                        penalties += BufferPenalty
                        BufferRule += (BufferMinutes - GapBefore)
                    
                    if 0 < GapAfter < BufferMinutes:
                        penalties += BufferPenalty
                        BufferRule += (BufferMinutes - GapAfter)

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
            NeedsAlternatives = (
                moved > 0 or BestExistingOverlap > 0 or BestSelectedOverlap > 0 or BufferRule >= 5
            )

            AlternativeRule = 1.5 if NeedsAlternatives else 0.25
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