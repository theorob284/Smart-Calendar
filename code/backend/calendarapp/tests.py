from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from calendarapp.models import Event

class EventAPITests(APITestCase):
    @staticmethod
    def to_z(dt):
        #Convert aware UTC datetime to ISO string with Z suffix.
        return dt.isoformat().replace("+00:00", "Z")

    def setUp(self):
        self.url = reverse("event-list")
        self.now = timezone.now().replace(microsecond=0)

        # Base events used by multiple tests
        self.create_event("Overlapping Event", hours_start=1, hours_end=2)
        self.create_event("Outside Event", days_start=2, days_end=2, hours_end=1)
        self.create_event("Spanning Event", hours_start=-1, days_end=1)

        self.range_start = self.to_z(self.now)
        self.range_end = self.to_z(self.now + timedelta(hours=3))

    # ---------- Helpers ----------
    def create_event(self,title,hours_start=0,hours_end=None,days_start=0,days_end=0,location="",event_type="",group=None,):
        start = self.now + timedelta(days=days_start, hours=hours_start)

        if hours_end is None and days_end == 0:
            # Default 1 hour duration if end not specified
            end = start + timedelta(hours=1)
        else:
            end = self.now + timedelta(days=days_end, hours=hours_end or 0)

        return Event.objects.create( title=title,start_time=start,end_time=end,location=location,event_type=event_type,group=group,)

    def api_get(self, params=None):
        #GET helper that always hits the correct endpoint.
        return self.client.get(self.url, params or {})

    def titles_from(self, response):
        #Extract a set of titles from a list response.
        return {e["title"] for e in response.data}

    # ---------- Tests ----------
    def test_event_overlap_filtering(self):
        response = self.api_get({"start": self.range_start, "end": self.range_end})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = self.titles_from(response)
        self.assertIn("Overlapping Event", titles)
        self.assertIn("Spanning Event", titles)
        self.assertNotIn("Outside Event", titles)

    def test_missing_one_param_returns_400(self):
        response = self.api_get({"start": self.range_start})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.api_get({"end": self.range_end})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_datetime_format_returns_400(self):
        response = self.api_get({"start": "not-a-datetime", "end": self.range_end})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_before_or_equal_start_returns_400(self):
        start = self.to_z(self.now)
        end_before = self.to_z(self.now - timedelta(hours=1))

        response = self.api_get({"start": start, "end": end_before})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.api_get({"start": start, "end": start})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_event_type(self):
        self.create_event("Meeting A", hours_start=4, hours_end=5, event_type="Meeting")
        self.create_event("Lecture A", hours_start=6, hours_end=7, event_type="Lecture")

        response = self.api_get({"event_type": "Meeting"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = self.titles_from(response)
        self.assertIn("Meeting A", titles)
        self.assertNotIn("Lecture A", titles)

    def test_filter_by_location_contains_case_insensitive(self):
        self.create_event("Room Event", hours_start=4, hours_end=5, location="Room A")
        self.create_event("Cafe Event", hours_start=6, hours_end=7, location="Campus Cafe")

        response = self.api_get({"location": "room"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = self.titles_from(response)
        self.assertIn("Room Event", titles)
        self.assertNotIn("Cafe Event", titles)

    def test_ordering_by_start_time_desc(self):
        self.create_event("Earlier", hours_start=1, hours_end=2)
        self.create_event("Later", hours_start=10, hours_end=11)

        response = self.api_get({"ordering": "-start_time"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_titles = [e["title"] for e in response.data]
        self.assertLess(returned_titles.index("Later"), returned_titles.index("Earlier"))

    def test_invalid_ordering_field_returns_400(self):
        response = self.api_get({"ordering": "does_not_exist"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
