from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.
class Document (models.Model):
    # upload batch (can be multiple files)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents",)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.title
    
class ExtractedEventCandidate(models.Model):
    # review the state of the extracted candidate
    class Status(models.TextChoices):
        pending = "PENDING", "pending"
        approved = "APPROVED", "approved"
        rejected = "REJECTED", "rejected"

    # source document that produced this candidate
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="candidates")


    # parsed event fields
    title = models.CharField(max_length=150, blank = True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=300, blank=True)
    description = models.TextField(max_length= 400 ,blank=True)
    event_type = models.TextField(max_length=30, blank=True)


    # confidence score from extraction logic
    confidence = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices = Status.choices, default=Status.pending)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # liks to a real event object if approved 
    approveEvent = models.ForeignKey("calendarapp.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="candidateSource")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Candidate {self.id} ({self.status}) from Doc {self.document_id}: {self.title}"

