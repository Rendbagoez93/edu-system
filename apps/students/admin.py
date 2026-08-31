"""Django admin for student models."""

from __future__ import annotations

from django.contrib import admin

from apps.students.models import Enrollment, ImportBatch, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["name", "nisn", "nis", "gender", "school", "date_of_birth", "created_at"]
    list_filter = ["gender", "school"]
    search_fields = ["name", "nisn", "nis"]
    ordering = ["name"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "class_section", "academic_year", "status", "created_at"]
    list_filter = ["status", "academic_year"]
    search_fields = ["student__name", "class_section__name"]


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ["file_name", "row_count", "error_count", "status", "imported_by", "created_at"]
    list_filter = ["status"]
    ordering = ["-created_at"]
