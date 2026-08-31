"""Django admin for academic structure models."""

from __future__ import annotations

from django.contrib import admin

from apps.academic_structure.models import ClassSection, GradeLevel, Major, Subject


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "created_at"]
    list_filter = ["school"]
    ordering = ["name"]


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    ordering = ["name"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name", "code"]
    ordering = ["name"]


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ["name", "grade_level", "major", "academic_year", "homeroom_teacher", "created_at"]
    list_filter = ["grade_level", "academic_year", "major"]
    search_fields = ["name"]
    ordering = ["name"]
