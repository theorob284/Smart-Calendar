import os
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Document, ExtractedEventCandidate
from .serializers import DocumentSerializer, ExtractedEventCandidateSerializer
from .parsers import parse_ics, extractPDF
from calendarapp.serializers import EventSerializer

class FileUploadAPIView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        doc_id = response.data["id"]
        doc = Document.objects.get(id=doc_id)

        file_path = doc.file.path
        ext = os.path.splitext(doc.file.name.lower())[1]

        candidates = []

        if ext == ".ics":
            candidates = parse_ics(file_path)

        elif ext == ".pdf":
            text = extractPDF(file_path)
            # One candidate for now, later split
            candidates = [{
                "title": f"Imported from {doc.title}",
                "start_time": None,
                "end_time": None,
                "location": "",
                "confidence": 0.2,
                "raw_text": text[:5000],  # avoid huge DB entry
            }]
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            candidates = [{
                "title": f"OCR pending for image: {doc.title}",
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
                "raw_text": doc.file.name,
                "start_time": None,
                "end_time": None,
                "location": "",
            }]

        created = []
        for c in candidates:
            obj = ExtractedEventCandidate.objects.create(
                document=doc,
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

        # Return normal upload response + candidates
        return Response(
            {
                "document": response.data,
                "candidates_created": created,
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

        if cand.status == "pending":
            return Response({"error": "only candidates in the pending state can be edited"}, status=409)
        
        ConvertToEvent = {
            "title": cand.title,
            "start_time": cand.start_time,
            "end_time": cand.end_time,
            "location": cand.location
        }

        serializer = EventSerializer(data=ConvertToEvent)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cand.status = ExtractedEventCandidate.Status.approved
        cand.reviewed_at = timezone.now()
        cand.save()

        return Response({
            "candidate": self.get_serializer(cand).data,
            "event": serializer.data
        }, status=201)