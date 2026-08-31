"""DRF serializers for student models."""

from __future__ import annotations

from rest_framework import serializers

from apps.students.models import Enrollment, ImportBatch, Student


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "nisn",
            "nis",
            "name",
            "date_of_birth",
            "gender",
            "phone",
            "email",
            "guardian_name",
            "guardian_contact",
            "guardian_relation",
            "phone_same_as_guardian",
            "address",
            "school",
            "user_account",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_account"]


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "nisn",
            "nis",
            "name",
            "date_of_birth",
            "gender",
            "phone",
            "email",
            "guardian_name",
            "guardian_contact",
            "guardian_relation",
            "phone_same_as_guardian",
            "address",
            "school",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "class_section",
            "academic_year",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ImportBatchSerializer(serializers.ModelSerializer):
    imported_by_email = serializers.CharField(source="imported_by.email", read_only=True)

    class Meta:
        model = ImportBatch
        fields = [
            "id",
            "file_name",
            "row_count",
            "error_count",
            "errors",
            "status",
            "imported_by",
            "imported_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "error_count",
            "errors",
            "status",
            "created_at",
            "updated_at",
        ]
