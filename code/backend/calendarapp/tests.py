from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from calendarapp.serializers import EventSerializer

#This code tests validation of required rules for events
class EventValidationTests(TestCase):
    
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)

    #testing that a title is required
    def test_title_is_required(self):
        data = {"start_time": self.now, "end_time": self.now + timedelta(hours=1)}
        serializer = EventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    #testing that the end time must be after start time
    def test_end_must_be_after_start(self):
        data = {"title": "Bad Event", "start_time": self.now + timedelta(hours=2), "end_time": self.now + timedelta(hours=1)}
        serializer = EventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    # testing that an event is valid with the required information
    def test_valid_event_passes(self):
        data = {
            "title": "Good Event",
            "start_time": self.now + timedelta(hours=1),
            "end_time": self.now + timedelta(hours=2),
            "location": "Room A",
            "event_type": "Meeting",
            "confidence": None, 
            "group": None,
        }
        serializer = EventSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
