from django.db import models
from accounts.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class BookingSession(models.Model):
    PROPOSAL_STATUS = (
        ('sent', _('sent')),
        ('accepted', _('accepted')),
        ('rejected', _('rejected')),
        ('completed', _('completed')),
        ('paid', _('paid'))
    )

    source = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="request_by",
        null=True,
        blank=True
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="request_to",
        null=True,
        blank=True
    )
    requested_date = models.DateField(
        blank=True,
        null=True
    )
    start_timestamp = models.DateTimeField(
        null=True,
        blank=True
    )
    end_timestamp = models.DateTimeField(
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=PROPOSAL_STATUS,
        null=True,
        blank=True
    )
    requested_services = models.JSONField(
        null=True,
        blank=True,
        default=list
    )
    extra_data = models.JSONField(
        null=True,
        blank=True,
        default=dict
    )
    total_price = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    reviewed = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name_plural = _(u"Booking Session Requests")




