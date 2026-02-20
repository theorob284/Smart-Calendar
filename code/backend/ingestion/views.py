import os

from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import AllowAny

from .models import Document, ExtractedEventCandidate
from .serializers import DocumentSerializer, ExtractedEventCandidateSerializer, SmartPlanSerializer
from .parsers import parse_ics, extractPDF, ExtractedTextToEvent, extractOCR
from calendarapp.serializers import EventSerializer
from calendarapp.models import Event
from calendarapp.utils import CreateConflictRecord

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Username is required.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("That username is already taken.")
        return value

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        user = User.objects.create_user(
            username=ser.validated_data["username"],
            password=ser.validated_data["password"],
        )
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)
    
#convert uploads into ExtractedEventCandidate records
class FileUploadAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.none()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):

        #accept multiple files if needed
        allowed_ext = [".ics", ".pdf", ".png", ".jpg", ".jpeg", ".webp"]
        files = request.FILES.getlist("files")
        if not files:
            OneFile =  request.FILES.get("file")
            if OneFile:
                files = [OneFile]
        
        if not files:
            return Response({"detail": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        for f in files:
            ext = os.path.splitext(f.name.lower())[1]
            if ext not in allowed_ext:
                raise ValidationError({"error": "unsupported_file_type","message": f"{f.name} is not supported."})
        
        FilesTitle = request.data.get("title") or f"Upload ({len(files)} files)"
        FilesDoc = Document.objects.create(title=FilesTitle, owner=request.user)
        #create parent doc to represent batch

        #multiple filetypes supported (.ics, .pdf, images)
        def parseFiles(file_path,name):
            candidates = []
            ext = os.path.splitext(name.lower())[1]
            #parsing logic based on file extension
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
                        "description": "",  # avoid huge DB entry
                        "event_type": "",
                    }]
            elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
                text = extractOCR(file_path)
                candidates = ExtractedTextToEvent(text)
                #if OCR yields no usable events
                if not candidates:
                    candidates = [{
                        "title": f"OCR pending for image: {name}",
                        "description": "Image uploaded. OCR not implemented yet.",
                        "confidence": 0.0,
                        "start_time": None,
                        "end_time": None,
                        "location": "",
                        "event_type": "",
                    }]
            #minimal placeholder is stored in case of unsupported file type 
            else:
                candidates = [{
                    "title": "Unsupported file type (stored only)",
                    "confidence": 0.0,
                    "description": name,
                    "start_time": None,
                    "end_time": None,
                    "location": "",
                    "event_type": ""
                }]
            return candidates

        created = []
        #each file is processed independently
        for f in files:
            # temporarily save uploaded file
            childDoc = Document.objects.create(title=f.name, file=f, owner=request.user)
            file_path = childDoc.file.path
            # file is parsed into event candidate dicts...
            candidates = parseFiles(file_path, childDoc.file.name)
            # and then converted into DB rows
            for c in candidates:
                obj = ExtractedEventCandidate.objects.create(
                    document=FilesDoc,
                    title=c.get("title", ""),
                    start_time=c.get("start_time"),
                    end_time=c.get("end_time"),
                    location=c.get("location", ""),
                    description=c.get("description", ""),
                    event_type = c.get("event_type", ""),
                    confidence=c.get("confidence"),
                )
                # collect response metadata
                created.append({
                    "id": obj.id,
                    "title": obj.title,
                    "start_time": obj.start_time,
                    "end_time": obj.end_time,
                    "location": obj.location,
                    "event_type": obj.event_type,
                    "description": obj.description,
                    "confidence": obj.confidence,
                })
            #cleanup file storage
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

#CRUD & review for extracted candidates
class CandidateView(viewsets.ModelViewSet):
    serializer_class = ExtractedEventCandidateSerializer
    permission_classes = [IsAuthenticated]

    # filtering by document of status
    def get_queryset(self):

        qs = ExtractedEventCandidate.objects.filter(document__owner=self.request.user).order_by("id")

        document_id = self.request.query_params.get("document")
        if document_id:
            qs = qs.filter(document_id=document_id)

        GetStatus = self.request.query_params.get("status")
        if GetStatus:
            qs = qs.filter(status=GetStatus)
        
        return qs
    #only allow editing while candidate is still pending
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

    # accept candidate and convert into real event
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
        

        #ensure valid time range
        if not cand.start_time or not cand.end_time:
            return Response({"error": "Missing start or end time"}, status=400)
        
        ConvertToEvent = {
            "title": cand.title,
            "start_time": cand.start_time,
            "end_time": cand.end_time,
            "location": cand.location,
            "event_type": cand.event_type,
            "description": cand.description,
            "confidence": cand.confidence
        }

        #create real calendar event
        serializer = EventSerializer(data=ConvertToEvent)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(owner=request.user)

        CreateConflictRecord(event) #compute conflicts

        #mark candidates as approved
        cand.status = ExtractedEventCandidate.Status.approved
        cand.reviewed_at = timezone.now()
        cand.approveEvent = event
        cand.save()

        return Response({"candidate": self.get_serializer(cand).data,"event": serializer.data}, status=201)
    
