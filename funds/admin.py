from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Transactions)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    list_filter = ('session__source__full_name', 'session__target__full_name')
