"""DRF serializers for core models."""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.core.models import AcademicYear, AuditLog, School, User


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "id",
            "npsn",
            "nss",
            "name",
            "address",
            "level",
            "kepala_sekolah",
            "phone",
            "email",
            "logo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = [
            "id",
            "label",
            "semester",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs: dict) -> dict:
        label = attrs.get("label") or (self.instance.label if self.instance else None)
        semester = attrs.get("semester") or (self.instance.semester if self.instance else None)
        if label and semester:
            exists = AcademicYear.objects.filter(label=label, semester=semester)
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise serializers.ValidationError(
                    {"semester": "An academic year with this label and semester already exists."}
                )
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "teacher",
            "date_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "date_joined",
            "created_at",
            "updated_at",
            "teacher",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "role"]

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AuditLogSerializer(serializers.ModelSerializer):
    content_type = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "timestamp",
            "user",
            "action",
            "content_type",
            "object_id",
            "changes",
        ]
        read_only_fields = fields
