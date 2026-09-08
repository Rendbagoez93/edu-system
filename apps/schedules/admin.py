from django.contrib import admin

from apps.schedules.models import TimeSlot


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["day", "period", "display_order"]
    list_filter = ["day"]
    ordering = ["day", "period"]
