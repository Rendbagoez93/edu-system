"""Django admin for core models."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.core.models import AcademicYear, AuditLog, School, User


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["npsn", "name", "level", "kepala_sekolah", "created_at"]
    list_filter = ["level"]
    search_fields = ["npsn", "name"]
    ordering = ["name"]


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ["label", "semester", "is_active", "created_at"]
    list_filter = ["semester", "is_active"]
    ordering = ["-label", "-semester"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Email-based user admin — no username field."""

    list_display = ["email", "first_name", "last_name", "role", "is_active", "is_staff"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Role & Status", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "first_name", "last_name"),
            },
        ),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only audit log admin."""

    list_display = ["timestamp", "user", "action", "content_type", "object_id"]
    list_filter = ["action", "content_type"]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request: admin) -> bool:
        return False

    def has_change_permission(self, request: admin, obj: AuditLog | None = None) -> bool:
        return False

    def has_delete_permission(self, request: admin, obj: AuditLog | None = None) -> bool:
        return False
