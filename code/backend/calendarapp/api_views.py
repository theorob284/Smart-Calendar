from rest_framework import viewsets
from .models import Event
from .serializers import EventSerializer

from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware
from django.conf import settings
from rest_framework.exceptions import ValidationError
from .utils import CreateConflictRecord

class EventViewSet(viewsets.ModelViewSet):
    #queryset = Event.objects.all().order_by("start_time") 
    serializer_class = EventSerializer

    ordered_Fields = {"start_time", "end_time", "title", "location", "event_type", "description"}

    def perform_create(self, serializer):
        event = serializer.save()
        CreateConflictRecord(event)

    def get_queryset(self):
        queryset = Event.objects.all()

        #optional field filters
        # location, time, group, title, event_type 
        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        location = self.request.query_params.get("location")
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        description = self.request.query_params.get("description")
        if description:
            queryset = queryset.filter(description=description)

        start_param = self.request.query_params.get("start")
        end_param = self.request.query_params.get("end")

        if start_param or end_param:

            if not start_param or not end_param:
                raise ValidationError({"Error": "Provide both 'start' and 'end' query parameters."})
            
            start_dateTime, end_dateTime = parse_datetime(start_param), parse_datetime(end_param)

            #Ensure correct datetime:
            if start_dateTime is None or end_dateTime is None:
                raise ValidationError( {"Error: Either start datetime or end datetime in incorrect format: start={start_param}, end={end_param}"})
            
            if settings.USE_TZ:
                if is_naive(start_dateTime):
                    start_dateTime = make_aware(start_dateTime)
                if is_naive(end_dateTime):
                    end_dateTime = make_aware(end_dateTime)

            if end_dateTime <= start_dateTime:
                raise ValidationError({"Error: End date time must happen after Start time"})
            
            queryset = queryset.filter(start_time__lt=end_dateTime, end_time__gt=start_dateTime)

        ordering = self.request.query_params.get("ordering", "start_time")

        raw_field = ordering.lstrip("-")

        if raw_field not in self.ordered_Fields:
            raise ValidationError(
                {
                    "detail": (
                        f"Invalid ordering field '{raw_field}'. "
                        f"Allowed: {sorted(self.ordered_Fields)}"
                    )
                }    
            )

        return queryset.order_by(ordering)
    