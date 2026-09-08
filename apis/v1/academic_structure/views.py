"""Academic structure API views."""

from __future__ import annotations

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets

from apps.academic_structure.models import ClassSection, GradeLevel, Major, Subject
from apps.academic_structure.serializers import (
    ClassSectionCreateSerializer,
    ClassSectionSerializer,
    GradeLevelCreateSerializer,
    GradeLevelSerializer,
    MajorCreateSerializer,
    MajorSerializer,
    SubjectCreateSerializer,
    SubjectSerializer,
)
from apps.core.models import UserRole


class IsAdminOrHeadmaster(permissions.BasePermission):
    """Admin or Headmaster roles may access."""

    def has_permission(self, request: viewsets, view: viewsets) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in [UserRole.HEADMASTER, UserRole.ADMIN]


class GradeLevelFilter(filters.FilterSet):
    class Meta:
        model = GradeLevel
        fields = {
            "name": ["exact", "icontains"],
        }


class GradeLevelViewSet(viewsets.ModelViewSet[GradeLevel]):
    """CRUD for GradeLevel (Tingkat)."""

    queryset = GradeLevel.objects.all()
    serializer_class = GradeLevelSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = GradeLevelFilter
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return GradeLevelCreateSerializer
        return GradeLevelSerializer

    def perform_destroy(self, instance: GradeLevel) -> None:
        instance.soft_delete()


class MajorFilter(filters.FilterSet):
    class Meta:
        model = Major
        fields = {
            "name": ["exact", "icontains"],
            "is_active": ["exact"],
        }


class MajorViewSet(viewsets.ModelViewSet[Major]):
    """CRUD for Major (Jurusan/Peminatan)."""

    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = MajorFilter
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return MajorCreateSerializer
        return MajorSerializer

    def perform_destroy(self, instance: Major) -> None:
        instance.soft_delete()


class SubjectFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    code = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Subject
        fields = ["name", "code", "is_active"]


class SubjectViewSet(viewsets.ModelViewSet[Subject]):
    """CRUD for Subject (Mata Pelajaran)."""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = SubjectFilter
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return SubjectCreateSerializer
        return SubjectSerializer

    def perform_destroy(self, instance: Subject) -> None:
        instance.soft_delete()


class ClassSectionFilter(filters.FilterSet):
    class Meta:
        model = ClassSection
        fields = {
            "grade_level": ["exact"],
            "academic_year": ["exact"],
            "major": ["exact"],
            "name": ["exact", "icontains"],
        }


class ClassSectionViewSet(viewsets.ModelViewSet[ClassSection]):
    """CRUD for ClassSection (Kelas)."""

    queryset = ClassSection.objects.all()
    serializer_class = ClassSectionSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = ClassSectionFilter
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return ClassSectionCreateSerializer
        return ClassSectionSerializer

    def perform_destroy(self, instance: ClassSection) -> None:
        instance.soft_delete()
