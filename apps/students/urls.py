"""Student URL routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.students.views import EnrollmentViewSet, ImportBatchViewSet, StudentViewSet

router = DefaultRouter()
router.register("students", StudentViewSet, basename="student")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("import-batches", ImportBatchViewSet, basename="import-batch")

urlpatterns = [
    path("", include(router.urls)),
]
