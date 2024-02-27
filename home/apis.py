from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, response, permissions, status

from helpers.tasks import SendOTPNotificationOnEmail
from .models import Faq, ContactUs
from .serializers import FaqSerializer, ContactUsSerializer


class FaqAPI(generics.ListAPIView):
    serializer_class = FaqSerializer
    permission_classes = (permissions.AllowAny,)
    model = Faq

    def get_queryset(self):
        return self.model.objects.filter(is_active=True)


class ContactUsAPI(generics.CreateAPIView):
    model = ContactUs
    serializer_class = ContactUsSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            task = SendOTPNotificationOnEmail()
            ctx = dict()
            ctx["full_name"] = obj.full_name
            ctx["email"] = obj.email
            ctx["phone_number"] = obj.phone_number
            ctx["message"] = obj.message
            ctx['subject_template_name'] = 'New Contact-Us Request by User'
            ctx['html_body_template_name'] = 'contact-us.html'
            ctx['text_template'] = 'contact-us.txt',
            ctx["current_site"] = get_current_site(request)
            ctx["user_email"] = "contactus@wafina.co.uk"
            task.run(**ctx)
            return response.Response(
                {"msg": "Your request has been successfully submitted"},
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )