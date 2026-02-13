import os
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
        FilesDoc = Document.objects.create(title=FilesTitle, file=files[0])

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

        return Response({
            "candidate": self.get_serializer(cand).data,
            "event": serializer.data
        }, status=201)
    
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
            existing = Event.objects.all()
        else:
            existing = []
        
        selected = []
        skipped = []

        def candConfidence(c):
            if c.confidence is not None:
                return float(c.confidence)
            else:
                return 0.5
            
        candidates = list(CandidateSet)
        candidates.sort(key=lambda c: (-candConfidence(c), c.start_time or timezone.now()))
        
        selected_ranges = []

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
            
            SelectedConflicts = False
            for (start, end) in selected_ranges:
                if cand.start_time < end and cand.end_time > start: #overlaps
                    SelectedConflicts = True
                    break
            
            if SelectedConflicts:
                skipped.append({"candidate_id": cand.id, "reason": "Conflicts"})
                continue
            
            ExistingConflicts = False
            if data["ExistingEvents"]:
                for ev in existing:
                    if cand.start_time < ev.end_time and cand.end_time > ev.start_time: #overlaps
                        ExistingConflicts = True
                        break
            
            if ExistingConflicts:
                skipped.append({"candidate_id": cand.id, "reason": "Conflicts"})
                continue


            selected.append({
                "candidate_id": cand.id,
                "title": cand.title,
                "start_time": cand.start_time,
                "end_time": cand.end_time,
                "confidence": candConfidence(cand)
            })
            selected_ranges.append((cand.start_time, cand.end_time))
        
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