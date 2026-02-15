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

class SmartPlanSerializer(serializers.Serializer):

    GetDocumentIds = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    ExistingEvents = serializers.BooleanField(default=True)
    ConflictPenalty = serializers.FloatField(default=1.0)
    ConfidenceWeight = serializers.FloatField(default=1.0)
    AllowReschedule = serializers.BooleanField(default=False)
    MaxTimeShift = serializers.IntegerField(default=60)
    SkipPenalty = serializers.FloatField(default=2.0)
    MovePenalty = serializers.FloatField(default = 0.05)
    ExistingConflictMulti = serializers.FloatField(default=3.0)
    WorkStart = serializers.IntegerField(default=9, min_value=0, max_value=23)
    WorkEnd = serializers.IntegerField(default=17, min_value=1, max_value=24)
    AvoidWeekends = serializers.BooleanField(default=True)
    OutsideWorkPenalty = serializers.FloatField(default=5.0)
    WeekendPenalty = serializers.FloatField(default=10.0)
    WorkHours = serializers.BooleanField(default=False)