"""Core URL routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.views import AcademicYearViewSet, AuditLogViewSet, SchoolViewSet, UserViewSet

router = DefaultRouter()
router.register("schools", SchoolViewSet, basename="school")
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("users", UserViewSet, basename="user")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]
