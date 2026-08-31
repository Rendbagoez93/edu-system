"""Teacher URL routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.teachers.views import TeacherViewSet

router = DefaultRouter()
router.register("teachers", TeacherViewSet, basename="teacher")

urlpatterns = [
    path("", include(router.urls)),
]
