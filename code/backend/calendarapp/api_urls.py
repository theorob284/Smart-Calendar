from rest_framework.routers import DefaultRouter
from .api_views import EventViewSet

# automatically generates REST routes for EventViewSet
router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")

urlpatterns = router.urls
