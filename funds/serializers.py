from rest_framework import exceptions, serializers, response, status
from .models import Transactions
from booking_requests.models import BookingSession


class TransactionSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    currency = serializers.CharField(
        required=True,
        allow_null=False,
        max_length=3
    )

    def validate_session_id(self, session_id):
        if not BookingSession.objects.filter(id=session_id):
            raise serializers.ValidationError("Given Session does not exist")
        if BookingSession.objects.filter(status='paid', id=session_id):
            raise serializers.ValidationError('You have already paid for this proposal')
        return session_id

    class Meta:
        model = Transactions
        fields = ('id', 'session_id', 'currency')


class WalletSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_user_id(self, obj):
        return obj.session.target.id

    def get_services(self, obj):
        return obj.session.extra_data.get("requested_services_data")

    def get_source_name(self, obj):
        return obj.session.source.full_name

    def get_payment_date(self, obj):
        return obj.transaction_date.date()

    def get_cost(self, obj):
        return obj.session.total_price

    class Meta:
        model = Transactions
        fields = ('user_id', 'services', 'source_name', 'payment_date', 'cost')
