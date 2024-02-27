from rest_framework import serializers
from notifications.models import InAppNotification
from booking_requests.models import BookingSession


class InAppNotificationSerializer(serializers.ModelSerializer):
    """
        serializer for notification model
    """
    user_id = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        required=False
    )
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        try:
            if obj.session_id:
                print(f"Session Id is {obj.session_id}")
                session_obj = BookingSession.objects.filter(id=obj.session_id).first()
                return session_obj.status
            else:
                return None
        except:
            return None

    class Meta:
        model = InAppNotification
        fields = ('id', 'user_id', 'notification_subject', 'notification_message', 'actionable',
                  'session_id', 'type_of_action', 'review_id', 'is_read', 'is_active', 'status', 'created_on')


class NotificationDeleteSerializer(serializers.Serializer):
    select_all = serializers.BooleanField(
        default=False
    )
    notification_id = serializers.IntegerField(
        allow_null=True,
        required=False
    )

    class Meta:
        fields = ("select_all", "notification_id",)
