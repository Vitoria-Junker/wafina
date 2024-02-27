from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "message")
    list_filter = ("session",)
    search_fields = ("message",)
    ordering = ("-created",)