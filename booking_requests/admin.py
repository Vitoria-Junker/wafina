from django.contrib import admin
from .models import *
from django.utils.translation import ugettext, ugettext_lazy as _


# Register your models here.


@admin.register(BookingSession)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'target', 'status', 'requested_date', 'start_timestamp', 'end_timestamp',
                    'total_price')
    list_filter = ('status', 'source__full_name', 'target__full_name')
    fieldsets = (
        (None, {'fields': ('source', 'target')}),
        (_('Session Details'), {'fields': ('requested_date', 'start_timestamp', 'end_timestamp', 'total_price',
                                           'status', 'requested_services')}),
    )
    readonly_fields = ('source', 'target', 'status', 'requested_date', 'start_timestamp', 'end_timestamp',
                       'total_price'
                       )
