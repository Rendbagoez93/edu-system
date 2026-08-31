"""Student API views."""

from __future__ import annotations

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.request import Request

from apps.core.models import User
from apps.students.models import Enrollment, ImportBatch, Student
from apps.students.serializers import (
    EnrollmentSerializer,
    ImportBatchSerializer,
    StudentCreateSerializer,
    StudentSerializer,
)


class IsAdminOrHeadmasterOrTeacher(permissions.BasePermission):
    """Admin, Headmaster, or Teacher roles may access."""

    def has_permission(self, request: Request, view: viewsets) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in [
            User.HEADMASTER,
            User.ADMIN,
            User.TEACHER,
        ]


class StudentFilter(filters.FilterSet):
    class Meta:
        model = Student
        fields = {
            "gender": ["exact"],
            "name": ["icontains"],
        }


class EnrollmentFilter(filters.FilterSet):
    class Meta:
        model = Enrollment
        fields = {
            "status": ["exact"],
            "academic_year": ["exact"],
        }


class ImportBatchFilter(filters.FilterSet):
    class Meta:
        model = ImportBatch
        fields = {
            "status": ["exact"],
        }


class StudentViewSet(viewsets.ModelViewSet[Student]):
    """CRUD for Student profiles."""

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrHeadmasterOrTeacher]
    filterset_class = StudentFilter
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return StudentCreateSerializer
        return StudentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet[Enrollment]):
    """CRUD for Student enrollments."""

    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrHeadmasterOrTeacher]
    filterset_class = EnrollmentFilter
    http_method_names = ["get", "post", "put", "patch", "head", "options"]


class ImportBatchViewSet(viewsets.ModelViewSet[ImportBatch]):
    """CRUD for ImportBatch records."""

    queryset = ImportBatch.objects.all()
    serializer_class = ImportBatchSerializer
    permission_classes = [IsAdminOrHeadmasterOrTeacher]
    filterset_class = ImportBatchFilter
    http_method_names = ["get", "post", "head", "options"]
