from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(InAppNotification)
class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "notification_subject", "notification_message", "actionable",
                    "session_id", "type_of_action", "is_read", "is_active", "created_on")
    list_filter = ("is_read", "is_active")
    ordering = ("-created_on",)

