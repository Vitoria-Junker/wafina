import random
from django.contrib.gis.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework_jwt.settings import api_settings
from django_countries.fields import CountryField
from accounts.managers import UserManager, UserOtpManager
from helpers.validators import validate_file


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPE = (
        ('professional', _('professional')),
        ('customer', _('customer')),
    )

    GENDER_CHOICES = (
        ('male', _('male')),
        ('female', _('female')),
        ('other', _('other')),

    )
    full_name = models.CharField(
        null=True,
        blank=True,
        max_length=80
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )
    username = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    account_type = models.CharField(
        choices=ACCOUNT_TYPE,
        null=True,
        blank=True,
        max_length=30
    )
    phone_number = PhoneNumberField(
        unique=True,
        blank=True,
        null=True
    )
    postcode = models.TextField(
        null=True,
        blank=True
    )
    address = models.TextField(
        null=True,
        blank=True
    )
    city = models.CharField(
        null=True,
        blank=True,
        max_length=80
    )
    location_coordinates = models.PointField(
        null=True,
        blank=True,
        srid=4326
    )
    profile_picture = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=False
    )
    account_complete = models.BooleanField(
        default=False
    )
    is_staff = models.BooleanField(
        default=False
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
    country = CountryField(
        blank_label='(select country)',
        multiple=False,
        null=True,
        blank=True
    )
    stripe_id = models.TextField(
        null=True,
        blank=True
    )
    expertise_added = models.BooleanField(
        default=False
    )
    verification_skipped = models.BooleanField(
        default=False
    )
    personal_info_added = models.BooleanField(
        default=False
    )
    needs_action = models.BooleanField(
        default=None,
        null=True
    )
    balance = models.FloatField(
        default=0,
        null=True,
        blank=True
    )
    off_day = models.CharField(
        null=True,
        blank=True,
        max_length=60
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.full_name}  => {self.account_type}"

    def is_user_active(self):
        """ check check user is active """
        return self.is_active

    def get_jwt_token_for_user(self):
        """ get jwt token for the user """
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(self)
        token = jwt_encode_handler(payload)
        return token

    def generate_otp(self, email, contact_number=None):

        otp_code = random.randint(11111, 99999)
        data = {
            'user': self,
            'otp': otp_code,
        }
        try:
            user_otp = UserOtp.objects.get_otp_of_user(self)
            user_otp.delete()
            user_otp = UserOtp.objects.create(**data)
        except UserOtp.DoesNotExist:
            user_otp = UserOtp.objects.create(**data)

        return user_otp.get_otp()


class UserOtp(models.Model):
    """ model for user otp"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    otp = models.CharField(
        max_length=5
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True)

    objects = UserOtpManager()

    def __str__(self):
        return "{0}-{1}".format(self.user.email, self.otp)

    def get_user(self):
        return self.user

    def get_otp(self):
        return self.otp

    def get_created_time(self):
        return self.created_on


class ExpertiseModel(models.Model):
    expertise_name = models.CharField(
        max_length=80,
    )
    is_active = models.BooleanField(
        default=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.expertise_name

    class Meta:
        verbose_name_plural = _(u"Expertise Name(s)")


class UserExpertise(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_expertise',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    expertise = models.ForeignKey(
        ExpertiseModel,
        related_name='admin_expertise',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    experience_in_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
    cost_in_usd = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    user_defined_expertise = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text='Expertise defined by User'
    )
    is_active = models.BooleanField(
        default=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = _(u"User(s) Expertise Details")


class UserStripeVerification(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    document_front_picture = models.FileField(
        null=True,
        blank=True,
        upload_to='stripe_docs/',
        validators=[validate_file]
    )
    document_back_picture = models.FileField(
        null=True,
        blank=True,
        upload_to='stripe_docs/',
        validators=[validate_file]
    )
    certificate = models.FileField(
        null=True,
        blank=True,
        upload_to='stripe_docs/',
        validators=[validate_file]
    )
    bank_account_number = models.CharField(
        null=True,
        blank=True,
        max_length=60
    )
    bank_sort_code = models.CharField(
        null=True,
        blank=True,
        max_length=20
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    errors = models.JSONField(
        default=list,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = _(u"User(s) Address Proof and Certificates")

