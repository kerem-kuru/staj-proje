from rest_framework.routers import SimpleRouter

from .views import StudentProfileViewSet

router = SimpleRouter()
router.register("", StudentProfileViewSet, basename="student")

urlpatterns = router.urls
