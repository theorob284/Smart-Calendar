from django.db import models

# Create your models here.

class AlternativeGroup(models.Model):
    description = models.CharField(max_length = 300, blank = True)

    def __str__(self):
        return f"Group {self.id}"

class Event(models.Model):
    title = models.CharField(max_length=30)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100, blank = True)
    event_type = models.CharField(max_length=30, blank = True)
    confidence = models.DecimalField(max_digits=3, decimal_places=2, null= True, blank=True)

    group = models.ForeignKey(
        AlternativeGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"

class ConflictRecord(models.Model):
    event1 = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="conflicts_as_event1")
    event2 = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="conflicts_as_event2")
    severity = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conflict {self.event1_id} vs {self.event2_id}"