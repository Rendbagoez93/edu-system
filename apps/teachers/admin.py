"""Django admin for teacher models."""

from __future__ import annotations

from django.contrib import admin

from apps.teachers.models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["name", "nuptk", "employment_status", "email", "school", "created_at"]
    list_filter = ["employment_status", "school"]
    search_fields = ["name", "nuptk", "email"]
    ordering = ["name"]
