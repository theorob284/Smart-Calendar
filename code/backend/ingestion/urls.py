from django.urls import path
from .api_views import FileUploadAPIView

urlpatterns = [
    path("uploads/", FileUploadAPIView.as_view(), name="file-upload-api"),
]
