from statistics import mean

from django.db.models import Q
from rest_framework import serializers

from reviews.models import Review
from .models import BookingSession


class BookingRequestSerializer(serializers.ModelSerializer):
    target_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    requested_date = serializers.DateField(
        required=True,
        input_formats=["%Y-%m-%d"]
    )
    start_timestamp = serializers.DateTimeField(
        input_formats=["%Y-%m-%d %H:%M:%S"],
        required=True
    )
    requested_services = serializers.JSONField(
        required=True,
        allow_null=False
    )
    
    class Meta:
        model = BookingSession
        fields = ('target_id', 'requested_date', 'start_timestamp',
                  'requested_services')


class SessionDetailsSerializer(serializers.ModelSerializer):
    customer_info = serializers.SerializerMethodField()
    target_info = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()
    session_start_time = serializers.SerializerMethodField()
    session_end_time = serializers.SerializerMethodField()
    requested_services = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    is_action_taken = serializers.SerializerMethodField()
    comparison_date = serializers.SerializerMethodField()

    def get_comparison_date(self, obj):
        return obj.requested_date

    def get_status(self, obj):
        if obj.status == "accepted":
            value = "not_paid"
        elif obj.status == "paid":
            value = "paid"
        elif obj.status == "completed":
            value = "completed"
        else:
            value = None
        return value

    def get_is_action_taken(self, obj):
        if obj.status == "accepted" or obj.status == "rejected":
            return True
        else:
            return False

    def get_customer_info(self, obj):
        customer_info = dict()
        customer_name = obj.source.full_name
        if obj.source.profile_picture:
            customer_profile_picture = obj.source.profile_picture.url
        else:
            customer_profile_picture = None
        customer_info["user_id"] = obj.source.id
        customer_info["name"] = customer_name
        customer_info["profile_picture"] = customer_profile_picture
        customer_info["city"] = obj.source.city
        customer_info["address"] = obj.source.address
        return customer_info

    def get_target_info(self, obj):
        target_info = dict()
        target_name = obj.target.full_name
        if obj.target.profile_picture:
            target_profile_picture = obj.target.profile_picture.url
        else:
            target_profile_picture = None
        target_info["user_id"] = obj.target.id
        target_info["name"] = target_name
        target_info["profile_picture"] = target_profile_picture
        target_info["city"] = obj.target.city
        target_info["address"] = obj.target.address
        review_dict = dict()
        ratings = []
        review_obj = Review.objects.filter(target_id=obj.target.id)
        review_dict["no_of_reviews"] = review_obj.count()
        for review in review_obj:
            ratings.append(int(review.rating))
        if ratings:
            mean_rating = mean(ratings)
            review_dict["ratings"] = round(mean_rating)

        else:
            review_dict["ratings"] = 0
        target_info["review_info"] = review_dict
        return target_info

    def get_session_date(self, obj):
        return obj.extra_data.get("custom_date")

    def get_session_start_time(self, obj):
        return obj.extra_data.get("start_time")

    def get_session_end_time(self, obj):
        return obj.extra_data.get("end_time")

    def get_requested_services(self, obj):
        return obj.extra_data.get("requested_services_data")

    class Meta:
        model = BookingSession
        fields = ('id', 'customer_info', 'target_info', 'session_date',
                  'session_start_time', 'session_end_time', 'requested_services', 'total_price', 'status',
                  'is_action_taken', 'comparison_date'
                  )


class SessionActionSerializer(serializers.Serializer):
    action_choice_field = [
        ("accept", "Accept"),
        ("reject", "Reject")
    ]
    session_id = serializers.IntegerField(required=True, allow_null=False)
    action = serializers.ChoiceField(
        choices=action_choice_field,
    )
    no_of_hours = serializers.IntegerField(allow_null=True, required=False)

    def validate_session_id(self, obj):
        if not BookingSession.objects.filter(id=obj):
            raise serializers.ValidationError('Given Session doesnot exists')
        if BookingSession.objects.filter(Q(status='accepted') | Q(status='rejected'),
                                         id=obj):
            raise serializers.ValidationError('You have already taken action on this '
                                              'Booking Session')
        return obj
