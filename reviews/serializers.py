from rest_framework import serializers
from reviews.models import Review
from booking_requests.models import BookingSession


class ReviewPostSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    rating = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    comments = serializers.CharField(
        required=False,
        allow_null=True
    )

    def validate_session_id(self, session_id):
        if not BookingSession.objects.filter(id=session_id):
            raise serializers.ValidationError("Given Session does not exist")
        return session_id

    class Meta:
        model = Review
        fields = ('session_id', 'rating', 'comments')


class ReviewGetSerializer(serializers.ModelSerializer):
    source_name = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    review_date = serializers.SerializerMethodField()

    def get_review_date(self, obj):
        return obj.created_on.date()

    def get_services(self, obj):
        return obj.session.extra_data.get("requested_services_data")

    def get_source_name(self, obj):
        source_info = dict()
        source_info["full_name"] = obj.source.full_name
        if obj.source.profile_picture:
            source_info["profile_picture"] = obj.source.profile_picture.url
        else:
            source_info["profile_picture"] = None
        return source_info

    def get_target_name(self, obj):
        return obj.target.full_name

    class Meta:
        model = Review
        fields = ('source_name', 'target_name', 'rating', 'comments', "services", "review_date")


