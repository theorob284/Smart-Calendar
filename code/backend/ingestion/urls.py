from django.urls import path
from .api_views import FileUploadAPIView, CandidateListAPIView

urlpatterns = [
    path("uploads/", FileUploadAPIView.as_view(), name="file-upload-api"),
    path("candidates/", CandidateListAPIView.as_view(),name="candidate-list" ),
]
