from django.db import models
from django.conf import settings

# Create your models here.

class Event(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events",)
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=150, blank = True)
    description = models.CharField(max_length=400, blank = True)
    event_type = models.CharField(max_length=30, blank = True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null= True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"

class ConflictRecord(models.Model):
    event1 = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="conflicts_as_event1")
    event2 = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="conflicts_as_event2")
    severity = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conflict {self.event1_id} vs {self.event2_id}"