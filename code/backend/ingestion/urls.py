from django.urls import path, include
from .views import FileUploadAPIView, CandidateView, SmartPlanView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"candidates", CandidateView, basename="candidate")

# routes for upload, smart planning and candidate CRUD
urlpatterns = [
    path("uploads/", FileUploadAPIView.as_view(), name="file-upload-api"),
    path("smart/plan/", SmartPlanView.as_view(),name="smart-plan"),
    path("", include(router.urls)),
]
