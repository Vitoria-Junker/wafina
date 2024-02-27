from django.contrib.auth import authenticate

from .models import User, UserOtp, UserExpertise, ExpertiseModel, UserStripeVerification
from rest_framework import serializers, exceptions
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from helpers.serializer_fields import CustomEmailSerializerField, PhoneNumberField, GeometryPointFieldSerializerFields
from helpers import messages
import django.contrib.auth.password_validation as validators
from django.conf import settings
from django.utils import timezone
from reviews.models import Review
from statistics import mean


class LoginSerializer(serializers.Serializer):
    """
       serializer for login view
    """
    email = CustomEmailSerializerField(
        required=True,
        allow_null=False
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'inactive_account': messages.INACTIVE_ACCOUNT_ERROR,
        'invalid_credentials': messages.INVALID_CREDENTIALS_ERROR,
        'blocked_account': messages.BLOCKED_ACCOUNT,
        'invalid_account': messages.NON_REGISTERED_ACCOUNT
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        try:
            user = User.objects.get_user_by_email(attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['invalid_account']
            )
        if user and not user.is_user_active():
            raise serializers.ValidationError(
                self.error_messages['inactive_account']
            )
        self.user = authenticate(username=attrs.get(User.USERNAME_FIELD),
                                 password=attrs.get('password'))
        if not self.user:
            raise serializers.ValidationError(
                self.error_messages['invalid_credentials'])
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    """
    serializer for registering new user
    """
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        validators=[validators.validate_password]
    )
    email = CustomEmailSerializerField()
    username = serializers.CharField(
        required=True,
        allow_null=False
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    account_type = serializers.ChoiceField(
        choices=User.ACCOUNT_TYPE,
        required=True,
        allow_null=False
    )

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('Password doesnt matches')
        return attrs

    def validate_email(self, email):
        if User.objects.filter(email=email):
            raise serializers.ValidationError("User with this email already exists")
        return email

    def validate_username(self, username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError("User with this username already exists")
        return username

    class Meta:
        model = User
        fields = ('account_type', 'email', 'username', 'password', 'confirm_password')


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=255)
    email = CustomEmailSerializerField()

    def validate(self, data):
        otp = data['otp']
        try:
            user = User.objects.get(email=data['email'])
            self.user_otp = UserOtp.objects.get_user_otp_by_otp_and_user(
                otp, user)
        except UserOtp.DoesNotExist:
            raise serializers.ValidationError(messages.INVALID_OTP)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                messages.UNREGISTERED_EMAIL)
        created = self.user_otp.created_on
        current_datetime = timezone.now()
        last = (current_datetime - created).seconds
        if last > settings.SESSION_IDLE_TIMEOUT:
            raise exceptions.ValidationError(messages.INVALID_OTP)
        return data


class ResendOtpSerilizer(serializers.Serializer):
    email = CustomEmailSerializerField(label="User Email")

    def validate_email(self, value):
        try:
            self.user = User.objects.get_user_by_email(value)
        except User.DoesNotExist:
            raise serializers.ValidationError(messages.UNREGISTERED_EMAIL)
        return value


class PasswordResetSerializer(serializers.Serializer):
    """ verify otp and change password """
    id = serializers.IntegerField(label="User Id", min_value=0)
    otp = serializers.CharField(max_length=5)
    new_password = serializers.CharField(max_length=255,
                                         min_length=6,
                                         validators=[
                                             validators.validate_password])

    def validate_otp(self, value):
        user = self.context['user']
        try:
            self.user_otp = UserOtp.objects.get_user_otp_by_otp_and_user(
                value, user)
        except UserOtp.DoesNotExist:
            raise serializers.ValidationError(messages.INVALID_OTP)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    postcode = serializers.CharField(
        required=True,
        allow_null=False
    )
    city = serializers.CharField(
        required=True,
        allow_null=False
    )
    date_of_birth = serializers.DateField(
        required=True,
        allow_null=True
    )
    country = CountryField(
        allow_null=False,
        required=True,
        allow_blank=False
    )
    full_name = serializers.CharField(
        allow_null=False,
        required=True
    )
    gender = serializers.ChoiceField(
        choices=User.GENDER_CHOICES,
        allow_null=False,
        required=True
    )
    phone_number = PhoneNumberField(
        allow_null=False,
        required=True
    )
    location_coordinates = GeometryPointFieldSerializerFields(
        allow_null=False,
        required=True
    )
    address = serializers.CharField(
        required=True,
        allow_null=False
    )

    def validate_phone_number(self, obj):
        if User.objects.filter(phone_number=obj).exists():
            raise serializers.ValidationError("User with this phone number already exists")
        else:
            return obj

    def validate_profile_picture(self, obj):
        file_size = obj.size
        megabyte_limit = 15.0
        if file_size > megabyte_limit * 1024 * 1024:
            raise serializers.ValidationError(f"Max size of profile picture you can upload is {megabyte_limit} MB")
        else:
            return obj

    class Meta:
        model = User
        fields = ('user_id', 'full_name', 'city', 'postcode', 'country', 'phone_number', 'gender',
                  'profile_picture', 'date_of_birth', 'location_coordinates', 'address', 'off_day'
                  )
        read_only_fields = ('user_id',)


class UserInformationGetSerializer(CountryFieldMixin, serializers.ModelSerializer):
    phone_number = PhoneNumberField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    location_coordinates = GeometryPointFieldSerializerFields(
        allow_null=True,
        required=False
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'city', 'postcode', 'country', 'phone_number',
                  'gender', 'profile_picture', 'date_of_birth', 'location_coordinates', 'address',
                  'account_complete', 'expertise_added', 'verification_skipped', 'personal_info_added',
                  'needs_action', 'off_day'
                  )


