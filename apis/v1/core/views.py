"""Core API views."""

from __future__ import annotations

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.models import AcademicYear, AuditLog, School, User, UserRole
from apps.core.selectors import get_active_academic_year, get_school
from apps.core.serializers import (
    AcademicYearSerializer,
    AuditLogSerializer,
    SchoolSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from apps.core.services import activate_academic_year


class IsAdminOrHeadmaster(permissions.BasePermission):
    """Only Admin and Headmaster roles may access."""

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.role in [UserRole.HEADMASTER, UserRole.ADMIN]
        )


class SchoolFilter(filters.FilterSet):
    class Meta:
        model = School
        fields = {
            "npsn": ["exact"],
            "name": ["icontains"],
            "level": ["exact"],
        }


class AcademicYearFilter(filters.FilterSet):
    class Meta:
        model = AcademicYear
        fields = {
            "label": ["exact", "icontains"],
            "semester": ["exact"],
            "is_active": ["exact"],
        }


class AuditLogFilter(filters.FilterSet):
    class Meta:
        model = AuditLog
        fields = {
            "action": ["exact"],
            "content_type": ["exact"],
            "user": ["exact"],
        }


class SchoolViewSet(viewsets.ModelViewSet[School]):
    """CRUD for School. Single-tenant: only one school per deployment."""

    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = SchoolFilter
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.action == "current":
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def current(self, request: Request) -> Response:
        """Return the current school profile."""
        school = get_school()
        if school is None:
            return Response({"detail": "School not configured."}, status=404)
        serializer = self.get_serializer(school)
        return Response(serializer.data)


class AcademicYearViewSet(viewsets.ModelViewSet[AcademicYear]):
    """CRUD for AcademicYear."""

    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = AcademicYearFilter
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    @action(detail=False, methods=["get"])
    def active(self, request: Request) -> Response:
        """Return the currently active academic year."""
        year = get_active_academic_year()
        if year is None:
            return Response({"detail": "No active academic year."}, status=404)
        serializer = self.get_serializer(year)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def activate(self, request: Request, pk: str | None = None) -> Response:
        """Activate this academic year, deactivating all others."""
        year = self.get_object()
        year = activate_academic_year(year)
        serializer = self.get_serializer(year)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet[User]):
    """CRUD for User accounts."""

    queryset = User.objects.all()
    permission_classes = [IsAdminOrHeadmaster]
    filterset_fields = {
        "role": ["exact"],
        "is_active": ["exact"],
    }
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet[AuditLog]):
    """Read-only audit log."""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrHeadmaster]
    filterset_class = AuditLogFilter
