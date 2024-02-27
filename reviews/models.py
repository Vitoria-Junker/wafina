from accounts.models import User
from booking_requests.models import BookingSession
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Review(models.Model):
    source = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="source_review",
        null=True,
        blank=True
    )
    target = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="target_review",
        null=True,
        blank=True
    )
    session = models.ForeignKey(
        BookingSession,
        related_name='session_review',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    comments = models.TextField(
        null=True,
        blank=True
    )
    rating = models.PositiveIntegerField(
        validators=
        [
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )