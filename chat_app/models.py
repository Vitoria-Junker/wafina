from django.db import models
from booking_requests.models import BookingSession
from accounts.models import User


class Conversation(models.Model):
    session = models.ForeignKey(
        BookingSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="session_chat"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="message_author"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="message_receiver"
    )
    message = models.TextField(
        null=False,
        blank=False
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    seen = models.BooleanField(
        default=False
    )


class Interactions(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversation_author"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversation_receiver"
    )
    session = models.ForeignKey(
        BookingSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="session_interaction"
    )
    all_users_list = models.JSONField(
        default=list,
        null=True,
        blank=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

