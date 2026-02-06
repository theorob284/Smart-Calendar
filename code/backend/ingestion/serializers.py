from rest_framework import serializers
from .models import Document, ExtractedEventCandidate

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "file"]

class ExtractedEventCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedEventCandidate
        fields = "__all__"
        ReadView = ["status", "reviewed_at", "approveEvent", "created_at", "updated_at"]