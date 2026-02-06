from django.db import models
from django.utils import timezone


# Create your models here.
class Document (models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.title
    
class ExtractedEventCandidate(models.Model):

    class Status(models.TextChoices):
        pending = "PENDING", "pending"
        approved = "APPROVED", "approved"
        rejected = "REJECTED", "rejected"

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="candidates")

    title = models.CharField(max_length=50, blank = True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=300, blank=True)
    raw_text = models.TextField(blank=True)

    confidence = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices = Status.choices, default=Status.pending)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    approveEvent = models.ForeignKey("calendarapp.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="candidateSource")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Candidate {self.id} ({self.status}) from Doc {self.document_id}: {self.title}"

