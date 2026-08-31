"""DRF serializers for teacher models."""

from __future__ import annotations

from rest_framework import serializers

from apps.teachers.models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            "id",
            "nuptk",
            "name",
            "employment_status",
            "contact_phone",
            "address",
            "email",
            "school",
            "user_account",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_account"]


class TeacherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            "nuptk",
            "name",
            "employment_status",
            "contact_phone",
            "address",
            "email",
            "school",
        ]