class UserUpdateSerializer(CountryFieldMixin, serializers.ModelSerializer):
    """
        User serializer for user ModelViewSet
    """
    email = CustomEmailSerializerField()
    phone_number = PhoneNumberField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    username = serializers.CharField(
        min_length=1,
        max_length=30,
        required=True
    )
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES,
                                     allow_null=True,
                                     required=False
                                     )
    location_coordinates = GeometryPointFieldSerializerFields(
        allow_null=True,
        required=False
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'city', 'postcode', 'country', 'phone_number',
                  'gender', 'profile_picture', 'date_of_birth', 'address', 'location_coordinates', 'phone_number',
                  'off_day'
                  )

    def validate_username(self, username):
        user_id = self.context.get('user_id')
        if User.objects.filter(username=username).exclude(id=user_id):
            raise serializers.ValidationError(
                messages.USERNAME_ALREADY_EXISTS
            )
        return username

    def validate_email(self, email):
        user_id = self.context.get('user_id')
        if User.objects.filter(email=email).exclude(id=user_id):
            raise serializers.ValidationError(
                messages.EMAIL_ALREADY_EXITS
            )
        return email

    def validate_phone_number(self, phone_number):
        user_id = self.context.get('user_id')
        if User.objects.filter(phone_number=phone_number).exclude(id=user_id):
            raise serializers.ValidationError("User with this phone number already exists")
        else:
            return phone_number


class ExpertiseGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpertiseModel
        fields = ('id', 'expertise_name')


class SelectExpertiseSerializer(serializers.Serializer):
    expertise_data = serializers.JSONField(
        default=list,
        allow_null=False
    )

    class Meta:
        fields = ('expertise_data',)


class UserExpertiseGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserExpertise
        fields = ('id', 'user_id', 'expertise_id', 'experience_in_years', 'cost_in_usd',
                  'user_defined_expertise', 'is_active')


class UserSearchSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    location_coordinates = GeometryPointFieldSerializerFields(
        allow_null=True,
        required=False
    )
    ratings = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        review_dict = dict()
        ratings = []
        review_obj = Review.objects.filter(target_id=obj.id)
        review_dict["no_of_reviews"] = review_obj.count()
        for review in review_obj:
            ratings.append(int(review.rating))
        if ratings:
            mean_rating = mean(ratings)
            review_dict["ratings"] = round(mean_rating)

        else:
            review_dict["ratings"] = 0
        return review_dict

    def get_services(self, obj):
        service_list = list()
        if obj.user_expertise.all():
            for qs in obj.user_expertise.all():
                if qs.expertise:
                    service_list.append(qs.expertise.expertise_name)
            return service_list
        else:
            return service_list

    class Meta:
        model = User
        fields = ('id', 'full_name', 'profile_picture', 'location_coordinates', 'city', 'services',
                  'ratings', 'off_day')


class StripeVerificationSerializer(serializers.ModelSerializer):
    document_front_picture = serializers.FileField(
        required=True,
        allow_null=False
    )
    document_back_picture = serializers.FileField(
        required=True,
        allow_null=False
    )
    bank_account_number = serializers.CharField(
        required=True,
        allow_null=False
    )
    bank_sort_code = serializers.CharField(
        required=True,
        allow_null=False
    )
    certificate = serializers.FileField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = UserStripeVerification
        exclude = ('errors',)


class ChangePasswordSerializer(serializers.Serializer):
    """ change password serializer """
    new_password = serializers.CharField(write_only=True,
                                         max_length=255,
                                         min_length=6,
                                         validators=[
                                             validators.validate_password]
                                         # min_length=8,
                                         # validators=[valid.validate_password_field]
                                         )
    old_password = serializers.CharField(write_only=True)

    def validate_old_password(self, attrs):
        if self.context['request'].user.check_password(attrs):
            return attrs
        else:
            raise serializers.ValidationError("Please enter correct password")

    def validate_new_password(self, data):

        if self.context['request'].user.check_password(data):
            raise exceptions.ValidationError("New password cannot be same as old password")
        if len(data) == 0:
            raise exceptions.ValidationError("New password should not be empty")
        return data


class UserDataSerializer(serializers.ModelSerializer):
    service_data = serializers.SerializerMethodField()
    location_coordinates = GeometryPointFieldSerializerFields(
        allow_null=True,
        required=False
    )
    ratings = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        review_dict = dict()
        ratings = []
        review_obj = Review.objects.filter(target_id=obj.id)
        review_dict["no_of_reviews"] = review_obj.count()
        for review in review_obj:
            ratings.append(int(review.rating))
        if ratings:
            mean_rating = mean(ratings)
            review_dict["ratings"] = round(mean_rating)

        else:
            review_dict["ratings"] = 0
        return review_dict

    def get_service_data(self, obj):
        service_list = list()
        if obj.user_expertise.all():
            for qs in obj.user_expertise.all():
                try:
                    if qs.user_defined_expertise:
                        expertise_name = qs.user_defined_expertise
                    else:
                        expertise_name = qs.expertise.expertise_name
                except:
                    expertise_name = None
                service_list.append({
                    "id": qs.id,
                    "expertise_name": expertise_name,
                    "experience_in_years": qs.experience_in_years,
                    "cost_in_usd": qs.cost_in_usd,
                })
            return service_list
        else:
            return service_list

    class Meta:
        model = User
        fields = ('id', 'full_name', 'profile_picture', 'location_coordinates', 'address', 'city',
                  'service_data', 'ratings', 'off_day')
