import os
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import Document, ExtractedEventCandidate
from .serializers import DocumentSerializer, ExtractedEventCandidateSerializer
from .parsers import parse_ics, extractPDF

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
            ExtractedEventCandidate.objects.create(
            document=doc,
            title=f"OCR pending for image: {doc.title}",
            raw_text="Image uploaded. OCR not implemented yet.",
            confidence=0.0, )
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

class CandidateListAPIView(generics.ListAPIView):
    serializer_class = ExtractedEventCandidateSerializer

    def get_queryset(self):

        qs = ExtractedEventCandidate.objects.all().order_by("id")

        document_id = self.request.query_params.get("document")
        if document_id:
            qs = qs.filter(document_id=document_id)
        return qs