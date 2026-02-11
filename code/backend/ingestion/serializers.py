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
        read_only_fields = ["status", "reviewed_at", "approveEvent", "created_at", "updated_at"]

class SmartPlanSerializer(serializers.ModelSerializer):

    GetDocumentIds = serializers.ListField(chile=serializers.IntegerField(), allow_empty=False)
    ExistingEvents = serializers.BooleanField(default=True)
    ConflictPenalty = serializers.FloatField(default=1.0)
    ConfidenceWeight = serializers.FloatField(default=1.0)