# smart scheduling engine
# greedy scoring based planner
class SmartPlanView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        SmartSerializer = SmartPlanSerializer(data=request.data)
        SmartSerializer.is_valid(raise_exception=True)
        data = SmartSerializer.validated_data

        #only pending candidates
        CandidateSet = ExtractedEventCandidate.objects.filter(
            status=ExtractedEventCandidate.Status.pending,
            document_id__in=data["GetDocumentIds"],
            document__owner=request.user,
        )

        #option to include existing events in conflict scoring
        if data["ExistingEvents"]:
            existing = list(Event.objects.filter(owner=request.user))
        else:
            existing = []
        
        selected = []
        skipped = []

        def candConfidence(c):
            if c.confidence is not None:
                return float(c.confidence)
            else:
                return 0.5

        #compute interval overlap in minutes 
        def getOverlappingMinutes (Astart, Aend, Bstart, Bend):
            Latest = max(Astart, Bstart)
            Earliest = min(Aend, Bend)
            if Latest >= Earliest:
                return 0.0
            return (Earliest - Latest).total_seconds() / 60.0
            
        #longer duration first
        def SortCandidates(Sortkey):
            if Sortkey.start_time and Sortkey.end_time and Sortkey.end_time > Sortkey.start_time:
                duration = (Sortkey.end_time - Sortkey.start_time).total_seconds()
            else:
                duration = -1
            return (-duration, -candConfidence(Sortkey), Sortkey.start_time or timezone.now())
        
        #avoid duplicate groups
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
            # Merge overlapping busy intervals to simplify gap detection
            busy = MergeIntervals(GetGapStart)

            #artificial boundary markers at window edges
            timeline = [(GapStart, GapStart)] + busy + [(GapEnd, GapEnd)]
            candidates = []
            DurationSeconds = Duration.total_seconds()

            for i in range(len(timeline) - 1): #detect free gaps in intervals

                #gap lies between end two blocks
                GapStart = timeline[i][1]
                GapEnd = timeline[i + 1][0]

                #skip invalid gaps
                if GapEnd <= GapStart:
                    continue

                #skip gaps too small
                if (GapEnd - GapStart).total_seconds() < DurationSeconds:
                    continue
                
                # place event at beginning of gap
                start1 = GapStart
                event1 = start1 + Duration

                # place event at end of gap
                Start2 = GapEnd - Duration
                event2 = GapEnd


                # stay close to original target
                Start3 = Target
                if Start3 < GapStart:
                    Start3 = GapStart
                if (Start3 + Duration) > GapEnd:
                    Start3 = GapEnd - Duration
                event3 = Start3 + Duration


                # using set in order for avoid duplicate placements
                for start, end in {(start1, event1), (Start2, event2), (Start3, event3)}:

                    #compute how far we've moved from original time
                    moved = abs((start - Target).total_seconds()) / 60.0
                    candidates.append((start, end, moved))
            
            # deduplicate and keep minimal move distance
            best = {}
            for start, end, moved in candidates:
                key = (start, end)
                if key not in best or moved < best[key]:
                    best[key] = moved
            
            options = [(start, end, best[(start, end)]) for (start, end) in best.keys()]
            options.sort(key=lambda x: x[2]) #we prefer minimal movement from origin
            return options[:MaxGapOptions]


        #convert queryset to list
        candidates = list(CandidateSet)
        candidates.sort(key=SortCandidates) #sort
        
        selected_ranges = []        #track time intervals
        selectedGroups = set()      #prevent dupes


        for cand in candidates: #selection loop
            #validation filters
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
            
            # original time as default option
            options = [(cand.start_time, cand.end_time, 0)]
            if data["AllowReschedule"] and data["MaxTimeShift"] > 0:
                StartWindow = cand.start_time - timedelta(minutes=data["MaxTimeShift"])
                EndWindow = cand.start_time + timedelta(minutes=data["MaxTimeShift"])

                # busy interval list
                BusyIntervals = []
                if data["ExistingEvents"]:
                    BusyIntervals.extend((event.start_time, event.end_time) for event in existing)
                BusyIntervals.extend(selected_ranges)

                GapOptions = GetGapOptions(Target=cand.start_time, Duration=duration, Busy=BusyIntervals, GapStart = StartWindow, GapEnd=EndWindow, MaxGapOptions=10)

                options.extend(GapOptions)
            
            ## Scoring

            BestOption = None
            BestScore = None
            BestExistingOverlap = 0.0
            BestSelectedOverlap = 0.0
            SkipScore = -(data["SkipPenalty"] * confidece) #skip event if score below threshold
            ScoredOptions = []
            BestBufferRule = 0.0

            for OptionalStart, OptionalEnd, moved in options:
                # compute overlap with existing events
                ExistingOverlapMinutes = 0.0
                for event in existing:
                    ExistingOverlapMinutes += getOverlappingMinutes(OptionalStart, OptionalEnd, event.start_time, event.end_time)

                # compute overlap with selected canditates
                SelectedOverlapMinutes = 0.0
                for start, end in selected_ranges:
                    SelectedOverlapMinutes += getOverlappingMinutes(OptionalStart, OptionalEnd, start, end)

                #convert minutes to hours
                ExistingOverlap = ExistingOverlapMinutes / 60.0
                SelectedOverlap = SelectedOverlapMinutes / 60.0
                    
                #positive contr.
                Benefit = data["ConfidenceWeight"] * confidece
                penalties = 0.0
                #penalize movement
                penalties += data["MovePenalty"] * moved
                #penalize conflicts
                penalties += data["ConflictPenalty"] * (data["ExistingConflictMulti"] * ExistingOverlap + SelectedOverlap)
                #enforce gap between events
                BufferMinutes = data["BufferMinutes"]
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
                #abide work hours and weekends
                if data["WorkHours"]:
                    WorkStart = data["WorkStart"]
                    WorkEnd = data["WorkEnd"]

                    if OptionalStart.hour < WorkStart or OptionalEnd.hour >= WorkEnd:
                        penalties += data["OutsideWorkPenalty"]
                    if data["AvoidWeekends"] and OptionalStart.weekday() >= 5:
                        penalties += data["WeekendPenalty"]

                score = Benefit - penalties #final score


                # track best scoring option
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

                # descending sort
            ScoredOptions.sort(key=lambda x: x["score"], reverse=True)
            # skip if BestScore not strong enough
            if BestScore is None or BestScore <= SkipScore:
                skipped.append({
                    "candidate_id": cand.id,
                    "reason": "No option to schedule",
                    "bestOptionScore": BestScore,
                    "skip_threshold": SkipScore,
                })
                continue
            
            ChosenStart, ChosenEnd, moved = BestOption


            #generate alternatives
            AlternativeRule = 2 #tolerance window

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

            # prevent dupes
            Gkey = GroupKey(cand)
            if Gkey in selectedGroups:
                skipped.append({"candidate_id": cand.id, "reason": "Already in alternative group"})
                continue


            #accept candidate
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