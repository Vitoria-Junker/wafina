from django.contrib.auth import user_logged_in
from django.db.models import Q
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, response, status, permissions, views, viewsets, mixins, filters
from rest_framework.parsers import MultiPartParser, FormParser
from . import serializers, models
from helpers.tasks import SendOTPNotificationOnEmail, StripeVerificationTask
from helpers import messages
from helpers.notification_method import create_notification


class RegistrationAPI(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer
    model = models.User
    permission_classes = (
        permissions.AllowAny,
    )

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data.pop('confirm_password')
            user = self.model.objects.create_user(**serializer.validated_data)
            user.save()
            user_otp = user.generate_otp(email=user.email)
            ctx = {
                'otp_code': user_otp,
                'user_email': user.email,
                'username': user.username,
                'subject_template_name': 'Verify your Wafina Account!!',
                'html_body_template_name': 'email_verification.html',
                'text_template': 'email_verification.txt'
            }

            task = SendOTPNotificationOnEmail()
            task.run(**ctx)
            response_dict = dict()
            response_dict['user_id'] = user.id
            return response.Response(response_dict, status=status.HTTP_200_OK)
        else:
            return response.Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(generics.CreateAPIView):
    serializer_class = serializers.VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_otp = serializer.user_otp
            user = user_otp.get_user()
            user.is_active = True
            user.save()
            models.UserOtp.objects.get_all_otp_of_user(user).delete()
            response_dict = dict()
            response_dict['auth_token'] = user.get_jwt_token_for_user()
            response_dict['user_id'] = user.id
            response_dict['account_type'] = user.account_type
            return response.Response(response_dict, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    """ Api for the user login """

    serializer_class = serializers.LoginSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request, *args, **kwargs):
        """
        login api
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user  # take the user from serializer objects
            user_logged_in.send(
                sender=user.__class__, request=self.request, user=user)
            response_dict = dict()
            response_dict['auth_token'] = user.get_jwt_token_for_user()
            response_dict['user_id'] = user.id
            response_dict['account_type'] = user.account_type
            response_dict['personal_info_added'] = user.personal_info_added
            response_dict['expertise_added'] = user.expertise_added
            response_dict['verification_skipped'] = user.verification_skipped
            response_dict['account_complete'] = user.account_complete
            response_dict['needs_action'] = user.needs_action
            return response.Response(
                data=response_dict,
                status=status.HTTP_200_OK,
            )


class ResendOtp(views.APIView):
    """ endpoint to resend otp to user """
    permission_classes = (permissions.AllowAny,)
    model = models.User
    serializer_class = serializers.ResendOtpSerilizer

    @swagger_auto_schema(
        request_body=serializers.ResendOtpSerilizer,
        operation_id="Resend otp")
    def post(self, request, *args, **kwargs):
        """ resend the otp to user """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):

            user = serializer.user
            user_otp = user.generate_otp(email=user.email)

            ctx = {
                'username': user.username,
                'otp_code': user_otp,
                'user_email': user.email,
                'subject_template_name': 'OTP Notification',
                'html_body_template_name': 'otp.html',
                'text_template': 'otp.txt'
            }
            task = SendOTPNotificationOnEmail()
            task.run(**ctx)

            return response.Response(
                {'msg': messages.OTP_SENT_SUCCESSFULLY},
                status=status.HTTP_200_OK)
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordAPIView(views.APIView):
    model = models.User
    serializer_class = serializers.ResendOtpSerilizer  # serializer declaration
    permission_classes = (
        permissions.AllowAny,
    )
    msg_template_name = "otp.text"
    queryset = models.User.objects.all()

    @swagger_auto_schema(
        request_body=serializers.ResendOtpSerilizer,
        operation_id="Forgot password")
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user
            user_otp = user.generate_otp(email=user.email)
            ctx = {
                'username': user.username,
                'otp_code': user_otp,
                'user_email': user.email,
                'subject_template_name': 'Reset Your Password',
                'html_body_template_name': 'otp.html',
                'text_template': 'otp.txt'
            }

            task = SendOTPNotificationOnEmail()
            task.run(**ctx)
            res = {
                'user': user.id,
                "email": user.email
            }
            return response.Response(res, status=status.HTTP_200_OK)
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class OtpVerifyPasswordResetAPIView(views.APIView):
    """ end point to reset password with otp after forgot password """
    permission_classes = (permissions.AllowAny,)
    serializers_class = serializers.PasswordResetSerializer
    model = models.User

    @swagger_auto_schema(
        request_body=serializers.PasswordResetSerializer,
        operation_id="Reset Password")
    def post(self, request, *args, **kwargs):
        user_id = request.data["id"]
        try:
            user = self.model.objects.get_user_by_id(user_id)
        except self.model.DoesNotExist:
            raise Http404
        serializer = self.serializers_class(data=request.data, context={
            'request': request, 'user': user})

        if serializer.is_valid(raise_exception=True):
            user.is_active = True
            user.set_password(request.data["new_password"])
            user.save()
            serializer.user_otp.delete()
            return response.Response(
                data={'summary': "password reset successfully"},
                status=status.HTTP_200_OK
            )


class UserPersonalInfoAPI(generics.ListAPIView,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.ViewSet):
    model = models.User
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser,)

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.UserProfileSerializer
        elif self.request.method == 'GET':
            return serializers.UserInformationGetSerializer
        else:
            return serializers.UserUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_id = serializer.validated_data.pop("user_id")
            user_obj = self.model.objects.filter(id=user_id)
            user = user_obj.first()
            if "profile_picture" in serializer.validated_data:
                profile_picture = serializer.validated_data.pop("profile_picture")
                user.profile_picture = profile_picture
            if user.account_type == "customer":
                user.account_complete = True
            user.personal_info_added = True
            user.save()
            user_obj.update(**serializer.validated_data)
            return response.Response(
                {'msg': 'Personal Information successfully saved'},
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer_class()
        serializer_context = {"user_id": instance.id}
        serializer = serializer(data=request.data,
                                instance=instance,
                                partial=partial,
                                context=serializer_context
                                )

        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class ExpertiseAPI(generics.ListAPIView):
    model = models.ExpertiseModel
    serializer_class = serializers.ExpertiseGetSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.model.objects.filter(is_active=True)


class SelectExpertiseAPI(generics.ListAPIView,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.ViewSet):
    model = models.UserExpertise
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.model.objects.filter(
            user_id=self.request.user.id,
            is_active=True
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.SelectExpertiseSerializer
        else:
            return serializers.UserExpertiseGetSerializer

    def create(self, request, *args, **kwargs):
        user_id = self.request.user.id
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data, context={"user_id": user_id})
        if serializer.is_valid(raise_exception=True):
            expertise_data = serializer.validated_data.pop("expertise_data")
            if expertise_data:
                for obj in expertise_data:
                    keys = list(obj.keys())
                    if "id" in keys:
                        expertise_id = obj.pop("id")
                        self.model.objects.filter(id=expertise_id).update(**obj)
                    else:
                        obj = self.model.objects.create(**obj)
                        obj.user = self.request.user
                        obj.save()
                self.request.user.expertise_added = True
                self.request.user.save()
                return response.Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                self.request.user.expertise_added = True
                self.request.user.save()
                return response.Response(
                    status=status.HTTP_204_NO_CONTENT
                )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer_class()
        serializer_context = {"user_id": instance.id}
        serializer = serializer(data=request.data,
                                instance=instance,
                                partial=partial,
                                context=serializer_context
                                )

        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserSearchAPI(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('full_name', 'city', 'user_expertise__expertise__expertise_name', 'postcode',
                     'user_expertise__user_defined_expertise')
    model = models.User
    serializer_class = serializers.UserSearchSerializer

    def get_queryset(self):
        return self.model.objects.filter(account_type='professional')


class UserStripeVerification(generics.CreateAPIView):
    model = models.UserStripeVerification
    serializer_class = serializers.StripeVerificationSerializer
    parser_classes = (FormParser, MultiPartParser,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = self.model.objects.create(**serializer.validated_data)
            obj.user = self.request.user
            obj.save()
            task = StripeVerificationTask()
            domain_name = f"{request.scheme}://{request.META['HTTP_HOST']}"
            task.delay(obj.id, domain_name)
            return response.Response(
                {'msg': 'Thank You for uploading the documents.'
                        'We will get back to you shortly'},
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class SkipVerification(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        try:
            notification_data = {
                "user_id": user.id,
                "notification_subject": f'Verify your Account',
                "notification_message": f"In order to withdraw the money from wallet to your bank account, "
                                        f"verify your account.",
                "actionable": True,
                "type_of_action": "Profile Verification"
            }
            user.verification_skipped = True
            user.save()
            create_notification(notification_data)
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return response.Response({'error': e.args[0]},
                                     status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(views.APIView):
    """ change user password for authenticated user """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ChangePasswordSerializer

    @swagger_auto_schema(
        request_body=serializers.ChangePasswordSerializer,
        operation_id="Change password")
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            request.user.set_password(
                serializer.validated_data["new_password"])
            request.user.save()
            return response.Response(
                {"msg": "Password successfully changed"},
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserDataAPI(generics.ListAPIView):
    model = models.User
    serializer_class = serializers.UserDataSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return self.model.objects.filter(id=user_id)
        else:
            return self.model.objects.all()


class UpdateRoleAPI(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        obj = models.User.objects.filter(Q(account_type="company") | Q(account_type="freelancer")).update(
            account_type="professional"
        )
        return response.Response(
            {"msg":"Role successfully updated"}
        )


