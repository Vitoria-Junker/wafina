from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "target", "session", "comments", "rating", "created_on")
    list_filter = ("target__full_name", "rating")
    ordering = ("-created_on",)
