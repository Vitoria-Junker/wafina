from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class ContactUs(models.Model):
    full_name = models.CharField(
        blank=True,
        null=True,
        max_length=120,
        help_text=_("Name of the User who submitted this request")
    )
    email = models.EmailField(
        null=True,
        blank=True,
        help_text=_("Email address of the User")
    )
    phone_number = PhoneNumberField(
        null=True,
        blank=True,
        help_text=_("Contact number of the User")
    )
    message = models.TextField(
        null=True,
        blank=True
    )
    created_on = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True
    )
    modified_on = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True
    )

    class Meta:
        verbose_name_plural = _(u"Contact-Us")

    def __str__(self):
        return f"{self.email} => {self.message}"


class Faq(models.Model):
    question = models.TextField(
        null=False,
        blank=False
    )
    answer = models.TextField(
        null=False,
        blank=False
    )
    is_active = models.BooleanField(
        default=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    modified_on = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = _(u"FAQs")

    def __str__(self):
        return self.question

