"""Manager classes used by mixins in `shared.models`."""

from __future__ import annotations

from django.db import models


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self) -> models.QuerySet:
        return super().get_queryset()

    def deleted(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=True)
