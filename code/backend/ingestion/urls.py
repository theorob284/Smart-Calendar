from django.urls import path
from .api_views import FileUploadAPIView, CandidateView

urlpatterns = [
    path("uploads/", FileUploadAPIView.as_view(), name="file-upload-api"),
    path("candidates/", CandidateView.as_view(),name="candidate-list" ),
]
