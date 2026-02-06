from django.urls import path, include
from .views import FileUploadAPIView, CandidateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"candidates", CandidateView, basename="candidate")

urlpatterns = [
    path("uploads/", FileUploadAPIView.as_view(), name="file-upload-api"),
    path("", include(router.urls)),
]
