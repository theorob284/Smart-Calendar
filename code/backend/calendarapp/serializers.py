from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "location",
            "event_type",
            "confidence",
            "group",
        ]

    def validate(self, data):
        val_title = data.get("title")
        if not val_title:
            raise serializers.ValidationError("Each event must have a title.")
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end and end <= start:
            raise serializers.ValidationError("end_time must be after start_time.")
        return data