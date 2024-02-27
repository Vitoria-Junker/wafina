from django.db import models
from accounts.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.

class UserImage(models.Model):
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to="user_feed_images",
    )
    user = models.ForeignKey(
        User,
        related_name="feed",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    extra_text = models.TextField(
        null=True,
        blank=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.user.full_name}'s_{self.id} Image"


class UserLikesAndComment(models.Model):
    ACTIVITY_STATUS = (
        ('like', _('like')),
        ('comment', _('comment')),
    )
    image_obj = models.ForeignKey(
        UserImage,
        related_name="user_image",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    comment = models.TextField(
        null=True,
        blank=True
    )
    likes_extra_data = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )
    commented_by = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE,
        null=True,
        blank=True

    )
    type_of_action = models.CharField(
        choices=ACTIVITY_STATUS,
        null=True,
        blank=True,
        max_length=20
    )

    def __str__(self):
        return f"{self.type_of_action} on {self.image_obj.user.full_name}'s {self.image_obj.id} Image "



