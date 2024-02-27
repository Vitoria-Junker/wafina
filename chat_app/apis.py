from datetime import datetime
import pytz
from rest_framework import generics, response, permissions, status, views, exceptions
from .models import Conversation, Interactions
from .serializers import ConversationSerializer, ConversationListSerializer, InteractionSerializer
from booking_requests.models import BookingSession

from rest_framework.pagination import PageNumberPagination


class RestAPIPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100


class UnseenMessageCount(views.APIView):
    model = Conversation
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        qs = Conversation.objects.filter(seen=False, receiver_id=self.request.user.id).count()
        resp_dict = dict()
        resp_dict["count"] = qs
        return response.Response(
            resp_dict,
            status=status.HTTP_200_OK
        )


class ConversationAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Conversation
    pagination_class = RestAPIPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConversationListSerializer
        else:
            return ConversationSerializer

    def get_queryset(self):
        session_id = self.request.query_params.get("session_id")
        if session_id:
            qs = self.model.objects.filter(session_id=session_id)
            unseen_qs = qs.filter(receiver_id=self.request.user.id).order_by('-created')
            unseen_qs.update(seen=True)
            return qs

        else:
            raise exceptions.ValidationError(
                "session_id is required in query params"
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            session_id = serializer.validated_data.pop("session_id")
            session = BookingSession.objects.filter(id=session_id).first()
            interaction = Interactions.objects.filter(session_id=session_id)
            sender = self.request.user
            if sender.id != session.source.id:
                receiver = session.source
            else:
                receiver = session.target
            obj = self.model.objects.create(**serializer.validated_data)
            obj.session = session
            obj.sender = sender
            obj.receiver = receiver
            obj.save()
            if not interaction:
                user_list = list()
                user_list.append(sender.id)
                user_list.append(receiver.id)
                Interactions.objects.create(
                    session=session,
                    sender=sender,
                    receiver=receiver,
                    all_users_list=user_list
                )
            resp_dict = dict()
            resp_dict[sender.id] = {
                "full_name": sender.full_name,
                "message": obj.message
            }
            return response.Response(
                resp_dict,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                serializer.errors
            )


class InteractionsAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InteractionSerializer

    def get_queryset(self):
        qs = Interactions.objects.filter(all_users_list__contains=self.request.user.id).order_by('-created_on')
        return qs


class UnseenConversations(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Conversation

    def get(self, request, *args, **kwargs):
        last = self.request.GET.get('last')
        if last:
            last = pytz.utc.localize(datetime.utcfromtimestamp(int(last)))
        else:
            raise exceptions.ValidationError(
                "last timestamp is required"
            )
        resp_dict = dict()
        result = list()
        qs = Conversation.objects.filter(seen=False, receiver_id=self.request.user.id,
                                         created__gte=last)
        if qs:
            session_ids = list(set(qs.order_by("-created").values_list('session_id', flat=True)))
            for session in session_ids:
                queryset = qs.filter(session_id=session)
                resp_dict["unseen_count"] = queryset.count()
                resp_dict["session_id"] = session
                if self.request.user.id == queryset.first().sender.id:
                    resp_dict["user_info"] = dict()
                    resp_dict["user_info"]["user_id"] = queryset.first().receiver.id
                    resp_dict["user_info"]["user_full_name"] = queryset.first().receiver.full_name
                    profile_picture = queryset.first().receiver.profile_picture
                    if profile_picture:
                        resp_dict["user_info"]["user_profile_picture"] = queryset.first().receiver.profile_picture.url
                    else:
                        resp_dict["user_info"]["user_profile_picture"] = None
                else:
                    resp_dict["user_info"] = dict()
                    resp_dict["user_info"]["user_id"] = queryset.first().sender.id
                    resp_dict["user_info"]["user_full_name"] = queryset.first().sender.full_name
                    profile_picture = queryset.first().sender.profile_picture
                    if profile_picture:
                        resp_dict["user_info"]["user_profile_picture"] = queryset.first().sender.profile_picture.url
                    else:
                        resp_dict["user_info"]["user_profile_picture"] = None

                dict_copy = resp_dict.copy()
                result.append(dict_copy)
        return response.Response(
            result,
            status=status.HTTP_200_OK
        )








