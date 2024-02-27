from django.db import models

# Create your models here.


class InAppNotification(models.Model):
    user_id = models.PositiveIntegerField(
        null=True, blank=True
    )
    notification_subject = models.TextField(
        null=True,
        blank=True
    )
    notification_message = models.TextField(
        null=True,
        blank=True
    )
    actionable = models.BooleanField(
        default=False
    )
    session_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    type_of_action = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )
    review_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    is_read = models.BooleanField(
        default=False
    )
    is_active = models.BooleanField(
        default=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )
