"""DRF serializers for academic structure models."""

from __future__ import annotations

from rest_framework import serializers

from apps.academic_structure.models import ClassSection, GradeLevel, Major, Subject


class GradeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevel
        fields = [
            "id",
            "name",
            "school",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GradeLevelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevel
        fields = ["name", "school"]


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = [
            "id",
            "name",
            "school",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MajorCreateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Major
        fields = ["name", "school", "is_active"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "school",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubjectCreateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Subject
        fields = ["name", "code", "school", "is_active"]


class ClassSectionSerializer(serializers.ModelSerializer):
    grade_level_name = serializers.CharField(source="grade_level.name", read_only=True)
    major_name = serializers.CharField(source="major.name", read_only=True, allow_null=True)
    academic_year_label = serializers.CharField(source="academic_year.label", read_only=True)
    homeroom_teacher_name = serializers.CharField(
        source="homeroom_teacher.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ClassSection
        fields = [
            "id",
            "name",
            "grade_level",
            "grade_level_name",
            "major",
            "major_name",
            "academic_year",
            "academic_year_label",
            "homeroom_teacher",
            "homeroom_teacher_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClassSectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSection
        fields = [
            "name",
            "grade_level",
            "major",
            "academic_year",
            "homeroom_teacher",
        ]

    def to_representation(self, instance: ClassSection) -> dict:
        return ClassSectionSerializer(instance=instance).data
