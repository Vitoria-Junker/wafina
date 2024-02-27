from django.db import models
from booking_requests.models import BookingSession

# Create your models here.


class Transactions(models.Model):
    session = models.ForeignKey(
        BookingSession,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    transaction_date = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    currency = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    payment_id = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        try:
            return f"{self.session.total_price}$ transfer by {self.session.source.full_name} to " \
                   f"{self.session.target.full_name}"
        except:
            return f"{self.session.total_price}$ Transaction"

