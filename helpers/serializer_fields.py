import json
from rest_framework import serializers, exceptions
from phonenumber_field.phonenumber import to_python
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework_gis.serializers import GeometryField


class CustomEmailSerializerField(serializers.EmailField):

    def to_internal_value(self, value):
        value = super(CustomEmailSerializerField,
                      self).to_internal_value(value)
        return value.lower()


class PhoneNumberField(serializers.CharField):
    """
    A custom serialize field to represent data of `phone_number` field
    like
    {"phone_number": {"number": "1234567890", "country_code": "+91"}}
    """
    default_error_messages = {
        'invalid': 'Enter a valid phone number.',
    }

    def to_internal_value(self, data):
        phone_number = to_python(data)
        if phone_number and not phone_number.is_valid():
            raise exceptions.ValidationError(self.error_messages['invalid'])

        return phone_number

    def to_representation(self, value):
        """ break the country code and phone number """
        if value:
            return {
                'country_code': "+" + str(value.country_code),
                'number': str(value.national_number)
            }


class GeometryPointFieldSerializerFields(GeometryField):

    def to_internal_value(self, value):
        try:
            value = value.split(",")
        except:
            raise ValidationError(
                _("Enter the co-ordinates in (latitude, longitude). Ex-12,13")
            )
        try:
            latitude = float(value[0])
        except (ValueError, IndexError):
            raise ValidationError(
                _("Enter the co-ordinates in (latitude, longitude). Ex-12,13")
            )
        try:
            longitude = float(value[1])
        except (ValueError, IndexError):
            raise ValidationError(
                _("Enter the co-ordinates in (latitude, longitude). Ex-12,13")
            )
        value = {
            "type": "Point",
            "coordinates": [latitude, longitude]
        }
        value = json.dumps(value)
        try:
            return GEOSGeometry(value)
        except (ValueError, GEOSException, TypeError):
            raise ValidationError(
                _('Invalid format: string or unicode input unrecognized as GeoJSON, WKT EWKT or HEXEWKB.'))

    def to_representation(self, value):
        """ """
        value = super(
            GeometryPointFieldSerializerFields, self).to_representation(value)
        # change to compatible with google map
        data = {
            "type": "Point",
            "coordinates": [
                value['coordinates'][0], value['coordinates'][1]
            ]
        }
        return data
