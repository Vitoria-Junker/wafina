from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("full_name", "message")


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "is_active")
    search_fields = ("question",)
    list_filter = ("is_active", )
