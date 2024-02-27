from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, response, status, views, permissions
from .models import InAppNotification
from .serializers import InAppNotificationSerializer, NotificationDeleteSerializer


class NotificationView(generics.GenericAPIView):
    """
        endpoint to create/list/delete notifications
    """
    http_method_names = ["get", "post"]
    serializer_class = InAppNotificationSerializer
    model = InAppNotification
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        if request.query_params.get('unread_count', None):
            data = dict()
            data['count'] = self.model.objects.filter(
                user_id=user_id,
                is_active=True,
                is_read=False
            ).count()
            data['latest_ids'] = list(self.model.objects.filter(
                user_id=user_id,
                is_active=True,
                is_read=False
            ).values_list('id', flat=True))
            return response.Response(
                data,
                status=status.HTTP_200_OK
            )
        qs = InAppNotification.objects.filter(
            user_id=user_id,
            is_active=True
        ).order_by('-created_on')
        qs.update(is_read=True)

        serializer = self.serializer_class(qs, many=True)
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            InAppNotification.objects.create(**serializer.validated_data)
            return response.Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED
            )


class NotificationBulkDelete(views.APIView):
    """
        endpoint to delete bulk notifications
    """
    http_method_names = ["post"]
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationDeleteSerializer

    @swagger_auto_schema(
        request_body=NotificationDeleteSerializer,
        operation_id="Delete Notifications")
    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.data.get("select_all") is True:
            InAppNotification.objects.filter(
                user_id=user_id).update(is_active=False)
        else:
            InAppNotification.objects.filter(id=serializer.data.get("notification_id"),
                                             user_id=user_id).update(is_active=False)

        return response.Response(
            status=status.HTTP_204_NO_CONTENT
        )
