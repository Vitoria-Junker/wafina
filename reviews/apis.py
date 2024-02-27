from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, permissions, status, response, filters, mixins, viewsets
from helpers.notification_method import create_notification
from reviews.models import Review
from reviews.serializers import ReviewPostSerializer, ReviewGetSerializer
from booking_requests.models import BookingSession
from helpers.tasks import SendOTPNotificationOnEmail


class ReviewAPI(generics.ListCreateAPIView,
                mixins.RetrieveModelMixin,
                viewsets.ViewSet
                ):
    model = Review
    permission_classes = (permissions.IsAuthenticated,)
    ordering = ('-created_on',)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('rating',)
    task = SendOTPNotificationOnEmail()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReviewGetSerializer
        else:
            return ReviewPostSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id", None)
        if user_id:
            queryset = self.model.objects.filter(target_id=user_id)
        else:
            queryset = self.model.objects.filter(target_id=self.request.user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            session = BookingSession.objects.filter(id=serializer.validated_data.pop('session_id')).first()
            review_obj = Review.objects.create(**serializer.validated_data)
            review_obj.session = session
            review_obj.source = session.source
            review_obj.target = session.target
            review_obj.save()
            name_list = list()
            for obj in session.extra_data.get("requested_services_data"):
                name_list.append(obj['service_name'])
            notification_data = {
                "user_id": session.target.id,
                "notification_subject": f'New Review by {session.source.full_name}',
                "notification_message": f"Review for {','.join(name_list)} Session."
                                        f"Please click here to check.",
                "session_id": session.id,
                "actionable": True,
                "type_of_action": "review",
                "review_id": review_obj.id
            }
            domain_name = get_current_site(request)
            create_notification(notification_data)
            ctx = {
                "user_email": session.target.email,
                "source_name": session.source.full_name,
                "target_name": session.target.full_name,
                "current_site": domain_name,
                'subject_template_name': 'New Review on your Profile',
                'html_body_template_name': 'review.html',
                'text_template': 'review.txt',
                'services': ','.join(name_list)
            }
            self.task.run(**ctx)
            session.status = 'completed'
            session.save()
            return response.Response({"msg": "Review successfully submitted"}, status=status.HTTP_201_CREATED)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)