from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    # fields for compatibility with FullCallendar (read-only)
    start = serializers.DateTimeField(source = "start_time", read_only = True)
    end = serializers.DateTimeField(source = "end_time", read_only = True)
    
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "start", # field for FullCallendar
            "end", # field for FullCallendar
            "description",
            "location",
            "event_type",
            "confidence",
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