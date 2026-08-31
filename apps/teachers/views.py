"""Teacher API views."""

from __future__ import annotations

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets

from apps.core.models import User
from apps.teachers.models import Teacher
from apps.teachers.serializers import TeacherCreateSerializer, TeacherSerializer


class IsAdminOrHeadmasterOrTeacher(permissions.BasePermission):
    """Admin, Headmaster, or Teacher roles may access."""

    def has_permission(self, request: viewsets, view: viewsets) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in [
            User.HEADMASTER,
            User.ADMIN,
            User.TEACHER,
        ]


class TeacherFilter(filters.FilterSet):
    class Meta:
        model = Teacher
        fields = {
            "employment_status": ["exact"],
            "name": ["icontains"],
        }


class TeacherViewSet(viewsets.ModelViewSet[Teacher]):
    """CRUD for Teacher profiles."""

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrHeadmasterOrTeacher]
    filterset_class = TeacherFilter
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return TeacherCreateSerializer
        return TeacherSerializer
