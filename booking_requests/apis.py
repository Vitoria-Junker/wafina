import pytz
from django.db.models import Q

from .models import BookingSession
from .serializers import BookingRequestSerializer, SessionDetailsSerializer, SessionActionSerializer
from rest_framework import generics, status, response, permissions, exceptions
from datetime import datetime
from accounts.models import User, UserExpertise
from helpers.tasks import SendOTPNotificationOnEmail
from helpers.notification_method import create_notification
from django.contrib.sites.shortcuts import get_current_site


class SendProposalView(generics.CreateAPIView):
    serializer_class = BookingRequestSerializer
    model = BookingSession
    permission_classes = (permissions.IsAuthenticated,)
    task = SendOTPNotificationOnEmail()

    def suffix(self, d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def custom_strftime(self, format, t):
        return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

    def create(self, request, *args, **kwargs):
        source = self.request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            target_id = serializer.validated_data.pop('target_id')
            start_time = serializer.validated_data['start_timestamp'].strftime("%Y-%m-%d %H:%M")
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M").strftime("%I:%M %p")
            custom_date = self.custom_strftime('%B {S}, %Y', serializer.validated_data['requested_date'])
            target = User.objects.get_user_by_id(user_id=target_id)
            domain_name = get_current_site(request)
            expertise_obj = UserExpertise.objects.filter(id__in=serializer.validated_data["requested_services"])
            total_price = sum([obj.cost_in_usd for obj in expertise_obj])
            expertise_name_list = list()
            requested_service_list = list()
            weekday = serializer.validated_data["requested_date"].strftime('%A')
            if target.off_day.lower() == weekday.lower():
                raise exceptions.ValidationError(
                    "Professional has an off day on given date.Please select different date"
                )
            try:
                for qs in expertise_obj:
                    try:
                        if qs.user_defined_expertise:
                            expertise_name_list.append(qs.user_defined_expertise)
                            expertise_name = qs.user_defined_expertise
                        else:
                            expertise_name_list.append(qs.expertise.expertise_name)
                            expertise_name = qs.expertise.expertise_name
                    except:
                        expertise_name_list.append("")
                        expertise_name = ""
                    requested_service_list.append(
                        {
                            "service_name": expertise_name,
                            "cost_in_usd": qs.cost_in_usd
                        }
                    )
            except:
                pass
            target_expertise_names = ",".join(expertise_name_list)
            obj = self.model.objects.create(**serializer.validated_data)
            obj.source = source
            obj.target = target
            obj.status = 'sent'
            extra_data = {'custom_date': custom_date, 'start_time': start_time,
                          "requested_services_data": requested_service_list
                          }

            obj.extra_data = extra_data
            obj.total_price = total_price
            obj.save()
            ctx = {
                "user_email": target.email,
                "session_date": custom_date,
                "start_time": start_time,
                "source_name": source.full_name,
                "target_name": target.full_name,
                "current_site": domain_name,
                "service_name": target_expertise_names,
                'subject_template_name': 'Booking Session Request',
                'html_body_template_name': 'booking_session_request.html',
                'text_template': 'booking_session_request.txt',
                'services': target_expertise_names
            }
            self.task.run(**ctx)
            notification_data = {
                "user_id": target_id,
                "notification_subject": f'New Session Request by {source.full_name}',
                "notification_message": f'On {custom_date} at {start_time}',
                "session_id": obj.id,
                "actionable": True,
                "type_of_action": "session_request"

            }
            create_notification(notification_data)
            return response.Response({'session_id': obj.id},
                                     status=status.HTTP_200_OK)
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class SessionDetailsAPI(generics.ListAPIView):
    model = BookingSession
    permission_classes = (permissions.AllowAny,)
    serializer_class = SessionDetailsSerializer

    def get_queryset(self):
        session_id = self.request.query_params.get("session_id")
        if session_id:
            return self.model.objects.filter(id=session_id)
        else:
            raise exceptions.ValidationError(
                "session_id is required in query parameters"
            )


class SessionActionAPI(generics.CreateAPIView):
    model = BookingSession
    serializer_class = SessionActionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    email_task = SendOTPNotificationOnEmail()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            import datetime
            action = serializer.validated_data["action"]
            session_obj = self.model.objects.filter(id=serializer.validated_data["session_id"]).first()
            no_of_hours = serializer.validated_data.get("no_of_hours")
            domain_name = get_current_site(request)
            source = session_obj.source
            target = session_obj.target
            if action == "accept":
                if no_of_hours is None:
                    raise exceptions.ValidationError("no_of_hours is required")
                end_time = (session_obj.start_timestamp + datetime.timedelta(hours=no_of_hours)).strftime("%Y-%m-%d "
                                                                                                          "%H:%M")
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M").strftime("%I:%M %p")
                session_obj.extra_data.update({"end_time": end_time})
                session_obj.end_timestamp = session_obj.start_timestamp + datetime.timedelta(hours=no_of_hours)
                session_obj.save()
                ctx = {
                    "user_email": source.email,
                    "source_name": source.full_name,
                    "target_name": target.full_name,
                    "custom_date": session_obj.extra_data.get("custom_date"),
                    "start_time": session_obj.extra_data.get("start_time"),
                    "end_time": session_obj.extra_data.get("end_time"),
                    "price": session_obj.total_price,
                    "current_site": domain_name,
                    "subject_template_name": 'Booking Session Request Accepted',
                    "html_body_template_name": 'session_accept.html',
                    "text_template": 'session_accept.txt',
                }
                self.email_task.run(**ctx)
                notification_data = {
                    "user_id": source.id,
                    "notification_subject": f'Booking Session Request Accepted',
                    "notification_message": f'Congrats {target.full_name} has accepted your session request. '
                                            f'Amount to be paid for this session is ${session_obj.total_price}',
                    "session_id": session_obj.id,
                    "actionable": True,
                    "type_of_action": "payment"
                }
                create_notification(notification_data)
                session_obj.status = 'accepted'
                session_obj.save()
                return response.Response(status=status.HTTP_204_NO_CONTENT)
            else:
                if action == "reject":
                    ctx = {
                        "user_email": source.email,
                        "source_name": source.full_name,
                        "target_name": target.full_name,
                        "current_site": domain_name,
                        "subject_template_name": 'Booking Session Request Rejected',
                        "html_body_template_name": 'session_reject.html',
                        "text_template": 'session_reject.txt',
                    }
                    self.email_task.run(**ctx)
                    notification_data = {
                        "user_id": source.id,
                        "notification_subject": f'Booking Session rejected',
                        "notification_message": f'Sorry {target.full_name} cannot fulfil your session request '
                                                f'at this '
                                                f' time',
                        "session_id": session_obj.id
                    }
                    create_notification(notification_data)
                    session_obj.status = 'rejected'
                    session_obj.save()
                    return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class CalenderDataView(generics.ListAPIView):
    model = BookingSession
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        start_timestamp = self.request.query_params.get('start_time', None)
        end_timestamp = self.request.query_params.get('end_time', None)
        user_id = self.request.user.id
        import datetime  # Do not change this line

        if start_timestamp and end_timestamp:
            if isinstance(start_timestamp, str):
                start_timestamp = datetime.datetime.strptime(
                    start_timestamp, "%Y-%m-%d"
                )
            if isinstance(end_timestamp, str):
                end_timestamp = datetime.datetime.strptime(
                    end_timestamp, "%Y-%m-%d"
                )
            start_time = datetime.time(
                hour=0, minute=0, second=0)
            end_time = datetime.time(
                hour=23, minute=59, second=59)
            end_timestamp = datetime.datetime.combine(
                end_timestamp, end_time
            ).replace(tzinfo=pytz.UTC)
            start_timestamp = datetime.datetime.combine(
                start_timestamp, start_time
            ).replace(tzinfo=pytz.UTC)
            result_qs = self.model.objects.filter(
                Q(
                    Q(start_timestamp__lte=start_timestamp) & Q(
                        end_timestamp__gte=start_timestamp)
                ) | Q(
                    Q(start_timestamp__gte=start_timestamp) & Q(
                        Q(end_timestamp__lte=end_timestamp) | Q(
                            Q(start_timestamp__lte=end_timestamp) & Q(
                                end_timestamp__gte=end_timestamp
                            )
                        )
                    )
                ),
                Q(status='accepted') | Q(status='paid') | Q(status='completed')
            )
            result_qs = result_qs.filter(Q(source_id=user_id) | Q(target_id=user_id))
            return result_qs
        else:
            raise exceptions.ValidationError('start_time, end_time are required')

    def get_serializer_class(self):
        return SessionDetailsSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        distinct_dates = list(set(queryset.values_list('requested_date', flat=True)))
        resp_dict = dict()
        if queryset:
            queryset = queryset.order_by('requested_date')
            serializer = self.get_serializer_class()
            serializer = serializer(
                queryset, context={'request': request}, many=True)
            resp_dict["dates"] = distinct_dates
            resp_dict["data"] = serializer.data
            return response.Response(
                resp_dict,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                {},
                status=status.HTTP_200_OK
            )
