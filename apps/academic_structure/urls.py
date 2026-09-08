"""Academic structure URL routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.academic_structure.views import (
    ClassSectionViewSet,
    GradeLevelViewSet,
    MajorViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register("grade-levels", GradeLevelViewSet, basename="grade-level")
router.register("majors", MajorViewSet, basename="major")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("class-sections", ClassSectionViewSet, basename="class-section")

urlpatterns = [
    path("", include(router.urls)),
]
