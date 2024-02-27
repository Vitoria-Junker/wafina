import re
from .models import ContactUs, Faq
from helpers.serializer_fields import PhoneNumberField, CustomEmailSerializerField
from rest_framework import serializers


class ContactUsSerializer(serializers.ModelSerializer):
    email = CustomEmailSerializerField(
        required=True, allow_null=False
    )
    phone_number = PhoneNumberField(
        required=True, allow_null=False
    )
    full_name = serializers.CharField(
        allow_null=False,
        allow_blank=False,
        required=True
    )
    message = serializers.CharField(
        allow_null=False,
        allow_blank=False,
        required=True
    )

    def validate_full_name(self, full_name):
        try:
            assert not re.search("\d", full_name)
        except AssertionError:
            raise serializers.ValidationError("Name cannot contain numbers")
        return full_name

    class Meta:
        model = ContactUs
        fields = ('full_name', 'email', 'phone_number', 'message',)


class FaqSerializer(serializers.ModelSerializer):

    class Meta:
        model = Faq
        fields = ('id', 'question', 'answer')

